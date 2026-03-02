
# STROM Build Rules (Non-Negotiable)

## 0) Single Source of Truth
- The `specs/` folder is authoritative for:
  - API contracts
  - Event schemas
  - DB schema
  - state machines
- If a required spec is missing or ambiguous, create a SPEC GAP ticket. Do not guess.

## 1) No Hallucinated Interfaces
- No agent may invent:
  - endpoints
  - event subjects
  - DB fields
  - broker limits
  - model provider capabilities
- If needed, raise SPEC GAP and block the task until resolved.

## 2) SPEV Loop (Mandatory)
1) Spec: update specs first
2) Plan: create task DAG with dependencies + DoD
3) Execute: implement tasks in dependency order
4) Verify: QA/Security validate against DoD
5) Repeat

## 3) Task Contract Requirement
Every task MUST include:
- Task ID
- Goal
- Inputs (files, specs)
- Outputs (exact files/paths to create/modify)
- Dependencies (task IDs)
- Definition of Done (tests, docs, demos)
- Rollback plan (how to revert safely)

Tasks that lack any section are invalid and must not be started.

## 4) PR Discipline
- 1 feature = 1 PR
- PR size limits:
  - ≤ 15 files changed OR ≤ 800 LOC net diff (whichever comes first)
- Each PR must include:
  - updated docs (if interfaces changed)
  - tests relevant to the change
  - how-to-run notes if needed

## 5) Safety Boundaries (Trading)
- LLM must never directly place or modify orders.
- Execution decisions must be deterministic: Strategy + Risk + Execution rules.
- Live trading is gated behind:
  - kill switch
  - extra QA checklist
  - “approved for live” strategy versions

## 6) Plugin Code Security
- User strategy/indicator code must run in a sandbox:
  - CPU/memory limits
  - wall-time timeout
  - no network by default
  - read-only FS by default
- If sandbox policy is not defined in specs, raise SPEC GAP.

## 7) Observability by Default
Every service must emit:
- health endpoint
- basic metrics (requests, errors, latency or loop time)
- structured logs
- trace correlation ID (at least propagated through API → events)

## 8) Stop-the-Line Policy
If tests fail, builds fail, or specs drift:
- stop implementation
- fix specs/tests/build first
- do not “work around” failing gates
