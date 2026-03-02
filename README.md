# Strom - Agentic Trading Platform

Strom is a high-performance agentic trading platform designed for SEBI compliance and deterministic execution.

## Project Structure
- `packages/api`: FastAPI backend.
- `packages/dashboard`: Next.js frontend (dashboard).
- `packages/agents`: Agentic runtime.
- `packages/shared`: Shared schemas and types.
- `infra/`: Infrastructure configurations (Docker, Postgres, etc).

## Local Development (Docker)
To start the entire environment with hot reload:

1.  Copy `.env.example` to `.env`:
    ```bash
    cp .env.example .env
    ```
2.  Spin up services:
    ```bash
    docker compose -f docker-compose.dev.yml up -d
    ```
3.  Check health:
    ```bash
    docker compose -f docker-compose.dev.yml ps
    ```

## Ports
- Dashboard: http://localhost:3000
- API: http://localhost:8000
- Postgres: 5432
- Redis: 6379
- Mock Broker: 8001

## Rules & Workflow
Refer to [.agent/RULES.md](.agent/RULES.md) and [.agent/WORKFLOW.md](.agent/WORKFLOW.md) for non-negotiable rules and development procedures.
