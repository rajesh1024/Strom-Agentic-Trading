# WORKFLOW.md — Agentic Trading Platform · Development Workflow & Conventions

> Paste this as context for tasks that involve multi-file changes, cross-service work, or CI/CD.

---

## Git Workflow

### Branch Strategy
```
main (protected)
  └── backend/B1-project-scaffold
  └── backend/B7-risk-engine
  └── frontend/F1-layout-shell
  └── devops/D1-docker-setup
  └── qa/Q2-risk-fuzz-test
```

### Commit Convention
```
feat: add risk engine with 8 validation rules
fix: correct margin calculation for spread orders
test: add fuzz tests for risk engine boundary conditions
docs: update API reference for /orders endpoint
chore: upgrade fastapi to 0.111.0
```

### PR Process
1. Create branch from `main`
2. Implement task (code + tests + docs)
3. Self-review: lint, type-check, test locally
4. Push and create PR with description template
5. CI runs automatically (lint → type → test → build → security)
6. 1 approval required
7. Squash merge to main

### PR Description Template
```markdown
## Task: [Task ID] - [Title]
## Workstream: Backend / Frontend / QA / DevOps / Docs

### What changed
- [bullet list of changes]

### How to test
- [manual test steps if applicable]

### Checklist
- [ ] Unit tests added (≥80% coverage on new code)
- [ ] No lint/type errors
- [ ] Documentation updated (if API/schema changed)
- [ ] No credentials in code
- [ ] Error handling follows RULES.md patterns
```

---

## Project Structure Quick Reference

```
agentic-trading-platform/
├── packages/
│   ├── dashboard/          # Next.js frontend
│   │   └── src/
│   │       ├── app/        # Pages (markets, trade, analytics, alerts, admin)
│   │       ├── components/ # UI components
│   │       ├── hooks/      # Custom hooks (useWebSocket, useMarketData)
│   │       ├── lib/        # API client, WS client, stores
│   │       └── types/      # TypeScript interfaces
│   │
│   ├── api/                # FastAPI backend
│   │   └── src/
│   │       ├── routers/    # API route handlers
│   │       ├── services/   # Business logic (signal engine, risk engine, etc.)
│   │       ├── adapters/   # Broker + data vendor adapters
│   │       ├── models/     # SQLAlchemy + Pydantic models
│   │       ├── events/     # Redis Streams event bus
│   │       └── utils/      # Greeks, indicators, validators
│   │
│   ├── agents/             # Agentic runtime
│   │   └── src/
│   │       ├── agents/     # Agent implementations
│   │       ├── tools/      # Deterministic tool functions
│   │       ├── skills/     # Reusable tool-chain workflows
│   │       ├── memory/     # Memory layer implementations
│   │       ├── llm/        # Groq + Ollama clients + router
│   │       └── prompts/    # System prompts for each agent
│   │
│   └── shared/             # Shared schemas, constants, types
│
├── infra/                  # Docker, K8s, monitoring configs
├── data/                   # Fixtures, sample data, historical
└── docs/                   # Architecture, API reference, runbook
```

---

## Environment Variables (.env.example)

```bash
# Database
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/trading
REDIS_URL=redis://localhost:6379/0

# Broker (NEVER commit real values)
BROKER_ADAPTER=paper  # paper | zerodha | flattrade
BROKER_API_KEY=
BROKER_API_SECRET=
BROKER_ACCESS_TOKEN=

# Data Vendor
DATA_VENDOR=mock  # mock | nse_feed | truedata
DATA_VENDOR_API_KEY=

# LLM
GROQ_API_KEY=
LLM_PROVIDER=groq  # groq | local
LOCAL_LLM_URL=http://localhost:11434  # Ollama

# Agent Config
MAX_AGENTS=20
AGENT_IDLE_TIMEOUT_SEC=300
AGENT_RETIRE_TIMEOUT_SEC=900
ENABLE_TRANSCRIPT_LOGGING=false

# Risk Params
MAX_DAILY_LOSS=20000
MAX_DRAWDOWN_PCT=10
MAX_POSITION_SIZE=4
MAX_MARGIN_UTIL_PCT=90

# App
APP_ENV=development  # development | staging | production
LOG_LEVEL=INFO
CORS_ORIGINS=http://localhost:3000
JWT_SECRET=
```

---

## Service Communication Map

```
Dashboard (3000) ──REST/WS──► API Gateway (8000)
                                    │
                    ┌───────────────┼───────────────┐
                    ▼               ▼               ▼
              Redis Streams    PostgreSQL       Agent Runtime
              (6379)           (5432)           (internal)
                    ▲               ▲               │
                    │               │               │
                    └───────────────┼───────────────┘
                                    │
                              Broker Adapter ──► Broker API (external)
                              Data Adapter ──► Data Vendor (external)
```

**Port Assignments (dev):**
| Service | Port |
|---------|------|
| Dashboard | 3000 |
| API | 8000 |
| PostgreSQL | 5432 |
| Redis | 6379 |
| Prometheus | 9090 |
| Grafana | 3001 |

---

## Data Flow: Trading Cycle

```
1. DataVendor → MarketDataService → Redis:market.ticks
2. SignalEngine reads ticks → computes features → runs strategy → Redis:signals.generated
3. RiskEngine reads signal → validates → Redis:risk.decisions
4. ExecutionGateway reads approved signal → BrokerAdapter → places order
5. BrokerAdapter → fill callback → Redis:orders.filled
6. PortfolioManager reads fill → updates positions → Redis:portfolio.updated
7. WebSocket gateway → pushes to Dashboard
8. AuditLogger → records everything to PostgreSQL
```

---

## Review Gates (CI Pipeline)

```yaml
# Runs on every PR
jobs:
  lint:        # ruff (py) + eslint (ts) — must pass, zero tolerance
  typecheck:   # mypy (py) + tsc (ts) — must pass strict mode
  unit-test:   # pytest + vitest — must pass, ≥80% coverage on changed
  build:       # docker build — must exit 0
  security:    # bandit (py) + npm audit — no high/critical

  # Runs on merge to main
  integration: # full service tests with docker-compose
  e2e:         # trading cycle E2E (paper trading)
```

---

## Definition of Done (per task)

A task is DONE when ALL of these are true:
1. ✅ Code implements all acceptance criteria listed in the task
2. ✅ Unit tests added with ≥80% coverage on new code
3. ✅ All tests pass (unit + integration if applicable)
4. ✅ Zero lint errors (ruff / eslint)
5. ✅ Zero type errors (mypy / tsc)
6. ✅ No credentials or secrets in code
7. ✅ Error handling follows patterns in RULES.md
8. ✅ Documentation updated if API/schema changed
9. ✅ PR reviewed and approved (1 approval)
10. ✅ CI pipeline green
11. ✅ Merged to main via squash merge
