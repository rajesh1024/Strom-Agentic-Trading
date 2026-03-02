# WORKFLOW.md — Agentic Trading Platform · Developer Onboarding & Workflow

> [!IMPORTANT]
> This document is the source of truth for setting up, developing, and contributing to Strom.

---

## 🚀 Getting Started (Dev Onboarding)

Follow these steps to get the platform running locally in <5 minutes.

### 1. Prerequisites
- **Docker Desktop** (with Compose)
- **Git**
- **Python 3.11+** (for local IDE support)
- **Node.js 20+** (for local IDE support)

### 2. Setup (3-Command Start)
From the project root:

1. **Initialize Environment**:
   ```bash
   cp .env.example .env
   ```
2. **Launch Services**:
   ```bash
   docker compose -f docker-compose.dev.yml up --build -d
   ```
3. **Verify Health**:
   ```bash
   docker compose -f docker-compose.dev.yml ps
   ```

### 3. Verify System Health
Once services are up, verify via terminal:
- **API**: `curl -f http://localhost:8000/health` (Expect `{"status": "ok"}`)
- **Mock Broker**: `curl -f http://localhost:8001/health`
- **Dashboard**: Open `http://localhost:3000` in your browser.

---

## 📂 Project Structure

```
strom/
├── packages/
│   ├── frontend/           # Next.js dashboard (Port 3000)
│   ├── api/                # FastAPI backend gateway (Port 8000)
│   ├── agents/             # Agentic trading runtime
│   ├── mock-broker/        # Simulated broker for testing (Port 8001)
│   └── shared/             # Shared Pydantic models & constants
├── infra/                  # Docker configs, DB init scripts
├── data/                   # Fixtures & sample data
└── .agent/                 # Agent-specific context (Rules, Specs, Workflows)
```

---

## 🛠 Development Workflow

### Git & Branching
- **Main branch**: `main` (protected)
- **Feature branches**: `workstream/T-task-id-description`
  - Example: `backend/B7-risk-engine`
- **Commits**: Follow [Conventional Commits](https://www.conventionalcommits.org/).

### Pull Request Process
1. Create branch from `main`.
2. Implement code + tests + docs.
3. Run local verification (lint + tests).
4. Push and open PR using the template in [CONTRIBUTING.md](../CONTRIBUTING.md).
5. CI must pass and 1 approval is required before merging.

---

## 🐳 Docker Workflow

### Local Operations
- **Spin up everything**: `docker compose -f docker-compose.dev.yml up -d`
- **View logs**: `docker compose -f docker-compose.dev.yml logs -f [service]`
- **Check health**: `docker compose -f docker-compose.dev.yml ps`
- **Rebuild**: `docker compose -f docker-compose.dev.yml up -d --build`
- **Shutdown**: `docker compose -f docker-compose.dev.yml down`

---

## 🧪 Testing & Quality

| Tool | Command | Purpose |
|------|---------|---------|
| **Ruff** | `ruff check .` | Linting & Formatting (Python) |
| **ESLint** | `npm run lint` | Linting & Formatting (TS) |
| **Pytest** | `pytest --cov=src`| Unit & Integration Tests |
| **Mypy** | `mypy .` | Static Type Checking |

---

## 📝 Definition of Done (DoD)
A task is NOT done until:
1. ✅ ACs in task description are met.
2. ✅ Unit tests pass with ≥80% coverage on new code.
3. ✅ Zero lint errors (ruff / eslint).
4. ✅ Zero type errors (mypy / tsc).
5. ✅ No credentials or secrets in code.
6. ✅ Error handling follows patterns in RULES.md.
7. ✅ Documentation updated if API/schema changed.
8. ✅ PR approved and CI green.
9. ✅ Docker build successful and health checks pass.
10. ✅ Merged to `main` via squash merge.

---

## 🚀 CI Pipeline (GitHub Actions)

The CI pipeline runs automatically on every Pull Request to `main`. It ensures our strict requirements are met efficiently.

**Pipeline Stages:**
1. **Linting (Parallel & Fast Fail)**: Runs `ruff` (backend/agents) and `eslint` (frontend). If linting fails, it stops immediately.
2. **Type Checking (Parallel)**: Runs `mypy` and `tsc` ensuring strict typing compliance. Need `lint` to succeed first.
3. **Tests (Parallel)**: Runs `pytest` and `vitest` with coverage checks (≥80% required on API).
4. **Security Scan**: Runs `bandit` on Python code and `npm audit` on Node code.
5. **Docker Build**: Validates image builds for `api`, `dashboard`, and `agents` concurrently using a matrix strategy.

---

## 📅 Workstream Status: Frontend
- [x] Project Scaffolding
- [x] Layout Shell & Sidebar
- [x] Responsive Mobile Bottom Nav
- [x] Dark Mode Implementation
- [x] Top Bar: Connection, Mode, Kill Switch
- [x] Shared Components Library (F8)
- [x] State Management & Data Fetching (F9)
- [ ] Markets Page Implementation
- [ ] Trading Interface
- [ ] Real-time Data Integration
