-- WP4: immutable raw layer + provenance columns required by the ingestion contract.
BEGIN;

CREATE TABLE IF NOT EXISTS raw_documents (
    raw_document_id  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_id        TEXT NOT NULL REFERENCES source_registry(source_id),
    fetched_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
    request_url      TEXT NOT NULL,
    request_params   JSONB,
    http_status      INTEGER,
    content_type     TEXT,
    payload          JSONB NOT NULL,
    payload_sha256   CHAR(64) NOT NULL,
    UNIQUE (source_id, payload_sha256)
);

CREATE INDEX IF NOT EXISTS idx_raw_documents_source_fetched
    ON raw_documents (source_id, fetched_at DESC);

ALTER TABLE events
    ADD COLUMN IF NOT EXISTS reported_cause TEXT;

ALTER TABLE event_sources
    ADD COLUMN IF NOT EXISTS external_event_id TEXT;

CREATE UNIQUE INDEX IF NOT EXISTS uq_event_sources_external
    ON event_sources (source_id, external_event_id)
    WHERE external_event_id IS NOT NULL;

COMMIT;
