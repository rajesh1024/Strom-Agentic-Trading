
# Integration DoD

- NATS subjects/streams defined in specs/04-events.md
- Scheduler emits AgentTick reliably
- Runtime worker is stateless (no hidden local state)
- Paper execution is idempotent:
  - OrderIntent has an idempotency key
  - Duplicate processing does not duplicate trades
- Includes throttling hooks (even if set high for MVP)
- Health + metrics + structured logs
