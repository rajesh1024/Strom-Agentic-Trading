
# STROM Orchestration Workflow (SPEV)

## Roles
- Conductor: orchestrates plan, enforces gates, assigns tasks
- Spec Editor: owns specs; resolves SPEC GAP; merges interface changes
- Builders: Frontend / Backend / Integration / DevOps / Data-Backtest
- Verifiers: QA + Security/IAM

## Required Specs (must exist before Milestone M1 coding starts)
- specs/01-architecture.md
- specs/02-data-model.md
- specs/03-apis.md
- specs/04-events.md
- specs/05-security.md
- specs/06-backtesting.md (can be stubbed for M0–M1 but must declare parity rule)

If any are missing: create SPEC GAP and block.

---

## Milestones (Build Order)
- M0: Foundations (repo + infra + auth + observability skeleton)
- M1: Agent lifecycle with simulated market (no real trading)
- M2: Paper trading MVP (signal → risk → paper fills → PnL)

Milestones M3+ are out of scope for this starter pack.

---

## Gates (Hard Stops)

### Gate G0 — Spec Gate
Pass criteria:
- Specs exist and reference each other coherently.
- APIs/events/DB sections are consistent (no conflicts).
- State machines are defined (Agent + Order + Backtest at least stubbed).

### Gate G1 — Build Gate
Pass criteria:
- `docker compose up` starts core stack without errors.
- Health checks return OK for API + Web.
- NATS and Postgres reachable from services.

### Gate G2 — Test Gate
Pass criteria:
- Backend unit tests pass (pytest)
- Event schema validation tests pass
- One end-to-end demo test passes for M1/M2

### Gate G3 — Observability Gate
Pass criteria:
- Minimal metrics endpoint available (or exported to Prometheus)
- Logs are structured JSON and include correlation IDs
- One trace/span visible in local tooling (or log-based tracing if simplified)

### Gate G4 — Demo Gate
Pass criteria:
- Each milestone includes a deterministic demo script:
  - `make demo-m0`
  - `make demo-m1`
  - `make demo-m2`

---

## Execution Procedure (Strict)
1) Conductor generates or confirms the milestone plan (task DAG) and assigns owners.
2) For each task:
   - Verify dependencies complete
   - Verify Inputs exist
   - Builder executes only the described Outputs
   - Builder updates docs/tests per DoD
3) QA verifies task DoD and signs off.
4) Spec Editor merges only if interfaces match specs.
5) After all milestone tasks complete, run demo script and record the result.

---

## “SPEC GAP” Workflow
When any agent hits ambiguity:
- Create a SPEC GAP ticket using `.antigravity/tasks/spec-gap.md`
- Assign to Spec Editor
- Block dependent tasks until closed
- Spec Editor updates specs and links resolution back to the ticket

---

## Merge / Close Criteria
- No task may be marked done without:
  - QA sign-off (and Security sign-off when keys/auth/sandbox touched)
  - Passing gates relevant to the milestone
