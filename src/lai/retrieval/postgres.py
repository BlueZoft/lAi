"""Transactional PostgreSQL/pgvector index. Query text is never persisted."""

import json
import tempfile
from collections.abc import Sequence
from importlib.resources import files
from pathlib import Path
from typing import Any

import psycopg
from psycopg.types.json import Jsonb

from lai.corpus.models import IngestionRecord, digest
from lai.retrieval.catalog import document_key
from lai.retrieval.index import check_sections
from lai.retrieval.models import (
    BackendIdentity,
    Embedding,
    EncodedSection,
    SearchHit,
    SearchPools,
    SectionChunk,
)

Connection = psycopg.Connection[tuple[Any, ...]]


def passfile_line(password_file: Path, database: str, port: int, host: str) -> str:
    password = password_file.read_text().strip()
    if not password or any(character in password + database for character in "\n\r"):
        raise ValueError("local_authentication_file_invalid")
    fields = (host, str(port), database, "lai", password)
    return ":".join(value.replace("\\", "\\\\").replace(":", "\\:") for value in fields) + "\n"


def connect_local(password_file: Path, database: str = "lai", port: int = 54329) -> Connection:
    socket_directory = password_file.parent / "postgres-socket"
    using_socket = (socket_directory / ".s.PGSQL.5432").is_socket()
    host = str(socket_directory.resolve()) if using_socket else "127.0.0.1"
    port = 5432 if using_socket else port
    with tempfile.NamedTemporaryFile(
        mode="w",
        prefix="lai-pgpass-",
        dir=password_file.parent,
    ) as authentication:
        authentication.write(
            passfile_line(password_file, database, port, "localhost" if using_socket else host)
        )
        authentication.flush()
        try:
            return psycopg.connect(
                host=host,
                port=port,
                dbname=database,
                user="lai",
                passfile=authentication.name,
                connect_timeout=5,
                autocommit=True,
            )
        except psycopg.Error:
            raise ValueError("local_database_unavailable") from None


def migrate(connection: Connection) -> None:
    script = files("lai.retrieval").joinpath("migrations/001_retrieval.sql").read_text()
    checksum = digest(script.encode())
    with connection.transaction():
        connection.execute("SELECT pg_advisory_xact_lock(184670301)")
        connection.execute("CREATE SCHEMA IF NOT EXISTS lai_retrieval")
        connection.execute("""CREATE TABLE IF NOT EXISTS lai_retrieval.schema_migrations (
            version integer PRIMARY KEY, sha256 text NOT NULL)""")
        applied = connection.execute(
            "SELECT sha256 FROM lai_retrieval.schema_migrations WHERE version = 1"
        ).fetchone()
        if applied is not None:
            if applied[0] != checksum:
                raise ValueError("migration_checksum_conflict")
            return
        connection.execute(script)
        connection.execute(
            "INSERT INTO lai_retrieval.schema_migrations(version, sha256) VALUES (1, %s)",
            (checksum,),
        )


def vector_literal(vector: Embedding) -> str:
    return "[" + ",".join(str(value) for value in vector.normalised().dense) + "]"


class PostgresIndex:
    def __init__(self, connection: Connection, collection: str, identity: BackendIdentity):
        if not collection or len(collection) > 100 or identity.dimensions != 1024:
            raise ValueError("collection_parameters_invalid")
        self.connection, self.collection, self.identity = connection, collection, identity
        with connection.transaction():
            connection.execute(
                """INSERT INTO lai_retrieval.collections
                   (name, backend_name, backend_kind, dimensions)
                   VALUES (%s, %s, %s, %s) ON CONFLICT DO NOTHING""",
                (collection, identity.name, identity.kind, identity.dimensions),
            )
            existing = connection.execute(
                """SELECT backend_name, backend_kind, dimensions
                   FROM lai_retrieval.collections WHERE name = %s""",
                (collection,),
            ).fetchone()
            if existing != (identity.name, identity.kind, identity.dimensions):
                raise ValueError("embedding_backend_mismatch")

    def replace_document(self, record: IngestionRecord, sections: Sequence[EncodedSection]) -> None:
        check_sections(self.identity, record, sections)
        key = document_key(record)
        payload = json.loads(record.model_dump_json())
        with self.connection.transaction():
            self.connection.execute(
                "SELECT name FROM lai_retrieval.collections WHERE name = %s FOR UPDATE",
                (self.collection,),
            )
            self.connection.execute(
                """INSERT INTO lai_retrieval.acquisitions(collection, record_id, payload)
                   VALUES (%s, %s, %s) ON CONFLICT DO NOTHING""",
                (self.collection, record.record_id, Jsonb(payload)),
            )
            stored = self.connection.execute(
                """SELECT payload FROM lai_retrieval.acquisitions
                   WHERE collection = %s AND record_id = %s""",
                (self.collection, record.record_id),
            ).fetchone()
            if (
                stored is None
                or IngestionRecord.model_validate_json(json.dumps(stored[0])) != record
            ):
                raise ValueError("stored_acquisition_conflict")
            self.connection.execute(
                "DELETE FROM lai_retrieval.sections WHERE collection = %s AND document_key = %s",
                (self.collection, key),
            )
            self.connection.execute(
                """INSERT INTO lai_retrieval.documents(collection, document_key, record_id)
                   VALUES (%s, %s, %s) ON CONFLICT (collection, document_key)
                   DO UPDATE SET record_id = EXCLUDED.record_id""",
                (self.collection, key, record.record_id),
            )
            for item in sections:
                self.connection.execute(
                    """INSERT INTO lai_retrieval.sections
                       (collection, chunk_id, document_key, record_id, payload,
                        dense, sparse_weights, sparse_keys)
                       VALUES (%s, %s, %s, %s, %s, %s::vector, %s, %s)""",
                    (
                        self.collection,
                        item.chunk.id,
                        key,
                        record.record_id,
                        Jsonb(item.chunk.model_dump(mode="json")),
                        vector_literal(item.vector),
                        Jsonb(item.vector.sparse),
                        sorted(item.vector.sparse),
                    ),
                )

    def search(self, vector: Embedding, limit: int = 15) -> SearchPools:
        if len(vector.dense) != self.identity.dimensions or not 1 <= limit <= 100:
            raise ValueError("search_parameters_invalid")
        expression = """COALESCE((SELECT sum(
            (term.value::double precision) *
            COALESCE((s.sparse_weights ->> term.key)::double precision, 0))
            FROM jsonb_each_text(%s::jsonb) AS term), 0)"""
        statement = (
            """SELECT s.payload, 1 - (s.dense <=> %s::vector) AS similarity,
            """
            + expression
            + """ AS sparse_score
            FROM lai_retrieval.sections s WHERE s.collection = %s"""
        )
        parameters = (vector_literal(vector), Jsonb(vector.sparse), self.collection)
        dense_statement = statement + " ORDER BY similarity DESC, s.chunk_id LIMIT %s"
        sparse_statement = (
            statement
            + " AND s.sparse_keys && %s::text[] AND "
            + expression
            + " > 0 ORDER BY sparse_score DESC, s.chunk_id LIMIT %s"
        )
        query = (
            "SELECT 'dense', dense.* FROM (" + dense_statement + ") dense UNION ALL "
            "SELECT 'sparse', sparse.* FROM (" + sparse_statement + ") sparse"
        )
        with self.connection.transaction():
            rows = self.connection.execute(
                query,
                parameters
                + (limit,)
                + parameters
                + (sorted(vector.sparse), Jsonb(vector.sparse), limit),
            ).fetchall()

        def hits(rows: list[tuple[Any, ...]]) -> tuple[SearchHit, ...]:
            return tuple(
                SearchHit(
                    chunk=SectionChunk.model_validate_json(json.dumps(row[0])),
                    dense_similarity=float(row[1]),
                    sparse_score=float(row[2]),
                )
                for row in rows
            )

        return SearchPools(
            dense=hits([row[1:] for row in rows if row[0] == "dense"]),
            sparse=hits([row[1:] for row in rows if row[0] == "sparse"]),
        )
