# Medallion Architecture — Postgres + ClickHouse

A skeleton for a bronze → silver → gold data platform.

| Layer  | Store      | Table                  | Purpose                                               |
|--------|------------|------------------------|-------------------------------------------------------|
| Bronze | Postgres   | `bronze.raw_orders`    | Raw JSONB payloads exactly as received, append-only   |
| Silver | ClickHouse | `silver.orders`        | Cleaned, typed, deduplicated (`ReplacingMergeTree`)   |
| Gold   | ClickHouse | `gold.daily_revenue`   | Business aggregates rebuilt from silver               |
| Meta   | Postgres   | `meta.pipeline_runs`   | Pipeline run history                                  |

```
 API / sources ──► Postgres bronze ──(bronze_to_silver)──► ClickHouse silver ──(silver_to_gold)──► ClickHouse gold
                         ▲                                                                              │
                         └──────── bad records flagged with `error`         FastAPI ◄── React console ◄─┘
```

## Layout

```
infra/postgres/       bronze + meta schema (runs on first container start)
infra/clickhouse/     silver + gold schema (runs on first container start)
backend/app/
  core/config.py      settings from env / .env
  db/                 Postgres pool, ClickHouse client
  pipelines/          transforms (pure), bronze_to_silver, silver_to_gold, run tracking
  api/routes/         health, bronze ingest, layer summary + gold, pipelines
frontend/src/         React console: layer counts, seed data, trigger pipelines, view gold
```

## Run

Everything in Docker:

```bash
make up            # frontend http://localhost:5173, API docs http://localhost:8000/docs
```

Or databases in Docker, apps locally (hot reload):

```bash
make db
make backend       # in one terminal
make frontend      # in another
```

Then in the UI: **Seed 50 raw orders → Run bronze → silver → Run silver → gold**.
A few seeded records have an invalid status on purpose, so you can see them flagged in bronze.

## API

| Method | Path                              |                                  |
|--------|-----------------------------------|----------------------------------|
| GET    | `/api/health`                     | Postgres + ClickHouse status     |
| POST   | `/api/bronze/orders`              | Land raw records                 |
| GET    | `/api/layers/summary`             | Row counts per layer             |
| GET    | `/api/pipelines`                  | Available pipelines              |
| POST   | `/api/pipelines/{name}/run`       | Run a pipeline synchronously     |
| GET    | `/api/pipelines/runs`             | Recent run history               |
| GET    | `/api/gold/daily-revenue`         | Gold aggregate                   |

## Adding a new dataset

1. Bronze table in `infra/postgres/`, silver/gold tables in `infra/clickhouse/`.
2. A pure cleaning function in `pipelines/transforms.py` (+ tests).
3. A pipeline module and an entry in `pipelines/registry.py`.

Init scripts only run on an empty volume — `docker compose down -v` to re-apply schema changes
(a migration tool is a sensible next step).

## Tests

```bash
make test lint
```
