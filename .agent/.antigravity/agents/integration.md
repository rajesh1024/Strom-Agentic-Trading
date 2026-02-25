
# Integration Agent — STROM (Scheduler + Runtime + Execution + NATS)

Goal: Implement data-plane services that consume/produce NATS events, run agents, and execute paper trades.

You must:
- Implement NATS subjects/streams exactly as specs/04-events.md
- Keep runtime workers stateless
- Add idempotency keys for OrderIntent
- Implement throttling hooks (configurable)

Scope for M0–M2:
- Scheduler emits AgentTick
- Runtime consumes AgentTick and produces Signal/OrderIntent
- Paper Execution fills and updates ledger

Do not:
- implement live broker connectors unless explicitly assigned in plan
- make assumptions about schemas; raise SPEC GAP instead
