
# STROM Milestone Plan (M0–M2) — Task DAG

This plan is the minimum to produce a workable system with simulated data and paper trading.

## M0 — Foundations
### STROM-T0.1 Repo skeleton + tooling
- Owner: DevOps
- Dependencies: none
- Outputs: Makefile, lint configs, docker compose baseline
- DoD: `make lint` and `make format` and `make test` placeholders wired

### STROM-T0.2 Core infrastructure in docker-compose
- Owner: DevOps
- Dependencies: T0.1
- Outputs: docker-compose with postgres, nats, valkey
- DoD: `docker compose up` and health checks reachable

### STROM-T0.3 Auth + secrets baseline wiring
- Owner: Security/IAM + Backend
- Dependencies: T0.2
- Outputs: Keycloak container + realm import stub; OpenBao container + policy stub
- DoD: API validates JWT locally OR a stub auth mode documented (MVP), but must be explicit in specs

### STROM-T0.4 Observability skeleton
- Owner: DevOps
- Dependencies: T0.2
- Outputs: minimal metrics/logging plumbing
- DoD: at least one service emits structured logs + metrics endpoint

**M0 Gate:** G1 Build + partial G0 Spec existence

---

## M1 — Agent Lifecycle (Simulated Market, No Trading)
### STROM-T1.1 Specs baseline (architecture, DB, APIs, events)
- Owner: Spec Editor
- Dependencies: T0.1
- Outputs: specs/01-architecture.md, 02-data-model.md, 03-apis.md, 04-events.md, 05-security.md
- DoD: Consistent references + minimal state machines defined

### STROM-T1.2 Backend: Agent CRUD + Start/Stop endpoints
- Owner: Backend
- Dependencies: T1.1, T0.2
- Outputs: apps/api endpoints + DB migrations
- DoD: unit tests + OpenAPI matches specs

### STROM-T1.3 Integration: Scheduler emits AgentTick (NATS)
- Owner: Integration
- Dependencies: T1.1, T0.2
- Outputs: scheduler service + NATS subjects from specs
- DoD: emits ticks for enabled agents; test proves emission

### STROM-T1.4 Integration: Runtime worker consumes AgentTick and emits AgentRun events
- Owner: Integration
- Dependencies: T1.3
- Outputs: runtime worker service + DB writes for run records
- DoD: run records visible in DB + event emission test

### STROM-T1.5 Market data simulator
- Owner: Integration
- Dependencies: T1.1
- Outputs: marketdata simulator service emitting prices
- DoD: runtime can read latest prices deterministically

### STROM-T1.6 Frontend: Agent wizard + Agent dashboard skeleton
- Owner: Frontend
- Dependencies: T1.2
- Outputs: web UI flows, start/stop controls, run history
- DoD: UI works against real API; shows countdown (based on agent frequency)

### STROM-T1.7 QA: E2E test for M1
- Owner: QA
- Dependencies: T1.6
- Outputs: e2e test that creates agent → starts → sees run record
- DoD: runs in CI or locally via docker-compose

**M1 Gate:** G0, G1, G2, G4(demo-m1)

---

## M2 — Paper Trading MVP
### STROM-T2.1 DB schema: orders/trades/positions/PnL
- Owner: Backend + Spec Editor
- Dependencies: T1.1
- Outputs: migrations + spec updates
- DoD: schema documented + tested

### STROM-T2.2 Strategy engine v0 (predefined only)
- Owner: Data-Backtest
- Dependencies: T1.4, T1.5
- Outputs: simple strategy interface + 1-2 predefined strategies
- DoD: deterministic signals given fixed data

### STROM-T2.3 Risk engine v0
- Owner: Integration
- Dependencies: T2.1, T2.2
- Outputs: risk checks + exposure caps
- DoD: blocks trades when rules violated (tests)

### STROM-T2.4 Paper execution (fill simulator)
- Owner: Integration + Data-Backtest
- Dependencies: T2.3
- Outputs: execution service that converts OrderIntent → fills
- DoD: generates trades + updates positions + PnL

### STROM-T2.5 Dashboard: trades + PnL + running agents list
- Owner: Frontend
- Dependencies: T2.4
- Outputs: UI tables + PnL charts + live updates
- DoD: shows trades and PnL for a running agent

### STROM-T2.6 Telegram: stats + start/stop + PnL query
- Owner: Integration
- Dependencies: T2.5
- Outputs: telegram service calling API endpoints
- DoD: commands work and are authorized

### STROM-T2.7 QA: E2E test for M2
- Owner: QA
- Dependencies: T2.6
- Outputs: create agent → run → trade occurs → PnL visible
- DoD: deterministic seed makes test stable

**M2 Gate:** G0, G1, G2, G3, G4(demo-m2)
