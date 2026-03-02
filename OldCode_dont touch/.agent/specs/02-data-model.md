
# STROM — Data Model (PostgreSQL) (M0–M2)

All timestamps are UTC (timestamptz). IDs are UUID v4 unless stated otherwise.

## 1) Tables

### users
- id (uuid, pk)
- email (text, unique, not null)
- created_at (timestamptz, not null, default now())

### agents
- id (uuid, pk)
- user_id (uuid, fk users.id, not null)
- name (text, not null)
- mode (text, not null)  -- 'paper' in M0–M2; 'live' reserved
- frequency_seconds (int, not null) -- minimum 1
- universe (jsonb, not null) -- list of instrument symbols (canonical strings)
- strategy_ids (jsonb, not null) -- list of strategy IDs (UUID strings) from strategies table
- risk_profile (jsonb, not null) -- see RiskProfile schema below
- capital (numeric(18,2), not null) -- paper capital allocation
- is_enabled (boolean, not null, default false)
- status (text, not null, default 'CREATED') -- from Agent state machine
- created_at (timestamptz, not null, default now())
- updated_at (timestamptz, not null, default now())

Indexes:
- idx_agents_user_id (user_id)
- idx_agents_enabled (is_enabled)

### agent_runs
- id (uuid, pk)
- agent_id (uuid, fk agents.id, not null)
- tick_time (timestamptz, not null) -- when scheduler triggered
- started_at (timestamptz, not null)
- completed_at (timestamptz, null)
- status (text, not null) -- 'STARTED' | 'COMPLETED' | 'FAILED'
- error_message (text, null)
- created_at (timestamptz, not null, default now())

Index:
- idx_agent_runs_agent_time (agent_id, tick_time desc)

### market_prices (M1+ optional persistence)
- id (bigserial, pk)
- symbol (text, not null)
- ts (timestamptz, not null)
- price (numeric(18,6), not null)
- source (text, not null, default 'sim')
Index:
- idx_market_prices_symbol_ts (symbol, ts desc)

### strategies (predefined catalog)
- id (uuid, pk)
- key (text, unique, not null) -- e.g., 'ema_crossover'
- name (text, not null)
- description (text, not null)
- params_schema (jsonb, not null) -- JSON schema for parameters
- created_at (timestamptz, not null, default now())

### agent_strategy_params
- id (uuid, pk)
- agent_id (uuid, fk agents.id, not null)
- strategy_id (uuid, fk strategies.id, not null)
- params (jsonb, not null) -- validated against strategies.params_schema
Unique:
- uq_agent_strategy (agent_id, strategy_id)

### signals
- id (uuid, pk)
- agent_run_id (uuid, fk agent_runs.id, not null)
- agent_id (uuid, fk agents.id, not null)
- symbol (text, not null)
- side (text, not null) -- 'BUY' | 'SELL'
- confidence (numeric(5,4), not null) -- 0..1
- rationale (jsonb, not null) -- structured explanation (non-LLM in M0–M2)
- created_at (timestamptz, not null, default now())

Index:
- idx_signals_agent_created (agent_id, created_at desc)

### orders
- id (uuid, pk)
- agent_id (uuid, fk agents.id, not null)
- agent_run_id (uuid, fk agent_runs.id, not null)
- symbol (text, not null)
- side (text, not null) -- BUY|SELL
- qty (numeric(18,6), not null)
- order_type (text, not null) -- 'MARKET' only in M0–M2
- intent_idempotency_key (text, not null) -- unique key
- status (text, not null) -- 'INTENT'|'FILLED'|'REJECTED'
- requested_price (numeric(18,6), null)
- filled_price (numeric(18,6), null)
- filled_qty (numeric(18,6), null)
- fees (numeric(18,6), not null, default 0)
- reject_reason (text, null)
- created_at (timestamptz, not null, default now())

Unique:
- uq_orders_idempotency (intent_idempotency_key)

Index:
- idx_orders_agent_created (agent_id, created_at desc)

### trades
- id (uuid, pk)
- order_id (uuid, fk orders.id, not null)
- agent_id (uuid, fk agents.id, not null)
- symbol (text, not null)
- side (text, not null)
- qty (numeric(18,6), not null)
- price (numeric(18,6), not null)
- ts (timestamptz, not null)
- created_at (timestamptz, not null, default now())

Index:
- idx_trades_agent_ts (agent_id, ts desc)

### positions
- id (uuid, pk)
- agent_id (uuid, fk agents.id, not null)
- symbol (text, not null)
- net_qty (numeric(18,6), not null)
- avg_price (numeric(18,6), not null)
- updated_at (timestamptz, not null, default now())

Unique:
- uq_positions_agent_symbol (agent_id, symbol)

### pnl_snapshots
- id (uuid, pk)
- agent_id (uuid, fk agents.id, not null)
- ts (timestamptz, not null)
- equity (numeric(18,2), not null)
- realized_pnl (numeric(18,2), not null)
- unrealized_pnl (numeric(18,2), not null)
- drawdown (numeric(18,4), not null, default 0)
- created_at (timestamptz, not null, default now())

Index:
- idx_pnl_agent_ts (agent_id, ts desc)

---

## 2) JSON Schemas (stored in jsonb fields)

### universe (agents.universe)
```json
{
  "symbols": ["NSE:NIFTY50-INDEX", "NSE:BANKNIFTY-INDEX"]
}
```

### risk_profile (agents.risk_profile)
```json
{
  "max_risk_per_trade_pct": 1.0,
  "max_daily_loss_pct": 3.0,
  "max_open_positions": 3,
  "cooldown_seconds": 30,
  "max_notional_exposure_pct": 100.0
}
```

### signal.rationale (signals.rationale)
```json
{
  "strategy_key": "ema_crossover",
  "inputs": {"ema_fast": 9, "ema_slow": 21},
  "features": {"ema_fast": 201.12, "ema_slow": 199.87},
  "decision": {"rule": "fast_crosses_above_slow"}
}
```
