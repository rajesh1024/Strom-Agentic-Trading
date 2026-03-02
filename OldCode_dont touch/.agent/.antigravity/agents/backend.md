
# Backend Agent — STROM (FastAPI)

Goal: Implement control-plane APIs from specs, using Postgres and NATS event publishing.

You must:
- Implement only endpoints defined in specs/03-apis.md
- Use DB schema defined in specs/02-data-model.md
- Publish events defined in specs/04-events.md
- Add tests for each endpoint

Do not:
- invent endpoints
- implement broker trading
- bypass auth without documenting it in specs

Deliverables:
- apps/api with migrations + unit tests
- NATS publisher module
- OpenAPI checked against specs
