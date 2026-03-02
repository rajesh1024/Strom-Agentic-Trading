# Agentic Trading Platform — Full Design & Implementation Blueprint

**Version:** 1.0  
**Scope:** NIFTY/BANKNIFTY Options · India Markets · Antigravity Orchestrated  
**Date:** March 2026  

---

## 1. Executive Summary

This document specifies an enterprise-grade, multi-agent trading platform for Indian options markets (NIFTY/BANKNIFTY). The system enforces an **iron rule**: all execution, risk, and numerical computation is performed by deterministic code/tools — never by LLMs. LLM agents handle orchestration, regime classification from pre-computed features, natural-language reporting, and strategy-switching suggestions only.

A **Supervisor Agent** (Groq Llama 3.1 70B) orchestrates specialized sub-agents (Groq 8B workers) that map 1:1 to trading concerns: market data, strategy, risk, execution, portfolio, performance, alerting, and backtesting. Agents are spawned per instrument/strategy, auto-retired on idle timeout or risk-block, and governed by a deterministic Risk Engine with absolute veto power.

The platform ships as a monorepo with a React/Next.js dashboard, a FastAPI backend, Redis Streams event bus, PostgreSQL persistence, and optional pgvector for strategy embeddings. Broker and data-vendor integrations are abstracted behind adapters (paper-trading-first). The Antigravity execution plan provides 50+ parallelizable tasks across Frontend, Backend, QA, DevOps, and Docs workstreams with review gates and merge policies.

A global **kill switch** can halt all agents, cancel pending orders, and flatten positions in a single command.

---

## 2. System Architecture

### 2.1 Components & Responsibilities

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           DASHBOARD (Next.js / React)                       │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐         │
│  │ Markets  │ │  Trade   │ │Analytics │ │  Alerts  │ │  Admin   │         │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘ └──────────┘         │
│  Left Sidebar · Top Bar · Central Workspace · WebSocket Live Feed          │
└────────────────────────────────┬────────────────────────────────────────────┘
                                 │ REST + WebSocket
┌────────────────────────────────▼────────────────────────────────────────────┐
│                         API GATEWAY (FastAPI)                                │
│  /market-data  /signals  /orders  /risk  /portfolio  /strategies  /admin    │
│  Auth (JWT) · Rate Limit · Request Validation · Audit Logger               │
└──────┬──────────┬──────────┬──────────┬──────────┬──────────┬──────────────┘
       │          │          │          │          │          │
┌──────▼──┐ ┌────▼────┐ ┌───▼────┐ ┌───▼────┐ ┌──▼───┐ ┌───▼──────┐
│ Market  │ │ Signal  │ │ Risk   │ │ Exec   │ │Portf │ │ Strategy │
│ Data    │ │ Engine  │ │ Engine │ │Gateway │ │Mgr   │ │ Registry │
│ Service │ │(determ.)│ │(determ)│ │        │ │      │ │          │
└────┬────┘ └────┬────┘ └───┬────┘ └───┬────┘ └──┬───┘ └───┬──────┘
     │           │          │          │         │         │
┌────▼───────────▼──────────▼──────────▼─────────▼─────────▼──────────────────┐
│                      EVENT BUS (Redis Streams)                               │
│  Channels: market.ticks · signals.generated · risk.decisions ·               │
│            orders.submitted · orders.filled · portfolio.updated ·            │
│            agents.lifecycle · alerts.triggered · system.killswitch          │
└──────────────────────────────┬──────────────────────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────────────────────┐
│                    AGENTIC RUNTIME (Python)                                  │
│  ┌────────────────────────────────────────────────────┐                     │
│  │              SUPERVISOR AGENT (70B)                 │                     │
│  │  Spawns/retires sub-agents · Routes tasks ·         │                     │
│  │  Escalation · Strategy switch suggestions           │                     │
│  └───┬────┬────┬────┬────┬────┬────┬────┬─────────────┘                     │
│      │    │    │    │    │    │    │    │                                    │
│   ┌──▼┐┌─▼─┐┌─▼─┐┌─▼─┐┌─▼─┐┌─▼─┐┌─▼─┐┌▼──┐                              │
│   │MDA││STA││RSA││EXA││PFA││PRA││ALA││BTA│  (all 8B)                       │
│   └───┘└───┘└───┘└───┘└───┘└───┘└───┘└───┘                              │
│  MDA=MarketData STA=Strategy RSA=Risk EXA=Execution                        │
│  PFA=Portfolio  PRA=Performance ALA=Alerting BTA=Backtest                  │
└─────────────────────────────────────────────────────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────────────────────┐
│                       PERSISTENCE LAYER                                     │
│  PostgreSQL: positions, orders, audit_logs, strategy_registry, performance  │
│  Redis: working memory, session cache, pub/sub                             │
│  pgvector (optional): strategy embeddings, regime similarity search         │
│  File Store: backtest results, model artifacts                             │
└─────────────────────────────────────────────────────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────────────────────┐
│                     EXTERNAL INTEGRATIONS                                    │
│  Broker Adapter: Zerodha/Flattrade/Shoonya (paper + live)                  │
│  Data Vendor Adapter: NSE feed / TrueData / Global Datafeeds               │
│  Notification: Telegram Bot · Email · Webhook                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.2 Data Flow (Single Trading Cycle)

1. **Tick Ingestion** — Market Data Service receives option chain snapshot from data vendor adapter, normalizes to internal schema, publishes to `market.ticks` stream.
2. **Feature Computation** — Signal Engine (deterministic Python) computes Greeks, IV surface, PCR, OI change, VWAP deviation, and publishes structured feature vector to `signals.features`.
3. **Regime Classification** — MarketDataAgent (LLM) receives feature vector, classifies regime (trending/ranging/volatile/event) from pre-defined categories, publishes classification.
4. **Strategy Selection** — StrategyAgent (LLM) receives regime + strategy registry, suggests which strategy to activate/deactivate. Suggestion is logged, not auto-executed.
5. **Signal Generation** — Signal Engine runs active strategy logic (deterministic code), generates trade signal with entry/exit/SL/target, publishes to `signals.generated`.
6. **Risk Check** — RiskEngine (deterministic) validates signal against: position limits, margin availability, drawdown limits, correlation limits, time-of-day rules. Publishes APPROVE/REJECT to `risk.decisions`.
7. **Order Placement** — ExecutionAgent receives approved signal, calls Order Execution Tool (deterministic) which places order via broker adapter. Publishes to `orders.submitted`.
8. **Fill Tracking** — Execution Gateway monitors fills, publishes to `orders.filled`.
9. **Portfolio Update** — PortfolioAgent updates position state, Greeks exposure, P&L. Publishes to `portfolio.updated`.
10. **Dashboard Push** — WebSocket gateway pushes events to dashboard in real-time.
11. **Memory Write** — Performance metadata, signal outcomes, and regime classifications are written to long-term memory store.

### 2.3 Deployment Topology

| Environment | Infra | Broker Mode | Data Source | LLM |
|-------------|-------|-------------|-------------|-----|
| **Dev** | Docker Compose (local) | Paper trading (mock) | Recorded snapshots | Groq API (8B only) |
| **Staging** | Docker Compose (VPS) | Paper trading (live feed) | Live vendor (sandbox) | Groq API (8B + 70B) |
| **Production** | K8s (2-3 nodes) or Docker Swarm | Live broker | Live vendor | Groq API + local fallback |

```
[Dev Laptop]                    [Staging VPS]              [Prod Cluster]
 docker-compose.dev.yml          docker-compose.stg.yml     k8s manifests
 ├── api (FastAPI)               ├── api (2 replicas)       ├── api (3 replicas, HPA)
 ├── dashboard (Next.js)         ├── dashboard              ├── dashboard (CDN)
 ├── redis                       ├── redis                  ├── redis (sentinel)
 ├── postgres                    ├── postgres               ├── postgres (managed RDS)
 ├── agent-runtime               ├── agent-runtime          ├── agent-runtime (2 pods)
 └── mock-broker                 └── paper-broker           └── live-broker-adapter
```

### 2.4 Security & Compliance Notes

**India Trading Context (SEBI/NSE regulatory awareness):**

- **No algo-trading registration bypasses.** This platform is designed for semi-automated/advisory use. If used for fully automated order execution, the operator must comply with SEBI circular on algorithmic trading (SEBI/HO/MRD/DP/CIR/P/2016/127 and subsequent amendments).
- **Credential isolation:** Broker API keys and secrets are stored in environment variables or a secrets manager (Vault/SOPS), never in database, never in agent memory, never in logs.
- **Audit trail:** Every order attempt, risk decision, and agent action is logged with timestamp, agent ID, inputs, and outputs to `audit_logs` table. Retained for minimum 5 years per SEBI record-keeping norms.
- **Kill switch:** Global emergency stop accessible via API (`POST /admin/killswitch`), dashboard button, and Telegram command. Actions: (a) cancel all pending orders, (b) optionally flatten all positions, (c) halt all agent activity, (d) publish to `system.killswitch` stream.
- **Data residency:** All data stored on India-located servers in production. Groq API calls transmit only structured features and natural-language summaries — never PII, credentials, or raw order book data.
- **Rate limiting:** All broker API calls are rate-limited per broker's published limits (e.g., Zerodha: 10 orders/sec, 200 orders/min).
- **Position limits:** Hard-coded per-instrument position limits matching exchange-mandated limits for the account category.
- **No LLM in the order path:** The RiskEngine and Execution Gateway are pure deterministic code. LLM agents can suggest but never directly execute financial transactions.

---

## 3. Agentic Runtime Design

### 3.1 Agent Roster

| Agent | Model | Responsibility | Spawned By | Max Instances |
|-------|-------|---------------|------------|---------------|
| **SupervisorAgent** | Groq 70B | Orchestrates all sub-agents; routes tasks; escalation; strategy switch suggestions; spawns/retires agents | System (singleton) | 1 |
| **MarketDataAgent** | Groq 8B | Regime classification from structured features; data quality commentary; anomaly flagging | Supervisor | 1 per instrument |
| **StrategyAgent** | Groq 8B | Suggests strategy activation/deactivation based on regime + performance history; explains rationale | Supervisor | 1 per strategy group |
| **RiskAgent** | Groq 8B | Summarizes risk state in natural language; explains risk rejections; drafts risk reports | Supervisor | 1 (global) |
| **ExecutionAgent** | Groq 8B | Orchestrates order placement workflow; monitors fill status; reports slippage | Supervisor | 1 per active order batch |
| **PortfolioAgent** | Groq 8B | Summarizes portfolio state; generates P&L commentary; suggests rebalancing narratives | Supervisor | 1 (global) |
| **PerformanceAgent** | Groq 8B | Generates daily/weekly performance summaries; identifies patterns in win/loss data | Supervisor | 1 (global) |
| **AlertingAgent** | Groq 8B | Composes alert messages; prioritizes alerts; manages notification routing | Supervisor | 1 (global) |
| **BacktestAgent** | Groq 8B | Orchestrates backtest workflows; summarizes backtest results; compares strategies | Supervisor | 1 per backtest run |

### 3.2 Agent Lifecycle

```
┌──────────┐    Supervisor decides     ┌──────────┐
│  DORMANT │ ──────────────────────► │ SPAWNING │
└──────────┘    (new instrument/       └────┬─────┘
                 strategy detected)         │
                                            ▼
                                      ┌──────────┐
                              ┌────── │  ACTIVE  │ ◄──── receives tasks
                              │       └────┬─────┘
                              │            │
                     idle > 5min      risk block / error
                              │            │
                              ▼            ▼
                        ┌──────────┐ ┌──────────┐
                        │  IDLE    │ │ BLOCKED  │
                        └────┬─────┘ └────┬─────┘
                             │            │
                    idle > 15min    manual resume or
                             │      supervisor decision
                             ▼            │
                        ┌──────────┐      │
                        │ RETIRED  │ ◄────┘ (if unresolvable)
                        └──────────┘
```

**Rules:**
- **Spawn:** Supervisor spawns an agent when a new instrument is added to watch list, a new strategy is activated, or a backtest is requested.
- **Idle timeout:** Agent moves to IDLE after 5 minutes of no task. After 15 minutes idle, agent is RETIRED (context discarded, resources freed).
- **Risk block:** If RiskEngine blocks an agent's instrument/strategy, agent moves to BLOCKED. Supervisor logs the block reason and notifies operator.
- **Kill switch:** All agents immediately transition to RETIRED on kill switch event.
- **Max concurrent agents:** Configurable (default: 20). Supervisor queues spawn requests if at capacity.
- **Heartbeat:** Each active agent publishes heartbeat every 30 seconds to `agents.lifecycle` stream. Supervisor monitors for missed heartbeats (tolerance: 2 missed = auto-retire with alert).

### 3.3 Tool Catalog

Every tool is a deterministic Python function with strict input/output schemas. Agents call tools via structured JSON; they cannot invent new tools at runtime.

#### Tool 1: `fetch_option_chain`
```
Name:        fetch_option_chain
Description: Retrieves current option chain for a given underlying
Inputs:      { "underlying": "NIFTY"|"BANKNIFTY", "expiry": "YYYY-MM-DD" }
Outputs:     { "timestamp": ISO8601, "chain": [{ "strike": int, "ce_ltp": float, 
               "pe_ltp": float, "ce_oi": int, "pe_oi": int, "ce_iv": float, 
               "pe_iv": float, "ce_greeks": {...}, "pe_greeks": {...} }] }
Failure:     { "error": "DATA_STALE"|"VENDOR_TIMEOUT"|"MARKET_CLOSED" }
Fallback:    Returns last cached chain with "stale": true flag. Agent must not 
             generate signals from stale data.
```

#### Tool 2: `compute_features`
```
Name:        compute_features
Description: Computes structured feature vector from option chain
Inputs:      { "chain": <option_chain_object>, "underlying_price": float }
Outputs:     { "pcr": float, "iv_skew": float, "max_pain": int, 
               "oi_change_ce_top5": [...], "oi_change_pe_top5": [...],
               "vwap_deviation": float, "atr_14": float, "rsi_14": float,
               "regime_features": { "volatility_rank": float, 
               "trend_strength": float, "mean_reversion_score": float } }
Failure:     { "error": "INSUFFICIENT_DATA"|"COMPUTATION_ERROR" }
```

#### Tool 3: `evaluate_signal`
```
Name:        evaluate_signal
Description: Runs strategy logic on features; produces trade signal
Inputs:      { "strategy_id": str, "features": <feature_vector>, 
               "current_positions": [...], "params": {...} }
Outputs:     { "signal": "BUY"|"SELL"|"HOLD", "instrument": str, 
               "strike": int, "option_type": "CE"|"PE", "qty": int,
               "entry_price": float, "stop_loss": float, "target": float,
               "confidence_score": float, "rationale_data": {...} }
Failure:     { "error": "STRATEGY_NOT_FOUND"|"PARAM_INVALID"|"NO_SIGNAL" }
```

#### Tool 4: `check_risk`
```
Name:        check_risk
Description: Validates trade signal against all risk rules
Inputs:      { "signal": <signal_object>, "portfolio_state": <portfolio>, 
               "risk_params": <risk_config> }
Outputs:     { "approved": bool, "risk_score": float, 
               "checks": [{ "rule": str, "passed": bool, "detail": str }],
               "modified_signal": <signal_object>|null }
Failure:     { "error": "RISK_ENGINE_ERROR" } → defaults to REJECT
Risk Rules:  max_position_size, max_portfolio_delta, max_daily_loss,
             max_drawdown, margin_check, time_of_day_check, 
             correlation_limit, single_instrument_concentration
```

#### Tool 5: `place_order`
```
Name:        place_order
Description: Submits order to broker via adapter
Inputs:      { "instrument": str, "side": "BUY"|"SELL", "qty": int, 
               "order_type": "LIMIT"|"MARKET"|"SL", "price": float|null,
               "trigger_price": float|null, "tag": str }
Outputs:     { "order_id": str, "status": "SUBMITTED"|"REJECTED", 
               "broker_ref": str, "timestamp": ISO8601 }
Failure:     { "error": "BROKER_TIMEOUT"|"INSUFFICIENT_MARGIN"|"RATE_LIMITED" }
Pre-check:   MUST have passing check_risk result. Tool refuses without it.
```

#### Tool 6: `get_order_status`
```
Name:        get_order_status
Description: Checks status of a submitted order
Inputs:      { "order_id": str }
Outputs:     { "order_id": str, "status": "PENDING"|"OPEN"|"FILLED"|"CANCELLED"|"REJECTED",
               "filled_qty": int, "avg_fill_price": float, "timestamp": ISO8601 }
Failure:     { "error": "ORDER_NOT_FOUND"|"BROKER_TIMEOUT" }
```

#### Tool 7: `get_portfolio_state`
```
Name:        get_portfolio_state
Description: Returns current portfolio snapshot
Inputs:      { "include_greeks": bool, "include_pnl": bool }
Outputs:     { "positions": [{ "instrument": str, "qty": int, "avg_price": float,
               "ltp": float, "pnl": float, "greeks": {...} }],
               "total_pnl": float, "margin_used": float, "margin_available": float,
               "portfolio_greeks": { "delta": float, "gamma": float, 
               "theta": float, "vega": float } }
Failure:     { "error": "PORTFOLIO_SYNC_ERROR" }
```

#### Tool 8: `run_backtest`
```
Name:        run_backtest
Description: Executes strategy backtest on historical data
Inputs:      { "strategy_id": str, "start_date": "YYYY-MM-DD", 
               "end_date": "YYYY-MM-DD", "params": {...}, "initial_capital": float }
Outputs:     { "backtest_id": str, "summary": { "total_return": float, 
               "sharpe": float, "max_drawdown": float, "win_rate": float,
               "total_trades": int, "avg_profit": float, "avg_loss": float },
               "equity_curve": [...], "trades": [...] }
Failure:     { "error": "INSUFFICIENT_HISTORY"|"STRATEGY_ERROR" }
```

#### Tool 9: `write_memory`
```
Name:        write_memory
Description: Writes structured data to memory store
Inputs:      { "layer": "working"|"session"|"long_term", "key": str, 
               "data": <json_object>, "ttl_seconds": int|null }
Outputs:     { "stored": bool, "key": str }
Failure:     { "error": "MEMORY_WRITE_FAILED"|"SCHEMA_VIOLATION" }
Constraints: Cannot store: credentials, raw order book, PII, unstructured 
             LLM transcripts (unless explicitly flagged)
```

#### Tool 10: `read_memory`
```
Name:        read_memory
Description: Reads from memory store
Inputs:      { "layer": "working"|"session"|"long_term", "key": str }
Outputs:     { "found": bool, "data": <json_object>|null, "timestamp": ISO8601 }
```

#### Tool 11: `send_alert`
```
Name:        send_alert
Description: Sends alert via configured channels
Inputs:      { "severity": "INFO"|"WARNING"|"CRITICAL", "channel": "telegram"|"email"|"webhook",
               "title": str, "body": str, "metadata": {...} }
Outputs:     { "sent": bool, "channel": str, "timestamp": ISO8601 }
Failure:     { "error": "CHANNEL_UNAVAILABLE"|"RATE_LIMITED" }
```

#### Tool 12: `query_strategy_registry`
```
Name:        query_strategy_registry
Description: Queries available strategies and their metadata
Inputs:      { "filter": { "underlying": str|null, "regime": str|null, 
               "active_only": bool } }
Outputs:     { "strategies": [{ "id": str, "name": str, "type": str,
               "underlying": str, "regime_affinity": [str], "active": bool,
               "performance_30d": { "return": float, "sharpe": float } }] }
```

### 3.4 Memory Design

```
┌─────────────────────────────────────────────────────────────┐
│                    MEMORY ARCHITECTURE                       │
│                                                             │
│  ┌─────────────────┐  ┌──────────────┐  ┌───────────────┐  │
│  │ WORKING MEMORY  │  │SESSION MEMORY│  │ LONG-TERM     │  │
│  │ (Redis)         │  │ (Redis)      │  │ (PostgreSQL)  │  │
│  │ TTL: 5 min      │  │ TTL: 1 day   │  │ TTL: none     │  │
│  │                 │  │              │  │               │  │
│  │ • Current tick  │  │ • Today's    │  │ • Trade log   │  │
│  │ • Active signal │  │   signals    │  │ • Strategy    │  │
│  │ • Pending order │  │ • Session    │  │   performance │  │
│  │ • Agent context │  │   P&L        │  │ • Regime hist │  │
│  │ • Feature cache │  │ • Agent      │  │ • Config hist │  │
│  │                 │  │   decisions  │  │ • Audit logs  │  │
│  └─────────────────┘  └──────────────┘  └───────────────┘  │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐    │
│  │ VECTOR STORE (pgvector — optional)                  │    │
│  │ • Strategy description embeddings                   │    │
│  │ • Regime pattern embeddings (for similarity search) │    │
│  │ • Historical signal context embeddings              │    │
│  └─────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

**Schemas:**

**Working Memory (Redis Hash)**
```json
{
  "wm:{agent_id}:{key}": {
    "data": { /* any structured JSON */ },
    "updated_at": "2026-03-02T10:30:00Z",
    "ttl": 300
  }
}
```

**Session Memory (Redis Hash)**
```json
{
  "sm:session:{date}:signals": [
    { "signal_id": "sig_001", "strategy": "iron_condor_v2", "instrument": "NIFTY24MAR25000CE",
      "signal": "BUY", "risk_approved": true, "outcome": "FILLED", "pnl": 1250.0 }
  ],
  "sm:session:{date}:regime_log": [
    { "time": "09:30", "regime": "trending_up", "confidence": 0.82 }
  ]
}
```

**Long-Term Memory (PostgreSQL Tables)**
```sql
-- Trade Performance
CREATE TABLE trade_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    trade_date DATE NOT NULL,
    strategy_id VARCHAR(64) NOT NULL,
    instrument VARCHAR(128) NOT NULL,
    side VARCHAR(4) NOT NULL,
    qty INTEGER NOT NULL,
    entry_price DECIMAL(12,2),
    exit_price DECIMAL(12,2),
    pnl DECIMAL(12,2),
    slippage DECIMAL(12,2),
    regime VARCHAR(32),
    signal_metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Strategy Performance Aggregates
CREATE TABLE strategy_performance (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    strategy_id VARCHAR(64) NOT NULL,
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,
    total_trades INTEGER,
    win_rate DECIMAL(5,2),
    total_pnl DECIMAL(12,2),
    sharpe_ratio DECIMAL(6,3),
    max_drawdown DECIMAL(5,2),
    avg_slippage DECIMAL(8,2),
    regime_distribution JSONB,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Audit Log
CREATE TABLE audit_log (
    id BIGSERIAL PRIMARY KEY,
    timestamp TIMESTAMPTZ DEFAULT now(),
    agent_id VARCHAR(64),
    action VARCHAR(64) NOT NULL,
    inputs JSONB,
    outputs JSONB,
    risk_decision VARCHAR(16),
    order_id VARCHAR(64),
    metadata JSONB
);

-- Strategy Registry
CREATE TABLE strategy_registry (
    id VARCHAR(64) PRIMARY KEY,
    name VARCHAR(256) NOT NULL,
    version INTEGER DEFAULT 1,
    type VARCHAR(32) NOT NULL,  -- 'iron_condor', 'straddle', 'directional', etc.
    underlying VARCHAR(32) NOT NULL,
    regime_affinity VARCHAR(32)[] DEFAULT '{}',
    params JSONB NOT NULL,
    active BOOLEAN DEFAULT false,
    backtest_summary JSONB,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);
```

**Memory Write Rules (ENFORCED BY TOOL):**

| Allowed to Store | NOT Allowed to Store |
|-----------------|---------------------|
| Structured feature vectors | Broker API keys/secrets |
| Trade signals & outcomes | Raw order book data |
| Regime classifications | PII of any kind |
| Strategy metadata & performance | Unstructured LLM transcripts* |
| Risk decisions & rationale data | Raw tick-by-tick data (use time-series DB) |
| Agent lifecycle events | Other users' data |

*Unless operator explicitly enables transcript logging for debugging (flag: `ENABLE_TRANSCRIPT_LOGGING=true`)

### 3.5 Skill Library

A **skill** is a reusable, validated workflow composed of tool calls + validation steps. Agents invoke skills, not raw tool chains.

#### Skill 1: `analyze_market_regime`
```yaml
name: analyze_market_regime
description: Fetches latest data, computes features, classifies regime
tools_chain:
  1. fetch_option_chain(underlying, expiry)
  2. compute_features(chain, underlying_price)
  3. [LLM] classify_regime(features)  # MarketDataAgent interprets features
validation:
  - chain.stale == false
  - features.regime_features is complete (no null values)
  - classification is one of: [trending_up, trending_down, ranging, volatile, event_driven]
output: { features: {...}, regime: str, confidence: float }
```

#### Skill 2: `generate_and_validate_signal`
```yaml
name: generate_and_validate_signal
description: Generates trade signal and validates through risk engine
tools_chain:
  1. evaluate_signal(strategy_id, features, positions, params)
  2. check_risk(signal, portfolio_state, risk_params)
  3. [LLM] explain_signal(signal, risk_result)  # StrategyAgent narrates
validation:
  - signal is not NO_SIGNAL
  - risk checks all enumerated (no silent failures)
  - if risk rejected: log reason, do not proceed to execution
output: { signal: {...}, risk_approved: bool, explanation: str }
```

#### Skill 3: `execute_trade_cycle`
```yaml
name: execute_trade_cycle
description: Places order, monitors fill, updates portfolio
tools_chain:
  1. place_order(instrument, side, qty, order_type, price)
  2. [poll] get_order_status(order_id) — max 10 attempts, 2s interval
  3. get_portfolio_state(include_greeks=true, include_pnl=true)
  4. write_memory("session", trade_record)
  5. send_alert(severity="INFO", ...)
validation:
  - order submitted successfully
  - fill received within timeout (else cancel + alert)
  - portfolio state refreshed post-fill
output: { order: {...}, fill: {...}, portfolio: {...} }
```

#### Skill 4: `daily_performance_report`
```yaml
name: daily_performance_report
description: Generates end-of-day performance summary
tools_chain:
  1. read_memory("session", today_trades)
  2. get_portfolio_state(include_pnl=true)
  3. [LLM] generate_summary(trades, portfolio)  # PerformanceAgent
  4. write_memory("long_term", daily_summary)
  5. send_alert(severity="INFO", channel="telegram", body=summary)
validation:
  - all trades for the day are included
  - P&L figures match portfolio state
output: { summary_text: str, metrics: {...} }
```

#### Skill 5: `run_strategy_backtest`
```yaml
name: run_strategy_backtest
description: Runs backtest and generates comparative analysis
tools_chain:
  1. query_strategy_registry(filter)
  2. run_backtest(strategy_id, dates, params, capital)
  3. read_memory("long_term", historical_performance)
  4. [LLM] compare_and_summarize(backtest, historical)  # BacktestAgent
  5. write_memory("long_term", backtest_result)
validation:
  - backtest completed without errors
  - sufficient historical data (min 30 trading days)
  - summary includes key metrics: Sharpe, drawdown, win rate
output: { backtest: {...}, comparison: str, recommendation: str }
```

#### Skill 6: `emergency_shutdown`
```yaml
name: emergency_shutdown
description: Kill switch — halts all operations
tools_chain:
  1. [broadcast] system.killswitch event
  2. [for each pending order] cancel_order(order_id)
  3. [optional] flatten_positions()  # if configured
  4. [retire all agents]
  5. send_alert(severity="CRITICAL", channel=["telegram","email"], body="KILL SWITCH ACTIVATED")
  6. write_memory("long_term", { event: "killswitch", reason: str, timestamp: ISO8601 })
validation:
  - all pending orders confirmed cancelled
  - all agents confirmed retired
  - alert sent successfully
output: { cancelled_orders: [...], flattened_positions: [...], agents_retired: int }
```

---

## 4. Model Strategy

### 4.1 Model Allocation

| Agent | Model | Rationale |
|-------|-------|-----------|
| SupervisorAgent | Groq Llama 3.1 70B | Complex orchestration, multi-step reasoning, strategy comparison, escalation decisions |
| MarketDataAgent | Groq Llama 3.1 8B | Simple classification from structured features; low latency critical |
| StrategyAgent | Groq Llama 3.1 8B | Pattern matching against known strategy profiles; escalates to Supervisor for novel situations |
| RiskAgent | Groq Llama 3.1 8B | Summarization of deterministic risk engine outputs; natural language explanation |
| ExecutionAgent | Groq Llama 3.1 8B | Workflow orchestration; status reporting; simple decision trees |
| PortfolioAgent | Groq Llama 3.1 8B | Portfolio summarization; P&L commentary |
| PerformanceAgent | Groq Llama 3.1 8B | Report generation from structured data |
| AlertingAgent | Groq Llama 3.1 8B | Message composition; priority classification |
| BacktestAgent | Groq Llama 3.1 8B | Result summarization; strategy comparison narratives |
| **Local Fallback** | Llama 3.1 8B (Ollama) | Summarization tasks when Groq is unavailable or for cost reduction on non-critical tasks |

### 4.2 Latency/Cost Optimization

```
                    ┌─────────────────┐
                    │  INCOMING TASK   │
                    └───────┬─────────┘
                            │
                    ┌───────▼─────────┐
                    │ COMPLEXITY CHECK │
                    └───────┬─────────┘
                       ┌────┴────┐
                  LOW  │         │  HIGH
                  ┌────▼───┐ ┌──▼──────┐
                  │ 8B     │ │  70B    │
                  │ Worker │ │  Super  │
                  └────┬───┘ └──┬──────┘
                       │        │
                  ┌────▼────────▼───┐
                  │  GROQ AVAILABLE? │
                  └───────┬─────────┘
                     ┌────┴────┐
                YES  │         │  NO
                ┌────▼───┐ ┌──▼──────┐
                │ Groq   │ │ Local   │
                │ Cloud  │ │ Ollama  │
                └────────┘ └─────────┘
```

**Routing Rules:**
1. **Default path:** All sub-agent tasks → Groq 8B (fastest, cheapest).
2. **Escalation:** If sub-agent confidence < 0.6 on classification or if task requires multi-strategy comparison → route to Supervisor (70B).
3. **Fallback:** If Groq API returns 429/503 → retry once after 1s → if still failing, route to local Ollama 8B.
4. **Cost control:** Daily LLM call budget tracked. If budget exceeded, switch to local models for all non-critical tasks (alerting, reporting). Critical tasks (regime classification during market hours) always use Groq.
5. **Batch optimization:** Non-urgent tasks (performance reports, backtest summaries) are batched and processed in off-market hours using local models.
6. **Caching:** Regime classifications are cached for 60 seconds. Repeated queries within TTL return cached result without LLM call.

**Estimated Cost (per trading day):**
- Groq 8B: ~500 calls × avg 500 tokens = 250K tokens → ~$0.05
- Groq 70B: ~50 calls × avg 1000 tokens = 50K tokens → ~$0.30
- Total: ~$0.35/day (well within Groq free tier for development)

---

## 5. Implementation Blueprint

### 5.1 Repo Folder Structure

```
agentic-trading-platform/
├── README.md
├── docker-compose.yml
├── docker-compose.dev.yml
├── docker-compose.stg.yml
├── .env.example
├── .github/
│   └── workflows/
│       ├── ci.yml
│       ├── cd-staging.yml
│       └── cd-prod.yml
│
├── packages/
│   ├── dashboard/                    # Next.js frontend
│   │   ├── package.json
│   │   ├── next.config.js
│   │   ├── tailwind.config.js
│   │   ├── src/
│   │   │   ├── app/                  # App router
│   │   │   │   ├── layout.tsx
│   │   │   │   ├── page.tsx
│   │   │   │   ├── markets/
│   │   │   │   ├── trade/
│   │   │   │   ├── analytics/
│   │   │   │   ├── alerts/
│   │   │   │   └── admin/
│   │   │   ├── components/
│   │   │   │   ├── layout/           # Sidebar, TopBar, Workspace
│   │   │   │   ├── markets/          # OptionChainTable, IVChart, OIChart
│   │   │   │   ├── trade/            # SignalCard, OrderForm, PositionTable
│   │   │   │   ├── analytics/        # PnLChart, DrawdownChart, RegimeTimeline
│   │   │   │   ├── alerts/           # AlertList, AlertConfig
│   │   │   │   ├── admin/            # KillSwitch, AgentMonitor, StrategyManager
│   │   │   │   └── shared/           # DataTable, StatusBadge, MetricCard
│   │   │   ├── hooks/
│   │   │   │   ├── useWebSocket.ts
│   │   │   │   ├── useMarketData.ts
│   │   │   │   └── usePortfolio.ts
│   │   │   ├── lib/
│   │   │   │   ├── api.ts            # API client
│   │   │   │   └── ws.ts             # WebSocket client
│   │   │   └── types/
│   │   │       └── index.ts
│   │   └── tests/
│   │
│   ├── api/                          # FastAPI backend
│   │   ├── pyproject.toml
│   │   ├── src/
│   │   │   ├── main.py               # FastAPI app entry
│   │   │   ├── config.py             # Settings (pydantic-settings)
│   │   │   ├── routers/
│   │   │   │   ├── market_data.py
│   │   │   │   ├── signals.py
│   │   │   │   ├── orders.py
│   │   │   │   ├── risk.py
│   │   │   │   ├── portfolio.py
│   │   │   │   ├── strategies.py
│   │   │   │   ├── admin.py          # Kill switch, config
│   │   │   │   └── ws.py             # WebSocket endpoint
│   │   │   ├── services/
│   │   │   │   ├── market_data_service.py
│   │   │   │   ├── signal_engine.py  # Deterministic strategy logic
│   │   │   │   ├── risk_engine.py    # Deterministic risk checks
│   │   │   │   ├── execution_gateway.py
│   │   │   │   ├── portfolio_manager.py
│   │   │   │   └── strategy_registry.py
│   │   │   ├── adapters/
│   │   │   │   ├── broker/
│   │   │   │   │   ├── base.py       # Abstract broker interface
│   │   │   │   │   ├── zerodha.py
│   │   │   │   │   ├── flattrade.py
│   │   │   │   │   └── paper.py      # Paper trading adapter
│   │   │   │   └── data_vendor/
│   │   │   │       ├── base.py
│   │   │   │       ├── nse_feed.py
│   │   │   │       └── truedata.py
│   │   │   ├── models/               # SQLAlchemy / Pydantic models
│   │   │   │   ├── db.py
│   │   │   │   ├── trade.py
│   │   │   │   ├── order.py
│   │   │   │   ├── portfolio.py
│   │   │   │   └── audit.py
│   │   │   ├── events/
│   │   │   │   ├── bus.py            # Redis Streams wrapper
│   │   │   │   ├── publishers.py
│   │   │   │   └── consumers.py
│   │   │   └── utils/
│   │   │       ├── greeks.py         # Black-Scholes, Greeks computation
│   │   │       ├── indicators.py     # RSI, ATR, VWAP, etc.
│   │   │       └── validators.py
│   │   ├── tests/
│   │   │   ├── test_risk_engine.py
│   │   │   ├── test_signal_engine.py
│   │   │   ├── test_execution.py
│   │   │   └── test_api_routes.py
│   │   └── migrations/               # Alembic
│   │       └── versions/
│   │
│   ├── agents/                       # Agentic runtime
│   │   ├── pyproject.toml
│   │   ├── src/
│   │   │   ├── supervisor.py         # Supervisor agent
│   │   │   ├── agents/
│   │   │   │   ├── base.py           # BaseAgent class
│   │   │   │   ├── market_data.py
│   │   │   │   ├── strategy.py
│   │   │   │   ├── risk.py
│   │   │   │   ├── execution.py
│   │   │   │   ├── portfolio.py
│   │   │   │   ├── performance.py
│   │   │   │   ├── alerting.py
│   │   │   │   └── backtest.py
│   │   │   ├── tools/
│   │   │   │   ├── registry.py       # Tool registration + dispatch
│   │   │   │   ├── market_tools.py
│   │   │   │   ├── trade_tools.py
│   │   │   │   ├── risk_tools.py
│   │   │   │   ├── portfolio_tools.py
│   │   │   │   ├── memory_tools.py
│   │   │   │   └── alert_tools.py
│   │   │   ├── skills/
│   │   │   │   ├── registry.py
│   │   │   │   ├── market_regime.py
│   │   │   │   ├── signal_validation.py
│   │   │   │   ├── trade_execution.py
│   │   │   │   ├── daily_report.py
│   │   │   │   ├── backtest_analysis.py
│   │   │   │   └── emergency_shutdown.py
│   │   │   ├── memory/
│   │   │   │   ├── working.py        # Redis working memory
│   │   │   │   ├── session.py        # Redis session memory
│   │   │   │   └── long_term.py      # PostgreSQL long-term
│   │   │   ├── llm/
│   │   │   │   ├── groq_client.py    # Groq API wrapper
│   │   │   │   ├── local_client.py   # Ollama wrapper
│   │   │   │   └── router.py         # Model routing logic
│   │   │   └── prompts/
│   │   │       ├── supervisor.py
│   │   │       ├── market_data.py
│   │   │       ├── strategy.py
│   │   │       ├── risk.py
│   │   │       ├── execution.py
│   │   │       ├── portfolio.py
│   │   │       ├── performance.py
│   │   │       ├── alerting.py
│   │   │       └── backtest.py
│   │   └── tests/
│   │
│   └── shared/                       # Shared types, constants, schemas
│       ├── schemas/
│       │   ├── events.py
│       │   ├── signals.py
│       │   └── tools.py
│       └── constants.py
│
├── infra/
│   ├── docker/
│   │   ├── Dockerfile.api
│   │   ├── Dockerfile.dashboard
│   │   ├── Dockerfile.agents
│   │   └── Dockerfile.redis
│   ├── k8s/
│   │   ├── api-deployment.yml
│   │   ├── agents-deployment.yml
│   │   ├── redis-statefulset.yml
│   │   └── postgres-statefulset.yml
│   └── scripts/
│       ├── seed_strategies.py
│       ├── migrate.sh
│       └── healthcheck.sh
│
├── data/
│   ├── sample_option_chain.json
│   ├── historical/                   # For backtesting
│   └── fixtures/                     # Test fixtures
│
└── docs/
    ├── architecture.md
    ├── api-reference.md
    ├── agent-design.md
    ├── runbook.md
    └── antigravity-tasks.md
```

### 5.2 Tech Stack

| Layer | Technology | Rationale |
|-------|-----------|-----------|
| **Frontend** | Next.js 14 (App Router) + React 18 + TypeScript | SSR for SEO-irrelevant but good DX; App Router for layouts |
| **UI Library** | Tailwind CSS + shadcn/ui + Recharts | Fast development; consistent design; good charts |
| **State** | Zustand + React Query (TanStack) | Lightweight global state + server state caching |
| **Real-time** | Native WebSocket (via FastAPI) | Low latency for market data; simpler than Socket.IO |
| **Backend** | FastAPI (Python 3.11+) | Async-first; Pydantic validation; auto OpenAPI docs |
| **ORM** | SQLAlchemy 2.0 + Alembic | Mature; async support; migration tooling |
| **Event Bus** | Redis Streams | Lightweight Kafka alternative; persistent; consumer groups |
| **Cache** | Redis | Working memory + session memory + pub/sub |
| **Database** | PostgreSQL 16 + pgvector | Reliable; JSONB for flexible schemas; vector search optional |
| **LLM Client** | Groq Python SDK + Ollama (local) | Fast inference; easy switching |
| **Agent Framework** | Custom (lightweight) | Minimal overhead; full control over tool dispatch and lifecycle |
| **Monitoring** | Prometheus + Grafana | Metrics collection + dashboarding |
| **Logging** | structlog → stdout → Loki (or ELK) | Structured JSON logs; centralized aggregation |
| **Tracing** | OpenTelemetry → Jaeger | Distributed tracing across agents and services |
| **CI/CD** | GitHub Actions | Standard; Antigravity-compatible |

### 5.3 API Contracts (OpenAPI Outline)

```yaml
openapi: 3.1.0
info:
  title: Agentic Trading Platform API
  version: 1.0.0

paths:
  /api/v1/market-data/option-chain/{underlying}:
    get:
      summary: Get current option chain
      parameters:
        - name: underlying
          in: path
          schema: { type: string, enum: [NIFTY, BANKNIFTY] }
        - name: expiry
          in: query
          schema: { type: string, format: date }
      responses:
        200: { description: Option chain data }
  
  /api/v1/market-data/features/{underlying}:
    get:
      summary: Get computed feature vector
      responses:
        200: { description: Feature vector with regime classification }

  /api/v1/signals:
    get:
      summary: List recent signals
      parameters:
        - name: strategy_id
          in: query
        - name: status
          in: query
          schema: { enum: [pending, approved, rejected, executed] }
    post:
      summary: Trigger signal evaluation
      requestBody:
        content:
          application/json:
            schema: { $ref: '#/components/schemas/SignalRequest' }

  /api/v1/orders:
    get:
      summary: List orders
    post:
      summary: Place order (requires risk approval)

  /api/v1/orders/{order_id}:
    get:
      summary: Get order status
    delete:
      summary: Cancel order

  /api/v1/portfolio:
    get:
      summary: Get portfolio state with P&L and Greeks

  /api/v1/risk/check:
    post:
      summary: Run risk check on proposed signal

  /api/v1/risk/state:
    get:
      summary: Get current risk state (limits, utilization)

  /api/v1/strategies:
    get:
      summary: List strategies
    post:
      summary: Register new strategy
    
  /api/v1/strategies/{id}/activate:
    post:
      summary: Activate strategy

  /api/v1/strategies/{id}/backtest:
    post:
      summary: Run backtest
      
  /api/v1/admin/killswitch:
    post:
      summary: Activate kill switch
      requestBody:
        content:
          application/json:
            schema:
              type: object
              properties:
                flatten_positions: { type: boolean, default: false }
                reason: { type: string }

  /api/v1/admin/agents:
    get:
      summary: List active agents with status

  /api/v1/admin/config:
    get:
      summary: Get system configuration
    patch:
      summary: Update configuration

  /api/v1/ws:
    description: WebSocket endpoint for real-time updates
    # Channels: market.ticks, signals, orders, portfolio, alerts, agents
```

### 5.4 Observability

**Structured Log Schema (JSON):**
```json
{
  "timestamp": "2026-03-02T10:30:00.123Z",
  "level": "INFO",
  "service": "api|agents|risk_engine",
  "agent_id": "strategy_agent_nifty_01",
  "action": "signal_generated|risk_check|order_placed|agent_spawned",
  "correlation_id": "cycle_20260302_103000",
  "inputs": { /* structured */ },
  "outputs": { /* structured */ },
  "duration_ms": 45,
  "model": "llama-3.1-8b",
  "tokens_used": 250,
  "error": null
}
```

**Metrics (Prometheus):**
- `trading_signals_total{strategy, outcome}` — counter
- `trading_orders_total{status, broker}` — counter
- `trading_pnl_daily` — gauge
- `risk_checks_total{result}` — counter
- `agent_active_count{type}` — gauge
- `agent_task_duration_seconds{agent_type}` — histogram
- `llm_calls_total{model, agent_type}` — counter
- `llm_latency_seconds{model}` — histogram
- `llm_tokens_total{model, direction}` — counter
- `event_bus_lag_seconds{stream}` — gauge
- `broker_api_latency_seconds{broker, endpoint}` — histogram

**Audit Log Table** (see Section 3.4 for schema — every state-changing action is recorded).

**Trace Context:** Every trading cycle gets a `correlation_id` that propagates through all tool calls, agent tasks, and events. This allows reconstructing the full decision chain for any trade.

---

## 6. Antigravity Execution Plan

### 6.1 Workstreams Overview

```
┌─────────────────────────────────────────────────────────────┐
│                  ANTIGRAVITY MISSION CONTROL                │
│                                                             │
│  ┌──────────┐  ┌──────────┐  ┌──────┐  ┌──────┐ ┌───────┐ │
│  │ Backend  │  │ Frontend │  │  QA  │  │DevOps│ │ Docs  │ │
│  │ 15 tasks │  │ 12 tasks │  │8 task│  │8 task│ │5 tasks│ │
│  └──────────┘  └──────────┘  └──────┘  └──────┘ └───────┘ │
│                                                             │
│  Review Gates: lint → test → build → integration → deploy   │
│  Merge Policy: 1 approval + CI green + no conflicts         │
└─────────────────────────────────────────────────────────────┘
```

### 6.2 Backend Workstream

**B1: Project Scaffold & Config**
- Description: Initialize FastAPI project with pyproject.toml, config management (pydantic-settings), health endpoint, CORS, error handlers
- Inputs/Dependencies: None (kickoff task)
- Files/Modules: `packages/api/pyproject.toml`, `src/main.py`, `src/config.py`
- Acceptance Criteria: `GET /health` returns 200; pydantic settings load from env; CORS configured; structured logging initialized
- Complexity: S

**B2: Database Models & Migrations**
- Description: Define SQLAlchemy models for trade_log, strategy_registry, audit_log, strategy_performance. Set up Alembic migrations.
- Inputs/Dependencies: B1
- Files/Modules: `src/models/`, `migrations/`
- Acceptance Criteria: `alembic upgrade head` runs cleanly; all tables created; `alembic downgrade` works
- Complexity: M

**B3: Event Bus (Redis Streams)**
- Description: Implement Redis Streams wrapper: publish, consume (consumer groups), stream creation, health check
- Inputs/Dependencies: B1
- Files/Modules: `src/events/bus.py`, `src/events/publishers.py`, `src/events/consumers.py`
- Acceptance Criteria: Publish/consume round-trip test passes; consumer group rebalancing works; backpressure handling tested
- Complexity: M

**B4: Market Data Service + Vendor Adapter**
- Description: Build market data service with abstract vendor interface. Implement paper/mock adapter with sample data. Normalize option chain to internal schema.
- Inputs/Dependencies: B1, B3
- Files/Modules: `src/services/market_data_service.py`, `src/adapters/data_vendor/`
- Acceptance Criteria: Mock adapter returns valid option chain; service publishes to `market.ticks` stream; stale data detection works
- Complexity: M

**B5: Feature Computation Engine**
- Description: Implement deterministic feature computation: Greeks (Black-Scholes), IV surface, PCR, OI changes, RSI, ATR, VWAP deviation, max pain
- Inputs/Dependencies: B4
- Files/Modules: `src/utils/greeks.py`, `src/utils/indicators.py`, `src/services/signal_engine.py` (feature part)
- Acceptance Criteria: All feature computations match reference values (provide test fixtures); edge cases handled (zero volume, missing strikes)
- Complexity: L

**B6: Signal Engine (Strategy Logic)**
- Description: Implement strategy execution framework. At least 2 sample strategies: iron condor and directional momentum. Strategy registry CRUD.
- Inputs/Dependencies: B5, B2
- Files/Modules: `src/services/signal_engine.py`, `src/services/strategy_registry.py`, `src/routers/strategies.py`
- Acceptance Criteria: Strategy registered via API; signal generated from feature vector; signal schema validated; at least 2 passing strategy test cases each
- Complexity: L

**B7: Risk Engine**
- Description: Implement deterministic risk engine with all risk rules: position limits, margin check, drawdown limit, correlation limit, time-of-day, portfolio delta limit
- Inputs/Dependencies: B2, B6
- Files/Modules: `src/services/risk_engine.py`, `src/routers/risk.py`
- Acceptance Criteria: Each risk rule has dedicated test; risk engine returns structured check results; REJECT is default on any error; veto power is absolute (no override path)
- Complexity: L

**B8: Broker Adapter (Paper Trading)**
- Description: Implement abstract broker interface and paper trading adapter. Order lifecycle: submit → fill (simulated latency + slippage) → cancel.
- Inputs/Dependencies: B2, B3
- Files/Modules: `src/adapters/broker/base.py`, `src/adapters/broker/paper.py`
- Acceptance Criteria: Paper orders fill with configurable slippage; order status transitions are correct; rate limiting simulated
- Complexity: M

**B9: Execution Gateway**
- Description: Order placement service that enforces risk-check-before-order invariant. Connects signal → risk check → broker adapter → fill tracking.
- Inputs/Dependencies: B7, B8
- Files/Modules: `src/services/execution_gateway.py`, `src/routers/orders.py`
- Acceptance Criteria: Cannot place order without passing risk check (test for bypass attempt); order lifecycle events published; fill updates portfolio
- Complexity: M

**B10: Portfolio Manager**
- Description: Position tracking, P&L computation (realized + unrealized), Greeks aggregation, margin tracking
- Inputs/Dependencies: B4, B8, B2
- Files/Modules: `src/services/portfolio_manager.py`, `src/routers/portfolio.py`
- Acceptance Criteria: Positions update on fill; P&L computed correctly (test with known prices); Greeks aggregate correctly; margin utilization tracked
- Complexity: M

**B11: WebSocket Gateway**
- Description: FastAPI WebSocket endpoint that bridges Redis Streams to frontend. Channel subscription model.
- Inputs/Dependencies: B3, B1
- Files/Modules: `src/routers/ws.py`
- Acceptance Criteria: Client subscribes to channels; receives events within 100ms of publish; handles disconnect/reconnect; authentication on connect
- Complexity: M

**B12: Admin API + Kill Switch**
- Description: Admin endpoints: kill switch, agent listing, config management, system health. Kill switch cancels orders, halts agents, publishes event.
- Inputs/Dependencies: B3, B9
- Files/Modules: `src/routers/admin.py`
- Acceptance Criteria: Kill switch cancels all pending orders; kill switch event published; agent retirement triggered; cannot place new orders after kill switch until reset
- Complexity: M

**B13: Audit Logging Middleware**
- Description: Middleware that logs every state-changing API call to audit_log table. Includes agent actions, risk decisions, order events.
- Inputs/Dependencies: B2, B1
- Files/Modules: `src/models/audit.py`, middleware in `src/main.py`
- Acceptance Criteria: All POST/PUT/DELETE requests logged; agent tool calls logged; logs include correlation_id; log query API works
- Complexity: S

**B14: Backtest Runner**
- Description: Offline backtest engine that runs strategy against historical data. Computes equity curve, Sharpe, drawdown, trade log.
- Inputs/Dependencies: B5, B6, B7
- Files/Modules: `src/services/backtest_runner.py`, `src/routers/strategies.py` (backtest endpoint)
- Acceptance Criteria: Backtest produces correct metrics for known historical data; handles missing data gracefully; respects risk rules in simulation
- Complexity: L

**B15: Integration Test Suite**
- Description: End-to-end tests: full trading cycle from tick ingestion to order fill to portfolio update. Uses paper broker and mock data.
- Inputs/Dependencies: B4–B14
- Files/Modules: `tests/integration/`
- Acceptance Criteria: Full cycle test passes; kill switch integration test passes; stale data → no trade test passes; risk rejection test passes
- Complexity: L

### 6.2 Frontend Workstream

**F1: Project Scaffold + Layout Shell**
- Description: Next.js 14 app with Tailwind, shadcn/ui. Implement layout: left sidebar (collapsible), top bar (logo, status indicators, kill switch button), central workspace.
- Inputs/Dependencies: None
- Files/Modules: `packages/dashboard/src/app/layout.tsx`, `src/components/layout/`
- Acceptance Criteria: Layout renders on all breakpoints; sidebar collapses; navigation works; dark mode toggle
- Complexity: M

**F2: API Client + WebSocket Hook**
- Description: Typed API client (fetch wrapper) and useWebSocket hook with auto-reconnect, channel subscription, connection status indicator.
- Inputs/Dependencies: F1, B11 (for testing)
- Files/Modules: `src/lib/api.ts`, `src/lib/ws.ts`, `src/hooks/useWebSocket.ts`
- Acceptance Criteria: API client handles errors gracefully; WebSocket reconnects on disconnect; connection status shown in top bar
- Complexity: M

**F3: Markets Module**
- Description: Option chain table (strikes × CE/PE with LTP, OI, IV, Greeks), IV chart, OI chart, regime indicator badge.
- Inputs/Dependencies: F2, B4
- Files/Modules: `src/app/markets/`, `src/components/markets/`
- Acceptance Criteria: Option chain renders with live updates; charts update on new data; regime badge shows current classification; loading/error states handled
- Complexity: L

**F4: Trade Module**
- Description: Active signals list, signal detail card (entry/SL/target), order form (pre-filled from signal), position table with live P&L, order history.
- Inputs/Dependencies: F2, B6, B9
- Files/Modules: `src/app/trade/`, `src/components/trade/`
- Acceptance Criteria: Signal cards show risk approval status; order form validates inputs; positions update in real-time; order history filterable
- Complexity: L

**F5: Analytics Module**
- Description: P&L chart (daily/cumulative), drawdown chart, regime timeline, strategy performance comparison table, win/loss distribution.
- Inputs/Dependencies: F2, B10, B14
- Files/Modules: `src/app/analytics/`, `src/components/analytics/`
- Acceptance Criteria: Charts render with historical + live data; date range selector works; strategy comparison table sortable; export to CSV
- Complexity: L

**F6: Alerts Module**
- Description: Alert feed (real-time), alert configuration panel (thresholds, channels), alert history with severity filters.
- Inputs/Dependencies: F2, B3
- Files/Modules: `src/app/alerts/`, `src/components/alerts/`
- Acceptance Criteria: New alerts appear instantly via WebSocket; severity color coding; filter by severity/time; configuration saves correctly
- Complexity: M

**F7: Admin Module**
- Description: Kill switch panel (big red button with confirmation), agent monitor (active agents, status, heartbeat), strategy manager (CRUD), system config.
- Inputs/Dependencies: F2, B12
- Files/Modules: `src/app/admin/`, `src/components/admin/`
- Acceptance Criteria: Kill switch requires confirmation dialog; agent status updates live; strategy activation/deactivation works; config changes persist
- Complexity: M

**F8: Shared Components**
- Description: DataTable (sortable, filterable), MetricCard, StatusBadge, LoadingSpinner, ErrorBoundary, ConfirmDialog, Toast notifications.
- Inputs/Dependencies: F1
- Files/Modules: `src/components/shared/`
- Acceptance Criteria: All components have Storybook stories (or equivalent); responsive; accessible (ARIA labels); dark mode compatible
- Complexity: M

**F9: State Management (Zustand + React Query)**
- Description: Global stores for: portfolio state, active signals, agent status, system config. React Query for server state with polling + WebSocket invalidation.
- Inputs/Dependencies: F2
- Files/Modules: `src/hooks/`, stores in `src/lib/`
- Acceptance Criteria: State updates propagate correctly; optimistic updates for order placement; stale data indicators; proper cache invalidation on WebSocket events
- Complexity: M

**F10: Real-Time Data Integration**
- Description: Connect all modules to live WebSocket feed. Ensure smooth updates without UI jank (virtualized lists, throttled updates).
- Inputs/Dependencies: F2, F3–F7
- Files/Modules: All module pages
- Acceptance Criteria: 10 updates/second handled without frame drops; reconnect doesn't lose state; fallback to polling if WebSocket unavailable
- Complexity: M

**F11: Responsive Design + Mobile**
- Description: Ensure all modules work on tablet and mobile. Sidebar becomes bottom nav on mobile. Charts resize correctly.
- Inputs/Dependencies: F3–F7
- Files/Modules: All component files
- Acceptance Criteria: Usable on 768px and 375px widths; no horizontal scroll; touch targets ≥ 44px; charts readable on mobile
- Complexity: M

**F12: Frontend Test Suite**
- Description: Component tests (React Testing Library), hook tests, integration tests (MSW for API mocking).
- Inputs/Dependencies: F3–F9
- Files/Modules: `packages/dashboard/tests/`
- Acceptance Criteria: >80% component coverage; all critical flows tested (place order, kill switch, alert config); no console errors in tests
- Complexity: M

### 6.2 QA Workstream

**Q1: Test Strategy & Fixtures**
- Description: Define test strategy document. Create shared test fixtures: sample option chains, feature vectors, signals, portfolio states.
- Inputs/Dependencies: None
- Files/Modules: `data/fixtures/`, `docs/test-strategy.md`
- Acceptance Criteria: Fixtures cover happy path + edge cases; test strategy document approved
- Complexity: S

**Q2: Risk Engine Fuzz Testing**
- Description: Property-based testing (Hypothesis) for risk engine. Test boundary conditions: exact limits, off-by-one, negative values, extreme prices.
- Inputs/Dependencies: B7
- Files/Modules: `packages/api/tests/test_risk_engine_fuzz.py`
- Acceptance Criteria: 1000+ generated test cases pass; no risk bypass found; edge cases documented
- Complexity: M

**Q3: Signal Engine Validation**
- Description: Validate signal engine against known historical scenarios. Ensure signals match expected outputs for reference data.
- Inputs/Dependencies: B6, Q1
- Files/Modules: `packages/api/tests/test_signal_validation.py`
- Acceptance Criteria: All reference scenarios produce correct signals; regression test suite established
- Complexity: M

**Q4: Agent Integration Tests**
- Description: Test agent spawn/retire lifecycle, tool calling, memory writes, error handling, timeout behavior.
- Inputs/Dependencies: B15, agent runtime
- Files/Modules: `packages/agents/tests/`
- Acceptance Criteria: Agent spawns on event; retires on timeout; tool calls are logged; memory writes conform to schema; errors don't crash supervisor
- Complexity: L

**Q5: End-to-End Trading Cycle**
- Description: Full E2E: dashboard triggers strategy activation → signal generated → risk approved → order placed → fill → portfolio updated → dashboard shows
- Inputs/Dependencies: B15, F10
- Files/Modules: `tests/e2e/`
- Acceptance Criteria: Full cycle completes in under 10 seconds (paper trading); all dashboard modules reflect correct state; audit trail complete
- Complexity: L

**Q6: Kill Switch Testing**
- Description: Test kill switch from all entry points: API, dashboard, Telegram. Verify orders cancelled, agents stopped, positions optionally flattened.
- Inputs/Dependencies: B12, F7
- Files/Modules: `tests/e2e/test_killswitch.py`
- Acceptance Criteria: Kill switch activates within 2 seconds; all pending orders confirmed cancelled; no new orders accepted; system recoverable after reset
- Complexity: M

**Q7: Load Testing**
- Description: Simulate high-frequency data updates (100 ticks/sec), multiple concurrent agents, dashboard with 10 simultaneous connections.
- Inputs/Dependencies: B15, F10
- Files/Modules: `tests/load/`
- Acceptance Criteria: System stable at 100 ticks/sec; no memory leaks over 1 hour; WebSocket doesn't drop connections; agent response time < 2 sec p95
- Complexity: L

**Q8: Security Audit Checklist**
- Description: Verify: no credentials in logs/memory, auth on all endpoints, rate limiting, input validation, SQL injection protection, WebSocket auth.
- Inputs/Dependencies: B13, B1
- Files/Modules: `docs/security-checklist.md`
- Acceptance Criteria: All checklist items verified; no credentials in any log output; all endpoints require auth; rate limits enforced
- Complexity: M

### 6.2 DevOps Workstream

**D1: Docker Setup**
- Description: Dockerfiles for api, dashboard, agents, plus docker-compose for dev environment with Redis, Postgres, all services.
- Inputs/Dependencies: B1, F1
- Files/Modules: `infra/docker/`, `docker-compose.dev.yml`
- Acceptance Criteria: `docker compose up` starts all services; health checks pass; hot reload works for dev
- Complexity: M

**D2: CI Pipeline**
- Description: GitHub Actions CI: lint (ruff + eslint), type check (mypy + tsc), unit tests, build check, docker build.
- Inputs/Dependencies: D1
- Files/Modules: `.github/workflows/ci.yml`
- Acceptance Criteria: CI runs on every PR; fails fast on lint errors; parallel test execution; <5 min total
- Complexity: M

**D3: Database Migration Pipeline**
- Description: Alembic migration runs in CI and on deploy. Migration validation: up + down tested.
- Inputs/Dependencies: B2, D2
- Files/Modules: `.github/workflows/`, `infra/scripts/migrate.sh`
- Acceptance Criteria: Migrations run in CI; rollback tested; no data loss on migration
- Complexity: S

**D4: Staging Environment**
- Description: Docker Compose config for staging VPS. Includes monitoring (Prometheus + Grafana), log aggregation.
- Inputs/Dependencies: D1
- Files/Modules: `docker-compose.stg.yml`, `infra/`
- Acceptance Criteria: Staging deploys via CI; monitoring dashboards show key metrics; logs queryable
- Complexity: M

**D5: Secrets Management**
- Description: Set up secrets management: env-based for dev, GitHub Secrets for CI, Vault/SOPS for staging/prod. Broker keys never in code.
- Inputs/Dependencies: D1
- Files/Modules: `.env.example`, CI config, docs
- Acceptance Criteria: No secrets in code or docker images; secrets rotation documented; `.env.example` has all keys (no values)
- Complexity: S

**D6: Monitoring & Alerting**
- Description: Prometheus scraping from FastAPI, Grafana dashboards for: trading metrics, agent performance, system health, LLM costs.
- Inputs/Dependencies: D4, B13
- Files/Modules: `infra/monitoring/`
- Acceptance Criteria: 4 Grafana dashboards deployed; alerts configured for: agent down, risk engine error, kill switch activated, high latency
- Complexity: M

**D7: Production Deployment Config**
- Description: Kubernetes manifests or Docker Swarm config for production. HPA for API, resource limits, liveness/readiness probes.
- Inputs/Dependencies: D4
- Files/Modules: `infra/k8s/`
- Acceptance Criteria: Deployment manifests pass `kubectl apply --dry-run`; resource limits set; probes configured; rolling update strategy defined
- Complexity: L

**D8: Disaster Recovery & Backup**
- Description: PostgreSQL backup strategy (pg_dump cron or WAL archiving), Redis persistence config, recovery runbook.
- Inputs/Dependencies: D4
- Files/Modules: `infra/scripts/`, `docs/runbook.md`
- Acceptance Criteria: Backup runs daily; restore tested; RTO < 1 hour documented; runbook covers common failure scenarios
- Complexity: M

### 6.2 Docs Workstream

**P1: Architecture Documentation**
- Description: Document system architecture, data flow, agent design, tool catalog (from this blueprint).
- Files/Modules: `docs/architecture.md`
- Complexity: M

**P2: API Reference**
- Description: Auto-generated OpenAPI docs + supplementary guide with examples for each endpoint.
- Files/Modules: `docs/api-reference.md`
- Complexity: S

**P3: Agent Design Guide**
- Description: Document agent roster, lifecycle, prompts, tool-use rules, memory rules. Guide for adding new agents.
- Files/Modules: `docs/agent-design.md`
- Complexity: M

**P4: Operations Runbook**
- Description: Runbook covering: deployment, kill switch procedure, adding new strategy, adding new broker, troubleshooting guide.
- Files/Modules: `docs/runbook.md`
- Complexity: M

**P5: Developer Onboarding**
- Description: Getting started guide, local dev setup, contribution guidelines, PR process.
- Files/Modules: `docs/getting-started.md`, `CONTRIBUTING.md`
- Complexity: S

### 6.3 Review Gates & Definition of Done

**Review Gates (applied to every PR):**

| Gate | Tool | Pass Criteria |
|------|------|--------------|
| Lint | ruff (Python) + eslint (TypeScript) | Zero errors |
| Type Check | mypy (Python) + tsc (TypeScript) | Zero errors |
| Unit Tests | pytest + vitest | All pass, coverage ≥ 80% on changed files |
| Build | docker build | Exits 0 |
| Integration Tests | pytest (on merge to main) | All pass |
| Security Scan | bandit (Python) + npm audit | No high/critical vulnerabilities |

**Merge Policy:**
- 1 approval required (from another workstream agent or human reviewer)
- All CI gates green
- No merge conflicts
- Commit message follows conventional commits (`feat:`, `fix:`, `test:`, `docs:`, `chore:`)

**Definition of Done (per task):**
1. Code written and passes all acceptance criteria
2. Unit tests added (≥ 80% coverage on new code)
3. Documentation updated if API/schema changes
4. No lint/type errors
5. PR reviewed and approved
6. CI green
7. Merged to main

---

## 7. Prompt Chain

### 7.1 Supervisor System Prompt

```
You are the Supervisor Agent of an agentic trading platform focused on Indian options markets (NIFTY/BANKNIFTY).

ROLE: You orchestrate sub-agents, route tasks, manage agent lifecycle, and provide strategic oversight. You NEVER make trading decisions or compute numbers yourself.

IRON RULES:
1. All numerical computation is done by TOOLS. You never calculate prices, Greeks, P&L, or risk metrics.
2. All execution and risk decisions are made by DETERMINISTIC CODE (RiskEngine, SignalEngine). You orchestrate, not decide.
3. If any data is missing or stale, default action is NO TRADE + raise alert.
4. The RiskEngine has absolute veto power. You cannot override it.
5. You cannot invent new tools. You can only compose existing tools via skills.

AVAILABLE SUB-AGENTS (you spawn/retire these):
- MarketDataAgent: regime classification from structured features
- StrategyAgent: strategy activation/deactivation suggestions
- RiskAgent: risk state summarization, rejection explanation
- ExecutionAgent: order placement workflow orchestration
- PortfolioAgent: portfolio state summarization
- PerformanceAgent: performance report generation
- AlertingAgent: alert composition and routing
- BacktestAgent: backtest orchestration and analysis

LIFECYCLE RULES:
- Spawn agent when: new instrument added, strategy activated, backtest requested, market opens
- Retire agent when: idle > 15 min, risk blocked (unresolvable), market closes, kill switch
- Max concurrent agents: 20 (configurable)
- Monitor heartbeats: 2 missed = auto-retire + alert

AVAILABLE SKILLS:
- analyze_market_regime
- generate_and_validate_signal
- execute_trade_cycle
- daily_performance_report
- run_strategy_backtest
- emergency_shutdown

ESCALATION:
- If a sub-agent reports confidence < 0.6, take over the task yourself.
- If you encounter an unknown situation, log it, raise alert, and default to NO ACTION.

OUTPUT FORMAT: Always respond with structured JSON:
{
  "action": "spawn_agent|retire_agent|delegate_task|escalate|alert|no_action",
  "target_agent": "agent_type",
  "task": { "skill": "skill_name", "params": {...} },
  "reasoning": "brief explanation",
  "priority": "critical|high|normal|low"
}
```

### 7.2 Sub-Agent System Prompts

**MarketDataAgent:**
```
You are the Market Data Agent. You analyze structured feature vectors to classify market regime.

ROLE: Receive pre-computed feature vectors (PCR, IV skew, OI changes, trend strength, volatility rank) and classify the current market regime.

ALLOWED CLASSIFICATIONS:
- trending_up: strong directional move upward
- trending_down: strong directional move downward
- ranging: sideways, low trend strength
- volatile: high ATR, rapid regime changes
- event_driven: unusual OI/IV patterns suggesting known event (expiry, earnings, policy)

RULES:
1. You ONLY classify from structured data. Never infer from news or sentiment.
2. Always output a confidence score (0.0–1.0).
3. If confidence < 0.6, flag for Supervisor escalation.
4. Never fabricate data points. If a feature is missing, report it.

TOOLS: fetch_option_chain, compute_features, read_memory, write_memory

OUTPUT FORMAT:
{
  "regime": "trending_up|trending_down|ranging|volatile|event_driven",
  "confidence": 0.85,
  "key_factors": ["high_pcr_1.4", "iv_skew_positive", "oi_buildup_25000CE"],
  "anomalies": [],
  "data_quality": "good|degraded|stale"
}
```

**StrategyAgent:**
```
You are the Strategy Agent. You suggest which strategies to activate or deactivate based on regime and historical performance.

ROLE: Given the current market regime and strategy registry (with performance metrics), recommend strategy changes.

RULES:
1. You SUGGEST only. Activation requires operator confirmation or Supervisor approval.
2. Base suggestions on: regime affinity match, recent performance (30d Sharpe, drawdown), and strategy capacity.
3. Never suggest activating a strategy that has no backtest data.
4. Provide clear rationale for each suggestion.

TOOLS: query_strategy_registry, read_memory, write_memory

OUTPUT FORMAT:
{
  "suggestions": [
    {
      "action": "activate|deactivate|adjust_params",
      "strategy_id": "iron_condor_v2",
      "rationale": "Regime is ranging with low volatility; iron condor performs well historically in this regime (30d Sharpe: 1.8)",
      "confidence": 0.78
    }
  ]
}
```

**RiskAgent:**
```
You are the Risk Agent. You summarize risk engine outputs in natural language and explain rejections.

ROLE: Take structured risk check results and produce human-readable explanations. You do NOT make risk decisions — the deterministic RiskEngine does that. You explain them.

RULES:
1. Never override or reinterpret risk decisions. The RiskEngine output is final.
2. Provide clear, actionable explanations for rejections.
3. Summarize overall portfolio risk state when asked.
4. Flag when risk utilization approaches limits (>80%).

TOOLS: check_risk (read-only), get_portfolio_state, read_memory, send_alert

OUTPUT FORMAT:
{
  "summary": "Trade rejected: position size of 5 lots would exceed NIFTY single-instrument limit (max 4 lots). Current exposure: 3 lots.",
  "risk_utilization": { "position_limit": "75%", "margin": "62%", "daily_loss": "30%" },
  "warnings": ["Approaching position limit on NIFTY"],
  "suggested_actions": ["Reduce NIFTY exposure before adding new positions"]
}
```

**ExecutionAgent:**
```
You are the Execution Agent. You orchestrate the order placement workflow.

ROLE: Take approved signals (must have passed RiskEngine), execute them via the place_order tool, and monitor fills.

IRON RULES:
1. NEVER place an order without a valid, recent risk approval (< 60 seconds old).
2. If the risk approval is stale or missing, REFUSE and alert.
3. Monitor fills with polling (max 10 attempts, 2s interval). If not filled, cancel and alert.
4. Report slippage for every filled order.

TOOLS: place_order, get_order_status, send_alert, write_memory

OUTPUT FORMAT:
{
  "order_id": "ord_123",
  "status": "filled|partial|cancelled|failed",
  "fill_price": 150.25,
  "slippage": 0.25,
  "execution_time_ms": 1200
}
```

**PortfolioAgent:**
```
You are the Portfolio Agent. You summarize portfolio state and generate P&L commentary.

ROLE: Produce natural-language summaries of current positions, Greeks exposure, P&L, and margin utilization.

RULES:
1. All numbers come from get_portfolio_state tool. Never estimate or calculate yourself.
2. Highlight positions with large unrealized P&L (positive or negative).
3. Flag Greeks imbalances (e.g., high net delta, negative theta exceeding threshold).

TOOLS: get_portfolio_state, read_memory, write_memory

OUTPUT FORMAT:
{
  "summary": "Portfolio has 5 active positions across NIFTY and BANKNIFTY. Net P&L: +₹12,450. Portfolio delta is slightly positive at +0.15, suggesting mild bullish bias.",
  "highlights": ["NIFTY 25000CE up ₹8,200 (unrealized)", "BANKNIFTY 51000PE down ₹2,100"],
  "greeks_note": "Net theta of -₹3,400/day. Consider time decay impact over weekend.",
  "margin_note": "62% margin utilized. Sufficient buffer for current positions."
}
```

**PerformanceAgent:**
```
You are the Performance Agent. You generate performance reports from structured trade data.

ROLE: Produce daily, weekly, and custom period performance summaries with actionable insights.

RULES:
1. All metrics come from read_memory and database queries. Never compute returns or ratios yourself.
2. Identify patterns: winning streaks, losing streaks, regime correlation.
3. Compare current performance to historical benchmarks.

TOOLS: read_memory, query_strategy_registry, write_memory, send_alert

OUTPUT FORMAT:
{
  "period": "2026-03-02",
  "summary": "3 trades executed. 2 winners, 1 loser. Net P&L: +₹5,200. Win rate: 67%. Best: NIFTY iron condor (+₹4,100). Iron condor strategies outperforming directional in current ranging regime.",
  "metrics": { "total_pnl": 5200, "trades": 3, "win_rate": 0.67, "sharpe_daily": 1.2 },
  "insights": ["Iron condor has 5-day winning streak", "Directional strategies underperforming — consider reducing allocation"]
}
```

**AlertingAgent:**
```
You are the Alerting Agent. You compose and route alerts based on system events.

ROLE: Receive alert triggers, compose clear messages, and route to appropriate channels.

RULES:
1. CRITICAL alerts always go to ALL channels (telegram + email).
2. WARNING alerts go to telegram only.
3. INFO alerts go to telegram only (can be muted by user config).
4. Keep messages concise: title + 2-3 lines max.
5. Include actionable next steps in every alert.

TOOLS: send_alert, read_memory

OUTPUT FORMAT:
{
  "severity": "CRITICAL",
  "title": "⚠️ Risk Limit Breach: Daily Loss Limit at 85%",
  "body": "Daily loss has reached ₹17,000 (85% of ₹20,000 limit). 2 open positions with ₹3,500 unrealized loss.\nAction: Review positions or activate kill switch.",
  "channels": ["telegram", "email"],
  "metadata": { "current_loss": 17000, "limit": 20000 }
}
```

**BacktestAgent:**
```
You are the Backtest Agent. You orchestrate backtests and summarize results.

ROLE: Run backtests via the run_backtest tool, compare results across strategies, and produce clear summaries.

RULES:
1. Always report: total return, Sharpe ratio, max drawdown, win rate, total trades.
2. Compare against benchmark (buy-and-hold underlying) when possible.
3. Flag if backtest period is too short (< 30 trading days) or doesn't include volatility events.
4. Never claim backtest results predict future performance.

TOOLS: run_backtest, query_strategy_registry, read_memory, write_memory

OUTPUT FORMAT:
{
  "backtest_id": "bt_20260302_001",
  "strategy": "iron_condor_v2",
  "period": "2025-01-01 to 2025-12-31",
  "summary": "252 trading days tested. 180 trades. Win rate: 72%. Total return: 34.2%. Sharpe: 1.9. Max drawdown: 8.3%. Strategy outperformed in ranging regimes but underperformed during Aug/Sep volatile period.",
  "recommendation": "Suitable for activation in current ranging regime. Consider pausing during high-volatility events.",
  "disclaimer": "Past performance does not guarantee future results."
}
```

### 7.3 Antigravity Agent Prompts

**FrontendAgent (Antigravity):**
```
You are the Frontend Development Agent. You build the React/Next.js dashboard for the agentic trading platform.

STACK: Next.js 14 (App Router), TypeScript, Tailwind CSS, shadcn/ui, Recharts, Zustand, React Query.

CONSTRAINTS:
- All data comes from the API or WebSocket. Never hardcode trading data.
- Use TypeScript strictly (no `any` types except at API boundaries with validation).
- Components must be responsive (mobile-first).
- Use shadcn/ui components as base; customize with Tailwind.
- Real-time updates via WebSocket; fallback to polling.
- Every component must handle: loading, error, empty states.

REVIEW REQUIREMENTS:
- ESLint clean
- TypeScript strict mode passes
- Component tests with React Testing Library
- No console errors/warnings
```

**BackendAgent (Antigravity):**
```
You are the Backend Development Agent. You build the FastAPI services for the trading platform.

STACK: FastAPI, Python 3.11+, SQLAlchemy 2.0, Redis (aioredis), Pydantic v2, Alembic.

IRON RULES:
- RiskEngine is DETERMINISTIC code. Never use LLM for risk decisions.
- SignalEngine is DETERMINISTIC code. Strategy logic is Python, not LLM.
- All inputs validated with Pydantic models.
- All state-changing operations logged to audit_log.
- Broker credentials never logged, never in database, never in responses.

REVIEW REQUIREMENTS:
- ruff lint clean
- mypy strict passes
- pytest coverage ≥ 80%
- All risk rules have dedicated tests
```

**QAAgent (Antigravity):**
```
You are the QA Agent. You ensure the trading platform is correct, reliable, and secure.

FOCUS AREAS:
1. Risk engine: must never allow bypass. Fuzz test with Hypothesis.
2. Signal engine: must match reference outputs for known inputs.
3. Kill switch: must work from all entry points within 2 seconds.
4. Data staleness: system must refuse to trade on stale data.
5. Agent lifecycle: spawn/retire/timeout all correct.
6. Security: no credentials in logs, auth on all endpoints.

TEST PYRAMID:
- Unit tests: 80% coverage minimum
- Integration tests: all service-to-service flows
- E2E tests: full trading cycles
- Load tests: 100 ticks/sec sustained
- Security audit: OWASP checklist
```

**DevOpsAgent (Antigravity):**
```
You are the DevOps Agent. You build the infrastructure, CI/CD, and monitoring for the platform.

STACK: Docker, Docker Compose, GitHub Actions, Prometheus, Grafana, PostgreSQL, Redis.

PRIORITIES:
1. Dev environment: `docker compose up` must work in < 2 minutes.
2. CI: lint → test → build → security scan. < 5 minutes.
3. Staging: mirrors production topology.
4. Monitoring: 4 dashboards (trading, agents, system, LLM costs).
5. Secrets: zero secrets in code or images.
6. Backup: daily PostgreSQL backup, tested restore.
```

### 7.4 Tool-Use Rules and JSON Schemas

**Universal Tool-Use Rules (applied to ALL agents):**
```
TOOL-USE RULES:
1. You may ONLY call tools listed in your tool catalog. No inventing tools.
2. Every tool call must use the exact JSON schema specified.
3. Tool outputs are authoritative. Do not modify or reinterpret numerical results.
4. If a tool returns an error, report it truthfully. Do not retry more than once unless explicitly allowed by the skill definition.
5. Log every tool call with inputs and outputs (via write_memory or audit system).
6. Never chain more than 5 tool calls without reporting intermediate results to Supervisor.
7. If you need a tool that doesn't exist, report to Supervisor. Do not approximate with LLM reasoning.
```

**Tool Call JSON Schema (for LLM function calling):**
```json
{
  "type": "function",
  "function": {
    "name": "fetch_option_chain",
    "description": "Retrieves current option chain for a given underlying",
    "parameters": {
      "type": "object",
      "properties": {
        "underlying": { "type": "string", "enum": ["NIFTY", "BANKNIFTY"] },
        "expiry": { "type": "string", "format": "date" }
      },
      "required": ["underlying", "expiry"]
    }
  }
}
```

*(Similar schemas defined for all 12 tools in the catalog — omitted for brevity but each follows the same structure with the inputs/outputs defined in Section 3.3.)*

### 7.5 Memory Write Rules

```
MEMORY WRITE RULES (enforced by write_memory tool):

ALLOWED:
- Structured feature vectors (working memory, TTL 5 min)
- Trade signals and outcomes (session memory, TTL 1 day)
- Regime classifications with timestamps (session + long-term)
- Strategy performance metrics (long-term)
- Agent lifecycle events (long-term)
- Backtest results (long-term)
- Risk decision logs (long-term)
- Alert history (long-term)

FORBIDDEN (tool will reject):
- Broker API keys, secrets, tokens, passwords
- Raw order book / tick-by-tick data (use dedicated time-series store)
- Personally identifiable information (PII)
- Unstructured LLM conversation transcripts (unless ENABLE_TRANSCRIPT_LOGGING=true)
- Other users' data
- Executable code or scripts

VALIDATION:
- All memory writes are schema-validated before storage.
- write_memory tool checks for forbidden patterns (regex: API key formats, etc.)
- Long-term writes require a "category" field from approved list.
- Maximum value size: 1MB per key.
```

---

## 8. Worked Example: Single Trading Cycle

### Scenario
**Time:** 10:30 AM IST, March 2, 2026  
**Market:** NIFTY spot at 24,850  
**Active strategy:** `iron_condor_v2` (on NIFTY weekly expiry)  
**Current positions:** 1 lot NIFTY 25200CE sold, 1 lot NIFTY 24500PE sold (from previous day)

### Step-by-Step Execution

**Step 1: Market Data Ingestion**
```
[MarketDataService] Receives tick from data vendor adapter
→ Publishes to Redis Stream: market.ticks
  { "underlying": "NIFTY", "spot": 24850, "timestamp": "2026-03-02T10:30:00Z" }
```

**Step 2: Supervisor Receives Tick Event**
```
[SupervisorAgent] Detects market.ticks event for NIFTY
→ Delegates to MarketDataAgent (already active for NIFTY)
  Action: { "action": "delegate_task", "target_agent": "MarketDataAgent_NIFTY",
            "task": { "skill": "analyze_market_regime", "params": { "underlying": "NIFTY", "expiry": "2026-03-06" } } }
```

**Step 3: MarketDataAgent Executes Skill**
```
[MarketDataAgent_NIFTY]
→ Tool call: fetch_option_chain({ "underlying": "NIFTY", "expiry": "2026-03-06" })
  Returns: { chain: [ { strike: 24500, ce_ltp: 385, pe_ltp: 42, ce_oi: 1200000, pe_oi: 890000, ce_iv: 14.2, pe_iv: 13.8 }, ... 40 strikes ... ], stale: false }

→ Tool call: compute_features({ chain: <above>, underlying_price: 24850 })
  Returns: { pcr: 0.89, iv_skew: 0.4, max_pain: 24800, vwap_deviation: 0.12, atr_14: 180, rsi_14: 52, regime_features: { volatility_rank: 0.35, trend_strength: 0.22, mean_reversion_score: 0.71 } }

→ LLM Classification:
  Output: { "regime": "ranging", "confidence": 0.84, "key_factors": ["low_trend_strength_0.22", "high_mean_reversion_0.71", "rsi_neutral_52", "low_volatility_rank_0.35"], "anomalies": [], "data_quality": "good" }

→ Tool call: write_memory({ layer: "session", key: "regime_NIFTY_20260302_1030", data: { regime: "ranging", confidence: 0.84 } })
```

**Step 4: Supervisor Routes to StrategyAgent**
```
[SupervisorAgent] Receives regime classification: "ranging" with 0.84 confidence
→ Delegates to StrategyAgent
  Task: Check if iron_condor_v2 aligns with current regime

[StrategyAgent]
→ Tool call: query_strategy_registry({ filter: { underlying: "NIFTY", active_only: true } })
  Returns: { strategies: [{ id: "iron_condor_v2", regime_affinity: ["ranging", "low_volatile"], active: true, performance_30d: { return: 8.2, sharpe: 1.8 } }] }

→ Output: { "suggestions": [{ "action": "maintain", "strategy_id": "iron_condor_v2", "rationale": "Current ranging regime aligns with iron condor affinity. 30d Sharpe of 1.8 is strong. No change recommended.", "confidence": 0.88 }] }
```

**Step 5: Signal Generation**
```
[SignalEngine — deterministic code, not LLM]
→ Runs iron_condor_v2 logic on features
→ Detects: current short positions are within range, but PE leg is approaching adjustment trigger (spot at 24850, PE sold at 24500, threshold = 300 pts)
→ Generates signal:
  { "signal": "BUY", "instrument": "NIFTY26MAR24400PE", "option_type": "PE", "qty": 1,
    "entry_price": 28.50, "stop_loss": null, "target": null,
    "confidence_score": 0.75, "rationale_data": { "adjustment": "roll_down_pe_hedge",
    "current_pe_strike": 24500, "new_hedge_strike": 24400 } }
→ Publishes to signals.generated
```

**Step 6: Risk Check**
```
[RiskEngine — deterministic code]
→ Input: signal + portfolio_state + risk_params
→ Checks:
  ✅ Position size: 1 lot (within limit of 4)
  ✅ Margin: ₹15,000 required, ₹85,000 available
  ✅ Daily loss: ₹2,100 current (limit: ₹20,000)
  ✅ Drawdown: 3.2% (limit: 10%)
  ✅ Time of day: 10:30 AM (within trading hours)
  ✅ Correlation: within limits
→ Output: { "approved": true, "risk_score": 0.25, "checks": [all passed], "modified_signal": null }
→ Publishes to risk.decisions
```

**Step 7: RiskAgent Summarizes**
```
[RiskAgent]
→ Output: { "summary": "Trade approved. Adding PE hedge at 24400 strike. Low risk score (0.25). All 6 risk checks passed. Margin utilization will increase from 53% to 62%.", "risk_utilization": { "position_limit": "50%", "margin": "62%", "daily_loss": "10%" } }
```

**Step 8: Execution**
```
[ExecutionAgent]
→ Verifies risk approval timestamp: 2026-03-02T10:30:15Z (12 seconds ago — valid)
→ Tool call: place_order({ instrument: "NIFTY26MAR24400PE", side: "BUY", qty: 1, order_type: "LIMIT", price: 28.50, tag: "IC_adj_20260302" })
  Returns: { order_id: "ord_20260302_001", status: "SUBMITTED", broker_ref: "ZRD_123456" }

→ Tool call: get_order_status({ order_id: "ord_20260302_001" })  [attempt 1, 2s later]
  Returns: { status: "OPEN", filled_qty: 0 }

→ Tool call: get_order_status({ order_id: "ord_20260302_001" })  [attempt 2, 4s later]
  Returns: { status: "FILLED", filled_qty: 1, avg_fill_price: 28.75 }

→ Output: { "order_id": "ord_20260302_001", "status": "filled", "fill_price": 28.75, "slippage": 0.25, "execution_time_ms": 4200 }
```

**Step 9: Portfolio Update**
```
[PortfolioAgent]
→ Tool call: get_portfolio_state({ include_greeks: true, include_pnl: true })
  Returns: {
    positions: [
      { instrument: "NIFTY26MAR25200CE", qty: -1, avg_price: 45.00, ltp: 38.50, pnl: 650 },
      { instrument: "NIFTY26MAR24500PE", qty: -1, avg_price: 62.00, ltp: 42.00, pnl: 2000 },
      { instrument: "NIFTY26MAR24400PE", qty: 1, avg_price: 28.75, ltp: 28.50, pnl: -25 }
    ],
    total_pnl: 2625,
    margin_used: 62000,
    margin_available: 38000,
    portfolio_greeks: { delta: 0.08, gamma: -0.002, theta: -3400, vega: -120 }
  }

→ Output: { "summary": "Portfolio updated with PE hedge. 3 active positions. Total unrealized P&L: +₹2,625. Iron condor is profitable with PE hedge added for protection. Net delta near-neutral at +0.08." }
```

**Step 10: Dashboard Update**
```
[WebSocket Gateway]
→ Publishes to connected dashboard clients:
  Channel: portfolio.updated → full portfolio state
  Channel: orders.filled → order fill details
  Channel: signals.generated → signal + outcome

[Dashboard renders:]
  - Trade module: new position appears in position table
  - Markets module: signal indicator on option chain
  - Analytics module: P&L chart updates
  - Admin module: agent activity log updates
```

**Step 11: Memory Write**
```
[write_memory calls:]
1. Session memory: { key: "trade_20260302_001", data: { signal, risk_decision, order, fill, slippage, portfolio_impact } }
2. Long-term memory: Appended to trade_log table via audit system
3. Working memory: Updated current positions cache (TTL 5 min)
```

**Step 12: Alert**
```
[AlertingAgent]
→ Tool call: send_alert({ severity: "INFO", channel: "telegram", title: "🔄 IC Adjustment Executed", body: "Bought 1 lot NIFTY 24400PE @ ₹28.75 (hedge adjustment). Portfolio P&L: +₹2,625. Margin: 62%." })
```

### Cycle Summary

| Step | Actor | Tool/Action | Duration |
|------|-------|-------------|----------|
| 1 | MarketDataService | Tick ingestion | ~50ms |
| 2 | Supervisor | Task routing | ~200ms (LLM) |
| 3 | MarketDataAgent | 2 tools + LLM classification | ~800ms |
| 4 | StrategyAgent | 1 tool + LLM suggestion | ~500ms |
| 5 | SignalEngine | Deterministic signal gen | ~20ms |
| 6 | RiskEngine | Deterministic risk check | ~10ms |
| 7 | RiskAgent | LLM summarization | ~300ms |
| 8 | ExecutionAgent | Order + 2 status polls | ~4500ms |
| 9 | PortfolioAgent | 1 tool + LLM summary | ~400ms |
| 10 | WebSocket | Dashboard push | ~10ms |
| 11 | Memory | 3 writes | ~50ms |
| 12 | AlertingAgent | 1 tool | ~200ms |
| **Total** | | | **~7 seconds** |

---

## Appendix A: Design Improvements Over Original Spec

After thorough analysis of the requirements document, these enhancements were incorporated:

1. **Explicit separation of LLM-as-orchestrator vs code-as-executor** — The original spec mentions this as a principle, but the implementation here makes it structural: every tool that touches money is a pure Python function. LLM agents receive tool outputs as immutable facts.

2. **Skill abstraction layer** — Rather than agents composing raw tool chains ad-hoc, skills are pre-validated workflows. This prevents agents from calling tools in incorrect order (e.g., placing order before risk check).

3. **Risk approval staleness check** — ExecutionAgent verifies risk approval is < 60 seconds old before placing order. This prevents stale approvals from being used after market conditions change.

4. **Heartbeat-based agent health monitoring** — The original spec mentions idle timeout but not health monitoring. Heartbeats catch crashed agents that would otherwise appear active.

5. **Circuit breaker on LLM provider** — If Groq returns 3 consecutive errors within 60 seconds, circuit breaker opens and routes to local Ollama. This prevents agent stalls during API outages.

6. **Correlation ID propagation** — Every trading cycle gets a unique ID that flows through all tools, events, and logs. This is critical for post-trade analysis and debugging.

7. **Memory schema validation** — Rather than trusting agents to write correctly, the `write_memory` tool validates against schemas and rejects malformed or forbidden data at the tool level.

8. **Backpressure on event bus** — If consumers fall behind on Redis Streams, the system pauses signal generation rather than queueing stale signals. Stale signals in options markets are dangerous.

9. **Paper trading as first-class citizen** — The broker adapter pattern makes paper trading identical in code path to live trading, ensuring thorough testing before going live.

10. **SEBI compliance awareness** — Explicit notes on algorithmic trading regulations, record-keeping requirements, and data residency that were implied but not detailed in the original spec.

---

*End of Document*
