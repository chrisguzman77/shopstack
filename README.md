# ShopStack (Microservices Monorepo)

## Standards (Global Decisions)
- API: REST + JSON
- Auth: JWT access tokens (HS256)
- DB: Postgres (one container; separate DBs: auth_db, orders_db, notifications_db)
- Queue: Redis Streams with consumer groups
- Lint/format: Ruff
- Tests: Pytest
- CI: GitHub Actions

## Services
- gateway (port 8000): reverse proxy for auth + orders
- auth (port 8001): register/login/verify + rate limiting
- orders (port 8002): create orders + idempotency + publish events
- notifications (worker): consume events and record notifications

## Local Run (placeholder)
See docs + Makefile targets once created.
