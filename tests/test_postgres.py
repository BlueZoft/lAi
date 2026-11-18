from collections.abc import Iterator
from concurrent.futures import ThreadPoolExecutor
from datetime import date
from pathlib import Path
from uuid import uuid4

import psycopg
import pytest
from conftest import RetrievalContext
from psycopg import sql

from lai.retrieval.engine import index_document
from lai.retrieval.models import Embedding, EncodedSection
from lai.retrieval.postgres import Connection, PostgresIndex, connect_local, migrate

pytestmark = pytest.mark.local
PASSWORD_FILE = Path(__file__).resolve().parents[1] / ".local/postgres.password"
AS_OF = date(2026, 11, 18)


@pytest.fixture(scope="module")
def local_db() -> Iterator[Connection]:
    name = "lai_t3_test_" + uuid4().hex
    with connect_local(PASSWORD_FILE) as admin:
        admin.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(name)))
        connection = connect_local(PASSWORD_FILE, database=name)
        try:
            migrate(connection)
            yield connection
        finally:
            connection.close()
            admin.execute(sql.SQL("DROP DATABASE {} WITH (FORCE)").format(sql.Identifier(name)))


@pytest.fixture
def pg_index(local_db: Connection, retrieval_context: RetrievalContext) -> Iterator[PostgresIndex]:
    index = PostgresIndex(local_db, "synthetic-" + uuid4().hex, retrieval_context.backend.identity)
    index_document(
        retrieval_context.catalog,
        index,
        retrieval_context.backend,
        retrieval_context.record.record_id,
        AS_OF,
    )
    try:
        yield index
    finally:
        local_db.execute(
            "DELETE FROM lai_retrieval.collections WHERE name = %s", (index.collection,)
        )


def test_pgvector_hybrid_matches_memory_and_retries(
    local_db: Connection,
    pg_index: PostgresIndex,
    retrieval_context: RetrievalContext,
) -> None:
    context = retrieval_context
    query = context.backend.embed(["catalogue"])[0]
    memory, postgres = context.index.search(query), pg_index.search(query)
    assert [hit.chunk.id for hit in postgres.dense] == [hit.chunk.id for hit in memory.dense]
    assert [hit.chunk.id for hit in postgres.sparse] == [hit.chunk.id for hit in memory.sparse]
    assert [hit.dense_similarity for hit in postgres.dense] == pytest.approx(
        [hit.dense_similarity for hit in memory.dense], abs=1e-6
    )
    zero_sparse = Embedding(dense=query.dense, sparse={key: 0.0 for key in query.sparse})
    assert not context.index.search(zero_sparse).sparse
    assert not pg_index.search(zero_sparse).sparse
    for _ in range(2):
        index_document(context.catalog, pg_index, context.backend, context.record.record_id, AS_OF)
    count = local_db.execute(
        "SELECT count(*) FROM lai_retrieval.sections WHERE collection = %s", (pg_index.collection,)
    ).fetchone()
    assert count == (3,)


def test_migrations_are_idempotent_and_checksum_checked(local_db: Connection) -> None:
    migrate(local_db)
    row = local_db.execute(
        "SELECT sha256 FROM lai_retrieval.schema_migrations WHERE version=1"
    ).fetchone()
    assert row is not None
    local_db.execute(
        "UPDATE lai_retrieval.schema_migrations SET sha256=%s WHERE version=1", ("0" * 64,)
    )
    try:
        with pytest.raises(ValueError, match="migration_checksum_conflict"):
            migrate(local_db)
    finally:
        local_db.execute(
            "UPDATE lai_retrieval.schema_migrations SET sha256=%s WHERE version=1", (row[0],)
        )


def test_mid_update_database_failure_rolls_back_deletion(
    local_db: Connection,
    pg_index: PostgresIndex,
    retrieval_context: RetrievalContext,
) -> None:
    local_db.execute("""CREATE FUNCTION lai_retrieval.synthetic_failure() RETURNS trigger AS $$
        BEGIN IF NEW.payload->>'section_number' = '2' THEN
            RAISE EXCEPTION 'synthetic insertion failure';
        END IF; RETURN NEW; END; $$ LANGUAGE plpgsql""")
    local_db.execute("""CREATE TRIGGER synthetic_failure BEFORE INSERT ON lai_retrieval.sections
        FOR EACH ROW EXECUTE FUNCTION lai_retrieval.synthetic_failure()""")
    context = retrieval_context
    try:
        with pytest.raises(psycopg.errors.RaiseException):
            index_document(
                context.catalog, pg_index, context.backend, context.record.record_id, AS_OF
            )
    finally:
        local_db.execute("DROP TRIGGER synthetic_failure ON lai_retrieval.sections")
        local_db.execute("DROP FUNCTION lai_retrieval.synthetic_failure()")
    assert len(pg_index.search(context.backend.embed(["catalogue"])[0]).dense) == 3


def test_concurrent_updates_use_distinct_connections_and_keep_one_version(
    local_db: Connection,
    pg_index: PostgresIndex,
    retrieval_context: RetrievalContext,
) -> None:
    context = retrieval_context

    def write(_: int) -> int:
        with connect_local(PASSWORD_FILE, database=local_db.info.dbname) as connection:
            index = PostgresIndex(connection, pg_index.collection, context.backend.identity)
            return index_document(
                context.catalog, index, context.backend, context.record.record_id, AS_OF
            )

    with ThreadPoolExecutor(max_workers=3) as pool:
        assert list(pool.map(write, range(6))) == [3] * 6
    assert len(pg_index.search(context.backend.embed(["catalogue"])[0]).dense) == 3


def test_invalid_dimensions_fail_before_sql_write(
    pg_index: PostgresIndex, retrieval_context: RetrievalContext
) -> None:
    from lai.retrieval.catalog import record_chunks
    from lai.retrieval.embeddings import FakeEmbedding

    context = retrieval_context
    vector = FakeEmbedding(dimensions=8).embed(["synthetic"])[0]
    section = EncodedSection(chunk=record_chunks(context.record)[0], vector=vector)
    with pytest.raises(ValueError, match="embedding_dimension_mismatch"):
        pg_index.replace_document(context.record, [section])
    assert len(pg_index.search(context.backend.embed(["catalogue"])[0]).dense) == 3
