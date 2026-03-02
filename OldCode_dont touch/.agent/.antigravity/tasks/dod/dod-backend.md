
# Backend DoD

- OpenAPI matches specs/03-apis.md
- DB migrations exist and are reversible
- Unit tests cover:
  - agent CRUD
  - start/stop
  - auth checks (or explicit stub mode)
- Emits NATS events exactly as per specs/04-events.md
- Health endpoint + metrics endpoint
