-- BRONZE: raw, append-only landing zone. Payloads are stored exactly as received.
CREATE SCHEMA IF NOT EXISTS bronze;

CREATE TABLE IF NOT EXISTS bronze.raw_orders (
    id           BIGSERIAL PRIMARY KEY,
    source       TEXT        NOT NULL,
    payload      JSONB       NOT NULL,
    ingested_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    processed_at TIMESTAMPTZ,
    error        TEXT
);

CREATE INDEX IF NOT EXISTS raw_orders_unprocessed_idx
    ON bronze.raw_orders (id) WHERE processed_at IS NULL;

-- META: pipeline bookkeeping.
CREATE SCHEMA IF NOT EXISTS meta;

CREATE TABLE IF NOT EXISTS meta.pipeline_runs (
    id             BIGSERIAL PRIMARY KEY,
    pipeline       TEXT        NOT NULL,
    status         TEXT        NOT NULL,
    rows_processed INTEGER     NOT NULL DEFAULT 0,
    rows_failed    INTEGER     NOT NULL DEFAULT 0,
    started_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
    finished_at    TIMESTAMPTZ,
    error          TEXT
);
