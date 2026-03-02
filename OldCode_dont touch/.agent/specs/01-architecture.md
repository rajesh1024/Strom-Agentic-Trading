
# STROM — Architecture (M0–M2)

## 1. Components

### Control Plane
- API Service (FastAPI): Agent CRUD, start/stop, stats, read-only strategy catalog, health/metrics.
- Auth:
  - M0–M2: Dev Auth mode allowed (documented in Security spec)
  - Production target: Keycloak OIDC (future hardening)
- Telegram Service (M2): Calls API endpoints; does not access internal services directly.

### Data Plane
- NATS JetStream: event bus for ticks, runs, signals, order intents, fills, PnL updates.
- Scheduler Service: emits AgentTick events at configured frequency for enabled agents.
- Market Data Simulator (M1): publishes deterministic synthetic ticks for instruments in agent universes.
- Runtime Worker: consumes AgentTick, reads latest market state, runs strategy engine, produces Signal and OrderIntent (paper mode).
- Risk Engine (M2): deterministic gating for order intents.
- Paper Execution Service (M2): simulates fills, writes trades/positions/pnl, publishes fill events.

### Storage
- Postgres: system-of-record for agents, runs, orders, trades, positions, pnl snapshots, strategy metadata.
- Valkey: caching and rate-limit counters (optional in M0–M2; allowed but not required).

## 2. Data Flow (M2)
1) Scheduler emits `strom.agent.tick`
2) Runtime consumes tick, reads agent config + latest market price(s)
3) Strategy engine computes decision → emits `strom.signal.created`
4) Risk engine validates → emits `strom.order.intent`
5) Paper execution simulates fill → emits `strom.order.filled`
6) Ledger updated → emits `strom.pnl.updated`
7) API/Web read from Postgres; optionally subscribe to SSE/WS stream derived from events.

## 3. State Machines

### Agent State
- CREATED → CONFIGURED → RUNNING → PAUSED → STOPPED → ERROR
Notes:
- In M0–M2, UI uses ENABLED boolean + last_status; full PAUSED is optional.

### Order State (paper)
- INTENT → FILLED | REJECTED

### Backtest State (stub for M0–M2)
- REQUESTED → RUNNING → COMPLETED | FAILED (implemented M3+)

## 4. Non-functional Requirements (M0–M2)
- Determinism in tests: market simulator and strategy engine must support a fixed random seed.
- Idempotency: order intents must have idempotency keys; paper execution must not double-fill.
- Observability: each service emits health and minimal metrics.
