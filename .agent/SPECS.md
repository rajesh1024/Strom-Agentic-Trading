# SPECS.md — Agentic Trading Platform · Technical Specifications

> Paste this as context for tasks that involve API development, database work, or schema design.

---

## Database Schema

### trade_log
```sql
CREATE TABLE trade_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    trade_date DATE NOT NULL,
    strategy_id VARCHAR(64) NOT NULL,
    instrument VARCHAR(128) NOT NULL,
    side VARCHAR(4) NOT NULL CHECK (side IN ('BUY', 'SELL')),
    qty INTEGER NOT NULL CHECK (qty > 0),
    entry_price DECIMAL(12,2),
    exit_price DECIMAL(12,2),
    pnl DECIMAL(12,2),
    slippage DECIMAL(12,2),
    regime VARCHAR(32),
    signal_metadata JSONB,
    correlation_id VARCHAR(64),
    created_at TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX idx_trade_log_date ON trade_log(trade_date);
CREATE INDEX idx_trade_log_strategy ON trade_log(strategy_id);
```

### strategy_registry
```sql
CREATE TABLE strategy_registry (
    id VARCHAR(64) PRIMARY KEY,
    name VARCHAR(256) NOT NULL,
    version INTEGER DEFAULT 1,
    type VARCHAR(32) NOT NULL,
    underlying VARCHAR(32) NOT NULL,
    regime_affinity VARCHAR(32)[] DEFAULT '{}',
    params JSONB NOT NULL,
    active BOOLEAN DEFAULT false,
    backtest_summary JSONB,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);
```

### strategy_performance
```sql
CREATE TABLE strategy_performance (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    strategy_id VARCHAR(64) NOT NULL REFERENCES strategy_registry(id),
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
```

### audit_log
```sql
CREATE TABLE audit_log (
    id BIGSERIAL PRIMARY KEY,
    timestamp TIMESTAMPTZ DEFAULT now() NOT NULL,
    agent_id VARCHAR(64),
    action VARCHAR(64) NOT NULL,
    inputs JSONB,
    outputs JSONB,
    risk_decision VARCHAR(16),
    order_id VARCHAR(64),
    correlation_id VARCHAR(64),
    metadata JSONB
);
-- IMMUTABLE: no UPDATE or DELETE allowed (enforce via DB policy or app layer)
CREATE INDEX idx_audit_log_time ON audit_log(timestamp);
CREATE INDEX idx_audit_log_correlation ON audit_log(correlation_id);
CREATE INDEX idx_audit_log_action ON audit_log(action);
```

### orders
```sql
CREATE TABLE orders (
    id VARCHAR(64) PRIMARY KEY,
    broker_ref VARCHAR(128),
    instrument VARCHAR(128) NOT NULL,
    side VARCHAR(4) NOT NULL,
    qty INTEGER NOT NULL,
    order_type VARCHAR(8) NOT NULL,
    price DECIMAL(12,2),
    trigger_price DECIMAL(12,2),
    status VARCHAR(16) NOT NULL DEFAULT 'PENDING',
    filled_qty INTEGER DEFAULT 0,
    avg_fill_price DECIMAL(12,2),
    slippage DECIMAL(12,2),
    strategy_id VARCHAR(64),
    signal_id VARCHAR(64),
    risk_approval_id VARCHAR(64),
    tag VARCHAR(64),
    correlation_id VARCHAR(64),
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);
```

### positions
```sql
CREATE TABLE positions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    instrument VARCHAR(128) NOT NULL UNIQUE,
    qty INTEGER NOT NULL DEFAULT 0,
    avg_price DECIMAL(12,2),
    current_price DECIMAL(12,2),
    unrealized_pnl DECIMAL(12,2),
    realized_pnl DECIMAL(12,2),
    greeks JSONB,  -- { delta, gamma, theta, vega }
    updated_at TIMESTAMPTZ DEFAULT now()
);
```

---

## API Contracts (Pydantic Models)

### Shared Models
```python
from pydantic import BaseModel, Field
from datetime import datetime, date
from enum import Enum
from typing import Optional

class Underlying(str, Enum):
    NIFTY = "NIFTY"
    BANKNIFTY = "BANKNIFTY"

class Side(str, Enum):
    BUY = "BUY"
    SELL = "SELL"

class OrderType(str, Enum):
    LIMIT = "LIMIT"
    MARKET = "MARKET"
    SL = "SL"

class OrderStatus(str, Enum):
    PENDING = "PENDING"
    OPEN = "OPEN"
    FILLED = "FILLED"
    CANCELLED = "CANCELLED"
    REJECTED = "REJECTED"

class SignalType(str, Enum):
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"

class Regime(str, Enum):
    TRENDING_UP = "trending_up"
    TRENDING_DOWN = "trending_down"
    RANGING = "ranging"
    VOLATILE = "volatile"
    EVENT_DRIVEN = "event_driven"

class Severity(str, Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"
```

### Request/Response Models

```python
# Option Chain
class OptionStrike(BaseModel):
    strike: int
    ce_ltp: float
    pe_ltp: float
    ce_oi: int
    pe_oi: int
    ce_iv: float
    pe_iv: float
    ce_greeks: dict = Field(default_factory=dict)
    pe_greeks: dict = Field(default_factory=dict)

class OptionChainResponse(BaseModel):
    underlying: Underlying
    spot_price: float
    timestamp: datetime
    expiry: date
    chain: list[OptionStrike]
    stale: bool = False

# Crypto Orderbook
class DepthLevel(BaseModel):
    price: float
    qty: float

class CryptoOrderbook(BaseModel):
    symbol: str
    bids: list[DepthLevel]
    asks: list[DepthLevel]
    timestamp: datetime
    last_update_id: int

# Features
class RegimeFeatures(BaseModel):
    volatility_rank: float
    trend_strength: float
    mean_reversion_score: float

class FeatureVector(BaseModel):
    pcr: float
    iv_skew: float
    max_pain: int
    oi_change_ce_top5: list[dict]
    oi_change_pe_top5: list[dict]
    vwap_deviation: float
    atr_14: float
    rsi_14: float
    regime_features: RegimeFeatures

# Signals
class TradeSignal(BaseModel):
    signal_id: str
    signal: SignalType
    instrument: str
    strike: int
    option_type: str  # CE or PE
    qty: int
    entry_price: float
    stop_loss: Optional[float]
    target: Optional[float]
    strategy_id: str
    confidence_score: float
    rationale_data: dict = Field(default_factory=dict)
    timestamp: datetime

# Risk
class RiskCheck(BaseModel):
    rule: str
    passed: bool
    detail: str

class RiskDecision(BaseModel):
    approved: bool
    risk_score: float
    checks: list[RiskCheck]
    modified_signal: Optional[TradeSignal] = None
    timestamp: datetime

class RiskParams(BaseModel):
    max_position_size: int = 4
    max_portfolio_delta: float = 0.5
    max_daily_loss: float = 20000.0
    max_drawdown: float = 0.1
    margin_check: float = 0.9
    time_of_day: dict[str, str] = {"start": "09:20", "end": "15:15"}
    correlation_limit: float = 0.8
    single_concentration: float = 0.4

# Orders
class OrderRequest(BaseModel):
    instrument: str
    side: Side
    qty: int = Field(gt=0)
    order_type: OrderType
    price: Optional[float] = None
    trigger_price: Optional[float] = None
    tag: str = Field(max_length=64)
    risk_approval_id: str  # REQUIRED — must reference valid risk check

class OrderResponse(BaseModel):
    order_id: str
    status: OrderStatus
    broker_ref: Optional[str]
    timestamp: datetime

# Portfolio
class Position(BaseModel):
    instrument: str
    qty: int
    avg_price: float
    ltp: float
    pnl: float
    greeks: Optional[dict] = None

class PortfolioGreeks(BaseModel):
    delta: float
    gamma: float
    theta: float
    vega: float

class PortfolioState(BaseModel):
    positions: list[Position]
    total_pnl: float
    margin_used: float
    margin_available: float
    portfolio_greeks: Optional[PortfolioGreeks] = None
    crypto_positions: list[dict] = Field(default_factory=list)

# Admin
class KillSwitchRequest(BaseModel):
    flatten_positions: bool = False
    reason: str

class KillSwitchResponse(BaseModel):
    activated: bool
    cancelled_orders: list[str]
    flattened_positions: list[str]
    agents_retired: int
    timestamp: datetime

# Strategy
class StrategyCreate(BaseModel):
    id: str = Field(max_length=64, pattern=r'^[a-z0-9_]+$')
    name: str
    type: str
    underlying: Underlying
    regime_affinity: list[Regime] = []
    params: dict

class StrategyResponse(BaseModel):
    id: str
    name: str
    type: str
    underlying: str
    regime_affinity: list[str]
    active: bool
    performance_30d: Optional[dict] = None

# Backtest
class BacktestRequest(BaseModel):
    strategy_id: str
    start_date: date
    end_date: date
    params: dict = Field(default_factory=dict)
    initial_capital: float = Field(gt=0, default=1000000)

class BacktestSummary(BaseModel):
    backtest_id: str
    total_return: float
    sharpe_ratio: float
    max_drawdown: float
    win_rate: float
    total_trades: int
    avg_profit: float
    avg_loss: float
    equity_curve: list[dict]
```

---

## Redis Streams Schema

### Stream Names & Message Formats

```
market.ticks
  { "underlying": "NIFTY", "spot": 24850.0, "timestamp": "ISO8601" }

signals.features
  { "underlying": "NIFTY", "features": { ... FeatureVector ... }, "timestamp": "ISO8601" }

signals.generated
  { "signal": { ... TradeSignal ... }, "correlation_id": "cycle_xxx" }

risk.decisions
  { "decision": { ... RiskDecision ... }, "signal_id": "sig_xxx", "correlation_id": "cycle_xxx" }

orders.submitted
  { "order": { ... OrderResponse ... }, "correlation_id": "cycle_xxx" }

orders.filled
  { "order_id": "ord_xxx", "status": "FILLED", "fill_price": 28.75, "filled_qty": 1, "timestamp": "ISO8601" }

portfolio.updated
  { "portfolio": { ... PortfolioState ... }, "trigger": "order_filled|manual_refresh", "timestamp": "ISO8601" }

agents.lifecycle
  { "agent_id": "mda_nifty_01", "event": "spawned|active|idle|retired|error", "timestamp": "ISO8601" }

alerts.triggered
  { "severity": "INFO|WARNING|CRITICAL", "title": "...", "body": "...", "timestamp": "ISO8601" }

system.killswitch
  { "activated": true, "reason": "...", "flatten": false, "timestamp": "ISO8601" }
```

### Consumer Groups

| Group | Consumers | Streams |
|-------|-----------|---------|
| signal-engine | 1 | market.ticks |
| risk-engine | 1 | signals.generated |
| execution-gateway | 1 | risk.decisions |
| portfolio-manager | 1 | orders.filled |
| websocket-gateway | 1 | ALL (fan-out to clients) |
| agent-runtime | 1 | signals.*, risk.*, portfolio.* |
| audit-logger | 1 | ALL |

---

## WebSocket Protocol

### Connection
```
ws://localhost:8000/api/v1/ws?token=<jwt_token>
```

### Subscribe
```json
{ "type": "subscribe", "channels": ["market.ticks", "portfolio.updated", "alerts.triggered"] }
```

### Unsubscribe
```json
{ "type": "unsubscribe", "channels": ["market.ticks"] }
```

### Server Message
```json
{ "type": "event", "channel": "portfolio.updated", "data": { ... }, "timestamp": "ISO8601" }
```

### Heartbeat (server sends every 15s)
```json
{ "type": "ping" }
```
Client must respond:
```json
{ "type": "pong" }
```
3 missed pongs → server closes connection.

---

## Event Bus Wrapper Interface

```python
class EventBus:
    async def publish(self, stream: str, data: dict) -> str:
        """Publish message to stream. Returns message ID."""

    async def subscribe(self, stream: str, group: str, consumer: str,
                        handler: Callable, block_ms: int = 5000):
        """Subscribe to stream with consumer group. Calls handler(message) for each."""

    async def create_group(self, stream: str, group: str):
        """Create consumer group for stream."""

    async def ack(self, stream: str, group: str, message_id: str):
        """Acknowledge message processing."""

    async def health_check(self) -> bool:
        """Return True if Redis is reachable."""
```

---

## Broker Adapter Interface

```python
from abc import ABC, abstractmethod

class BrokerAdapter(ABC):
    @abstractmethod
    async def place_order(self, instrument: str, side: str, qty: int,
                          order_type: str, price: float | None,
                          trigger_price: float | None, tag: str) -> dict:
        """Place order. Returns { order_id, status, broker_ref }"""

    @abstractmethod
    async def get_order_status(self, order_id: str) -> dict:
        """Get order status. Returns { order_id, status, filled_qty, avg_fill_price }"""

    @abstractmethod
    async def cancel_order(self, order_id: str) -> dict:
        """Cancel order. Returns { order_id, cancelled }"""

    @abstractmethod
    async def get_positions(self) -> list[dict]:
        """Get current positions from broker."""

    @abstractmethod
    async def get_margins(self) -> dict:
        """Get margin state. Returns { used, available, total }"""
```

---

## Data Vendor Adapter Interface

```python
class DataVendorAdapter(ABC):
    @abstractmethod
    async def get_option_chain(self, underlying: str, expiry: str) -> dict:
        """Get option chain. Returns normalized OptionChainResponse."""

    @abstractmethod
    async def get_spot_price(self, underlying: str) -> float:
        """Get current spot price."""

    @abstractmethod
    async def get_historical(self, instrument: str, start: str, end: str,
                             interval: str = "1min") -> list[dict]:
        """Get historical OHLCV data."""

    @abstractmethod
    async def health_check(self) -> bool:
        """Return True if vendor API is reachable."""
```
