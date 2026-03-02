# SKILLS.md — Agentic Trading Platform · Skill Library & Tool Catalog

> Paste this as context for any task that involves agent implementation, tool development, or skill creation.

---

## Tool Catalog (Deterministic — No LLM)

Every tool is a Python async function with strict Pydantic input/output schemas. Agents call tools via structured JSON.

### Tool Registry Pattern
```python
from typing import Any, Callable
from pydantic import BaseModel

class ToolRegistry:
    _tools: dict[str, Callable] = {}

    @classmethod
    def register(cls, name: str):
        def decorator(func: Callable):
            cls._tools[name] = func
            return func
        return decorator

    @classmethod
    async def execute(cls, name: str, params: dict) -> dict:
        if name not in cls._tools:
            return {"error": "TOOL_NOT_FOUND", "tool": name}
        try:
            return await cls._tools[name](**params)
        except Exception as e:
            return {"error": "TOOL_ERROR", "detail": str(e)}
```

### Tool Definitions

| # | Tool Name | Inputs | Outputs | Failure Mode | Used By |
|---|-----------|--------|---------|-------------|---------|
| 1 | `fetch_option_chain` | underlying, expiry | timestamp, chain[], stale flag | DATA_STALE, VENDOR_TIMEOUT, MARKET_CLOSED | MarketDataAgent |
| 2 | `compute_features` | chain, underlying_price | pcr, iv_skew, max_pain, oi_changes, regime_features | INSUFFICIENT_DATA, COMPUTATION_ERROR | MarketDataAgent |
| 3 | `evaluate_signal` | strategy_id, features, positions, params | signal, instrument, strike, qty, entry/sl/target | STRATEGY_NOT_FOUND, NO_SIGNAL | SignalEngine (code) |
| 4 | `check_risk` | signal, portfolio_state, risk_params | approved, risk_score, checks[], modified_signal | RISK_ENGINE_ERROR → defaults to REJECT | RiskEngine (code) |
| 5 | `place_order` | instrument, side, qty, order_type, price, tag | order_id, status, broker_ref | BROKER_TIMEOUT, INSUFFICIENT_MARGIN | ExecutionAgent |
| 6 | `get_order_status` | order_id | status, filled_qty, avg_fill_price | ORDER_NOT_FOUND, BROKER_TIMEOUT | ExecutionAgent |
| 7 | `get_portfolio_state` | include_greeks, include_pnl | positions[], total_pnl, margin, portfolio_greeks | PORTFOLIO_SYNC_ERROR | PortfolioAgent |
| 8 | `run_backtest` | strategy_id, dates, params, capital | summary metrics, equity_curve, trades | INSUFFICIENT_HISTORY, STRATEGY_ERROR | BacktestAgent |
| 9 | `write_memory` | layer, key, data, ttl | stored, key | MEMORY_WRITE_FAILED, SCHEMA_VIOLATION | All agents |
| 10 | `read_memory` | layer, key | found, data, timestamp | MEMORY_READ_FAILED | All agents |
| 11 | `send_alert` | severity, channel, title, body, metadata | sent, channel, timestamp | CHANNEL_UNAVAILABLE, RATE_LIMITED | AlertingAgent |
| 12 | `query_strategy_registry` | filter (underlying, regime, active) | strategies[] with metadata | REGISTRY_ERROR | StrategyAgent |

---

## Skill Library (Validated Tool Chains)

A skill is a pre-validated sequence of tool calls with validation between steps. Agents invoke skills, not raw tool chains.

### Skill 1: `analyze_market_regime`
```
Purpose: Fetch data → compute features → classify regime
Steps:
  1. fetch_option_chain(underlying, expiry)
     VALIDATE: chain.stale == false (else ABORT → alert)
  2. compute_features(chain, underlying_price)
     VALIDATE: no null values in regime_features (else ABORT)
  3. [LLM] classify from features → one of: trending_up, trending_down, ranging, volatile, event_driven
     VALIDATE: confidence >= 0.6 (else escalate to Supervisor)
Output: { features, regime, confidence }
```

### Skill 2: `generate_and_validate_signal`
```
Purpose: Run strategy → validate through risk engine
Steps:
  1. evaluate_signal(strategy_id, features, positions, params)
     VALIDATE: signal != NO_SIGNAL
  2. check_risk(signal, portfolio_state, risk_params)
     VALIDATE: all risk checks enumerated, no silent failures
  3. [LLM] explain signal + risk result in natural language
If risk rejected: LOG reason, DO NOT proceed to execution
Output: { signal, risk_approved, explanation }
```

### Skill 3: `execute_trade_cycle`
```
Purpose: Place order → monitor fill → update portfolio
Steps:
  1. place_order(instrument, side, qty, order_type, price)
     VALIDATE: must have valid risk approval < 60 seconds old
  2. [POLL] get_order_status(order_id) — max 10 attempts, 2s interval
     VALIDATE: filled within timeout (else cancel + alert)
  3. get_portfolio_state(include_greeks=true, include_pnl=true)
  4. write_memory("session", trade_record)
  5. send_alert(severity="INFO", ...)
Output: { order, fill, portfolio_snapshot }
```

### Skill 4: `daily_performance_report`
```
Purpose: Summarize day's trading activity
Steps:
  1. read_memory("session", today_trades)
  2. get_portfolio_state(include_pnl=true)
  3. [LLM] generate summary (PerformanceAgent)
     VALIDATE: P&L in summary matches portfolio state
  4. write_memory("long_term", daily_summary)
  5. send_alert(severity="INFO", channel="telegram")
Output: { summary_text, metrics }
```

### Skill 5: `run_strategy_backtest`
```
Purpose: Backtest and compare strategy performance
Steps:
  1. query_strategy_registry(filter)
  2. run_backtest(strategy_id, dates, params, capital)
     VALIDATE: min 30 trading days of data
  3. read_memory("long_term", historical_performance)
  4. [LLM] compare and summarize (BacktestAgent)
  5. write_memory("long_term", backtest_result)
Output: { backtest_results, comparison, recommendation }
```

### Skill 6: `emergency_shutdown`
```
Purpose: Kill switch — halt everything
Steps:
  1. Broadcast system.killswitch event on Redis
  2. Cancel ALL pending orders (loop with confirmation)
  3. [Optional] Flatten all positions (if configured)
  4. Retire ALL agents
  5. send_alert(CRITICAL, ["telegram", "email"])
  6. write_memory("long_term", killswitch event)
VALIDATE: all orders confirmed cancelled, all agents confirmed retired
Output: { cancelled_orders, flattened_positions, agents_retired }

### Skill 7: `validate_test_fixtures`
```
Purpose: Ensure consistency between models and test data
Steps:
  1. Load all JSON files from data/fixtures/
  2. Import models from src.models
  3. Validate each file against its corresponding Pydantic model
  4. Report validation status
Output: { all_passed: true/false, failures: [] }
```
```

---

## Agent Base Class Pattern

```python
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
import asyncio

class BaseAgent(ABC):
    def __init__(self, agent_id: str, agent_type: str, model: str = "llama-3.1-8b-instant"):
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.model = model
        self.state = "SPAWNING"
        self.last_activity = datetime.utcnow()
        self.last_heartbeat = datetime.utcnow()

    async def start(self):
        self.state = "ACTIVE"
        asyncio.create_task(self._heartbeat_loop())

    async def _heartbeat_loop(self):
        while self.state in ("ACTIVE", "IDLE"):
            await self._publish_heartbeat()
            self.last_heartbeat = datetime.utcnow()
            await asyncio.sleep(30)

    def touch(self):
        """Call on every task to reset idle timer."""
        self.last_activity = datetime.utcnow()
        if self.state == "IDLE":
            self.state = "ACTIVE"

    @property
    def is_idle(self) -> bool:
        return (datetime.utcnow() - self.last_activity) > timedelta(minutes=5)

    @property
    def should_retire(self) -> bool:
        return (datetime.utcnow() - self.last_activity) > timedelta(minutes=15)

    async def retire(self):
        self.state = "RETIRED"
        await self._cleanup()

    @abstractmethod
    async def handle_task(self, task: dict) -> dict:
        """Process a task. Must be implemented by each agent."""
        pass

    @abstractmethod
    async def _cleanup(self):
        """Cleanup resources on retirement."""
        pass

    async def _publish_heartbeat(self):
        """Publish heartbeat to agents.lifecycle stream."""
        # Redis publish implementation
        pass
```

---

## Memory Layer Implementation Pattern

```python
# Working Memory (Redis, TTL 5 min)
class WorkingMemory:
    async def set(self, agent_id: str, key: str, data: dict, ttl: int = 300):
        validated = self._validate_schema(data)
        self._check_forbidden(validated)
        await redis.setex(f"wm:{agent_id}:{key}", ttl, json.dumps(validated))

    async def get(self, agent_id: str, key: str) -> dict | None:
        raw = await redis.get(f"wm:{agent_id}:{key}")
        return json.loads(raw) if raw else None

# Session Memory (Redis, TTL 1 day)
class SessionMemory:
    async def append(self, date: str, key: str, data: dict):
        validated = self._validate_schema(data)
        self._check_forbidden(validated)
        await redis.rpush(f"sm:session:{date}:{key}", json.dumps(validated))
        await redis.expire(f"sm:session:{date}:{key}", 86400)

# Long-Term Memory (PostgreSQL)
class LongTermMemory:
    async def write(self, category: str, data: dict):
        validated = self._validate_schema(data)
        self._check_forbidden(validated)
        # Insert into appropriate PostgreSQL table based on category
```

---

## Model Routing Logic

```python
class ModelRouter:
    def __init__(self):
        self.groq_available = True
        self.error_count = 0
        self.circuit_breaker_until = None

    async def route(self, task_complexity: str, agent_type: str) -> str:
        # Circuit breaker check
        if self.circuit_breaker_until and datetime.utcnow() < self.circuit_breaker_until:
            return "local:llama-3.1-8b"

        if task_complexity == "high" or agent_type == "supervisor":
            return "groq:llama-3.1-70b-versatile"
        else:
            return "groq:llama-3.1-8b-instant"

    async def on_error(self):
        self.error_count += 1
        if self.error_count >= 3:
            self.circuit_breaker_until = datetime.utcnow() + timedelta(minutes=5)
            self.error_count = 0

    async def on_success(self):
        self.error_count = 0
        self.circuit_breaker_until = None
```

---

## JSON Schema for Tool Calling (Groq Format)

```json
{
  "tools": [
    {
      "type": "function",
      "function": {
        "name": "fetch_option_chain",
        "description": "Retrieves current option chain for a given underlying",
        "parameters": {
          "type": "object",
          "properties": {
            "underlying": { "type": "string", "enum": ["NIFTY", "BANKNIFTY"] },
            "expiry": { "type": "string", "format": "date", "description": "Expiry date YYYY-MM-DD" }
          },
          "required": ["underlying", "expiry"]
        }
      }
    },
    {
      "type": "function",
      "function": {
        "name": "check_risk",
        "description": "Validates trade signal against all risk rules. Returns APPROVE or REJECT.",
        "parameters": {
          "type": "object",
          "properties": {
            "signal": { "type": "object", "description": "Trade signal from evaluate_signal" },
            "portfolio_state": { "type": "object", "description": "Current portfolio snapshot" },
            "risk_params": { "type": "object", "description": "Risk configuration parameters" }
          },
          "required": ["signal", "portfolio_state", "risk_params"]
        }
      }
    },
    {
      "type": "function",
      "function": {
        "name": "place_order",
        "description": "Submits order to broker. REQUIRES valid risk approval < 60s old.",
        "parameters": {
          "type": "object",
          "properties": {
            "instrument": { "type": "string" },
            "side": { "type": "string", "enum": ["BUY", "SELL"] },
            "qty": { "type": "integer", "minimum": 1 },
            "order_type": { "type": "string", "enum": ["LIMIT", "MARKET", "SL"] },
            "price": { "type": "number", "nullable": true },
            "trigger_price": { "type": "number", "nullable": true },
            "tag": { "type": "string", "maxLength": 64 }
          },
          "required": ["instrument", "side", "qty", "order_type", "tag"]
        }
      }
    }
  ]
}
```
