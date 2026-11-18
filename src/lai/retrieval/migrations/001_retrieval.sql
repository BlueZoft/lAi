CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE lai_retrieval.collections (
    name text PRIMARY KEY,
    backend_name text NOT NULL,
    backend_kind text NOT NULL CHECK (backend_kind IN ('fake', 'bge_m3')),
    dimensions integer NOT NULL CHECK (dimensions = 1024)
);

CREATE TABLE lai_retrieval.acquisitions (
    collection text NOT NULL REFERENCES lai_retrieval.collections(name) ON DELETE CASCADE,
    record_id text NOT NULL CHECK (record_id ~ '^[a-f0-9]{64}$'),
    payload jsonb NOT NULL,
    PRIMARY KEY (collection, record_id)
);

CREATE TABLE lai_retrieval.documents (
    collection text NOT NULL,
    document_key text NOT NULL CHECK (document_key ~ '^[a-f0-9]{64}$'),
    record_id text NOT NULL,
    PRIMARY KEY (collection, document_key),
    FOREIGN KEY (collection, record_id)
        REFERENCES lai_retrieval.acquisitions(collection, record_id) ON DELETE CASCADE
);

CREATE TABLE lai_retrieval.sections (
    collection text NOT NULL,
    chunk_id text NOT NULL CHECK (chunk_id ~ '^[a-f0-9]{64}$'),
    document_key text NOT NULL,
    record_id text NOT NULL,
    payload jsonb NOT NULL,
    dense vector(1024) NOT NULL,
    sparse_weights jsonb NOT NULL CHECK (jsonb_typeof(sparse_weights) = 'object'),
    sparse_keys text[] NOT NULL,
    PRIMARY KEY (collection, chunk_id),
    FOREIGN KEY (collection, document_key)
        REFERENCES lai_retrieval.documents(collection, document_key) ON DELETE CASCADE,
    FOREIGN KEY (collection, record_id)
        REFERENCES lai_retrieval.acquisitions(collection, record_id) ON DELETE CASCADE
);

CREATE INDEX sections_document ON lai_retrieval.sections(collection, document_key);
CREATE INDEX sections_sparse_keys ON lai_retrieval.sections USING gin(sparse_keys);
