# RULES.md — Agentic Trading Platform · Non-Negotiable Rules

> Paste this file as context into EVERY Antigravity agent task. These rules are absolute.

---

## IRON RULES (applies to ALL code, ALL agents)

### 1. LLM Never Touches Money
- All order placement, modification, and cancellation is **deterministic Python code**.
- LLM agents orchestrate workflows and generate natural-language outputs ONLY.
- No LLM output is ever used as a direct input to `place_order` without passing through `check_risk` first.

### 2. RiskEngine Has Absolute Veto
- The RiskEngine is a pure Python function. It returns APPROVE or REJECT.
- No agent, no supervisor, no API endpoint can override a REJECT.
- If RiskEngine errors out, the default is REJECT.
- Risk approval has a TTL of 60 seconds. Stale approvals are invalid.

### 3. Numerical Computation = Code Only
- Greeks, P&L, indicators (RSI, ATR, VWAP), feature vectors — all computed by Python functions.
- LLM agents receive computed results as read-only structured data.
- Never ask an LLM to "calculate" or "estimate" a number.

### 4. Stale Data = No Trade
- If `fetch_option_chain` returns `stale: true`, the system MUST NOT generate signals.
- If any feature in `compute_features` is null/NaN, the system MUST fallback to NO_SIGNAL.
- If broker API is unreachable, no orders are placed. Alert raised immediately.

### 5. Kill Switch is Sacred
- `POST /admin/killswitch` must ALWAYS work — even if other services are down.
- Kill switch actions (in order): cancel all pending orders → halt all agents → optionally flatten positions → send CRITICAL alert.
- Kill switch must complete within 2 seconds.
- After kill switch, no new orders are accepted until explicit reset.

### 6. Audit Everything
- Every state-changing action (order, risk decision, agent spawn/retire, config change) is logged to `audit_log` table.
- Logs include: timestamp, agent_id, action, inputs, outputs, correlation_id.
- Audit logs are immutable (INSERT only, no UPDATE/DELETE).
- Retention: minimum 5 years (SEBI compliance).

### 7. Credentials Never Leak
- Broker API keys, secrets, tokens: stored in env vars or secrets manager ONLY.
- Never in: database, Redis, agent memory, logs, API responses, error messages, frontend.
- Memory write tool rejects any value matching known credential patterns.

### 8. Agent Lifecycle Discipline
- Max concurrent agents: 20 (configurable via `MAX_AGENTS` env var).
- Idle timeout: 5 min → IDLE state. 15 min → RETIRED.
- Heartbeat: every 30 seconds. 2 missed heartbeats → auto-retire + alert.
- Kill switch → all agents immediately RETIRED.

---

## CODE STANDARDS

### Backend (Python / FastAPI)
- Python 3.11+
- All inputs validated with Pydantic v2 models (strict mode)
- Async-first (`async def` for all route handlers and service methods)
- Type hints on ALL functions (enforced by mypy strict)
- Linting: ruff (replaces flake8 + isort + black)
- Test framework: pytest + pytest-asyncio
- Coverage minimum: 80% on new code

### Frontend (TypeScript / Next.js)
- Next.js 14 App Router + React 18
- TypeScript strict mode (`"strict": true` in tsconfig)
- No `any` types except at API boundaries (with runtime validation)
- Styling: Tailwind CSS + shadcn/ui components
- State: Zustand (global) + React Query / TanStack Query (server)
- Linting: eslint + prettier
- Test framework: vitest + React Testing Library
- Coverage minimum: 80% on components

### Shared
- Conventional commits: `feat:`, `fix:`, `test:`, `docs:`, `chore:`
- Branch naming: `{workstream}/{task-id}-{short-description}` (e.g., `backend/B7-risk-engine`)
- PR requires: 1 approval + CI green + no conflicts

---

## RISK RULES (implemented in RiskEngine)

| Rule | Parameter | Default | Description |
|------|-----------|---------|-------------|
| max_position_size | Per instrument | 4 lots | Max lots for any single instrument |
| max_portfolio_delta | Absolute | 0.5 | Max absolute portfolio delta |
| max_daily_loss | INR | ₹20,000 | Hard stop on daily loss |
| max_drawdown | Percentage | 10% | Max drawdown from peak |
| margin_check | Percentage | 90% | Reject if margin util > 90% |
| time_of_day | Time range | 09:20–15:15 | No orders outside market hours |
| correlation_limit | Threshold | 0.8 | Max correlation between positions |
| single_concentration | Percentage | 40% | Max % of capital in one instrument |

---

## MEMORY RULES

### Allowed in Memory
- Structured feature vectors
- Trade signals and outcomes
- Regime classifications with timestamps
- Strategy metadata and performance
- Risk decisions and rationale data
- Agent lifecycle events

### FORBIDDEN in Memory (tool rejects these)
- Broker API keys, secrets, tokens, passwords
- Raw order book / tick-by-tick data
- Personally identifiable information (PII)
- Unstructured LLM conversation transcripts (unless `ENABLE_TRANSCRIPT_LOGGING=true`)
- Other users' data
- Executable code or scripts

---

## ERROR HANDLING PATTERNS

```python
# Every tool call must be wrapped
try:
    result = await tool.execute(params)
    if result.error:
        log_error(result.error)
        return fallback_action()  # NO_SIGNAL, REJECT, etc.
except TimeoutError:
    raise_alert("CRITICAL", f"Tool {tool.name} timed out")
    return fallback_action()
except Exception as e:
    audit_log(action="tool_error", error=str(e))
    raise_alert("CRITICAL", f"Unexpected error in {tool.name}")
    return fallback_action()
```

**Fallback actions by context:**
- Signal generation error → NO_SIGNAL
- Risk check error → REJECT (always conservative)
- Order placement error → do NOT retry automatically, alert operator
- Data fetch error → mark data as stale, stop signal generation
- Agent error → retire agent, alert supervisor

---

## INFRASTRUCTURE RULES

1. **Container-First**: All services MUST have a Dockerfile and be part of `docker-compose.dev.yml`.
2. **Health Checks**: Every service container MUST implement a health check (curl, wget, or pg_isready).
3. **Hot Reload**: Development containers MUST support hot reload (volumes for source code).
4. **No Sidecars for Auth**: Auth must be handled at the application layer or gateway, never as a required sidecar for local dev.
5. **Port discipline**: Follow port assignments in `WORKFLOW.md`.

---

## TESTING REQUIREMENTS

Every task's code MUST include:
1. **Unit tests** — cover happy path + at least 2 edge cases
2. **Error handling tests** — verify graceful failure
3. **No hardcoded test data** — use fixtures from `data/fixtures/`
4. **Fixture Validation** — all fixtures must pass `python tests/validate_fixtures.py`
5. **Risk-specific tests** — if touching risk/execution: test that bypass is impossible
6. **Idempotency** — if operation can be retried, test that double-execution is safe

---

## CI / CD RULES

1. **Linting First**: The CI pipeline fails fast on lint errors. Code MUST pass `ruff` and `eslint`. No exceptions.
2. **Type Security**: MyPy and TSC are mandatory to guarantee type safety.
3. **Time Bound**: The entire CI pipeline must execute in under 5 minutes utilizing parallel concurrent execution.
4. **Test Boundaries**: Missing tests (≤80% coverage) or failing unit tests will block merge.

---

## FRONTEND SPECIFIC RULES

### State Management Guidelines
- **Store Usage**: Group stores logically (e.g., `portfolioStore`, `configStore`, `agentStore`, `signalStore`).
- **Persistence**: Persist user settings to local storage via zustand persist middleware.
- **Data Fetching**: Use `@tanstack/react-query` to cache standard network requests, configured globally via `QueryProvider` in `layout.tsx`.
- **WebSocket**: Use `useWebSocket` hook to handle incoming events, invalidating queries dynamically and directly mutating Zustand stores when speed is preferred.
- **Optimistic Updates**: Wrap critical actions (like `submitOrder`) using query mutations with `onMutate` to present instant UI feedback, and fallback/revert on failure.

### Shared Components Registry
- **DataTable**: Built on `@tanstack/react-table`. Supports sorting, filtering, and pagination.
- **MetricCard**: Displays value with trend (up/down) and indicator colors.
- **AssetClassBadge**: Colored pill labels (Equity=Green, Crypto=Purple).
- **StatusBadge**: Pulse-dot status indicators (Success, Warning, Error).
- **LoadingSpinner**: Standardized Loader2 with accessibility labels.
- **ConfirmDialog**: Reusable AlertDialog for destructive or critical actions.
- **ErrorBoundary**: Graceful failure UI for component crashes.
