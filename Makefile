.PHONY: up down db backend frontend test lint

up:            ## Run the full stack in Docker
	docker compose up --build

down:
	docker compose down

db:            ## Run only Postgres + ClickHouse (for local dev)
	docker compose up -d postgres clickhouse

backend:
	cd backend && uv run uvicorn app.main:app --reload

frontend:
	cd frontend && npm run dev

test:
	cd backend && uv run pytest -q

lint:
	cd backend && uv run ruff check .
