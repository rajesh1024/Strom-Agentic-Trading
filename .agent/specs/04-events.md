
# STROM — Event Contracts (NATS JetStream) (M0–M2)

All event payloads are JSON.
All events MUST include these envelope fields:
- event_id (uuid)
- event_type (string)
- ts (timestamptz ISO8601 UTC)
- correlation_id (string) -- propagated from API request or scheduler tick
- producer (string) -- service name

## Subjects (authoritative list)

### Agent lifecycle
- `strom.agent.created`
- `strom.agent.updated`
- `strom.agent.deleted`
- `strom.agent.start_requested`
- `strom.agent.stop_requested`
- `strom.agent.tick`

### Runs / processing
- `strom.agent.run_started`
- `strom.agent.run_completed`
- `strom.agent.run_failed`

### Market data
- `strom.market.tick`

### Trading (paper)
- `strom.signal.created`
- `strom.order.intent`
- `strom.order.filled`
- `strom.order.rejected`
- `strom.pnl.updated`

---

## Payload Schemas

### strom.agent.created / updated
```json
{
  "event_id":"<uuid>",
  "event_type":"strom.agent.created",
  "ts":"2026-02-25T00:00:00Z",
  "correlation_id":"...",
  "producer":"api",
  "agent": {
    "id":"<uuid>",
    "user_id":"<uuid>",
    "name":"...",
    "mode":"paper",
    "frequency_seconds":60,
    "universe":{"symbols":["NSE:NIFTY50-INDEX"]},
    "strategy_ids":["00000000-0000-0000-0000-000000000001"],
    "risk_profile":{...},
    "capital":100000.0,
    "is_enabled":false,
    "status":"CREATED"
  }
}
```

### strom.agent.start_requested / stop_requested
```json
{
  "event_id":"<uuid>",
  "event_type":"strom.agent.start_requested",
  "ts":"...",
  "correlation_id":"...",
  "producer":"api",
  "agent_id":"<uuid>"
}
```

### strom.agent.tick
```json
{
  "event_id":"<uuid>",
  "event_type":"strom.agent.tick",
  "ts":"...",
  "correlation_id":"...",
  "producer":"scheduler",
  "agent_id":"<uuid>",
  "tick_time":"..."
}
```

### strom.market.tick (simulated)
```json
{
  "event_id":"<uuid>",
  "event_type":"strom.market.tick",
  "ts":"...",
  "correlation_id":"...",
  "producer":"marketdata-sim",
  "symbol":"NSE:NIFTY50-INDEX",
  "price": 22123.45
}
```

### strom.agent.run_started
```json
{
  "event_id":"<uuid>",
  "event_type":"strom.agent.run_started",
  "ts":"...",
  "correlation_id":"...",
  "producer":"runtime",
  "agent_run": {
    "id":"<uuid>",
    "agent_id":"<uuid>",
    "tick_time":"...",
    "started_at":"...",
    "status":"STARTED"
  }
}
```

### strom.agent.run_completed
```json
{
  "event_id":"<uuid>",
  "event_type":"strom.agent.run_completed",
  "ts":"...",
  "correlation_id":"...",
  "producer":"runtime",
  "agent_run": {
    "id":"<uuid>",
    "agent_id":"<uuid>",
    "tick_time":"...",
    "started_at":"...",
    "completed_at":"...",
    "status":"COMPLETED"
  }
}
```

### strom.signal.created
```json
{
  "event_id":"<uuid>",
  "event_type":"strom.signal.created",
  "ts":"...",
  "correlation_id":"...",
  "producer":"runtime",
  "signal": {
    "id":"<uuid>",
    "agent_run_id":"<uuid>",
    "agent_id":"<uuid>",
    "symbol":"NSE:NIFTY50-INDEX",
    "side":"BUY",
    "confidence":0.75,
    "rationale": {
      "strategy_key":"ema_crossover",
      "inputs":{"ema_fast":9,"ema_slow":21},
      "features":{"ema_fast":201.12,"ema_slow":199.87},
      "decision":{"rule":"fast_crosses_above_slow"}
    }
  }
}
```

### strom.order.intent
```json
{
  "event_id":"<uuid>",
  "event_type":"strom.order.intent",
  "ts":"...",
  "correlation_id":"...",
  "producer":"risk",
  "order_intent": {
    "intent_idempotency_key":"agent:<agent_id>:run:<run_id>:symbol:<symbol>:side:<side>:v1",
    "agent_id":"<uuid>",
    "agent_run_id":"<uuid>",
    "symbol":"NSE:NIFTY50-INDEX",
    "side":"BUY",
    "qty": 1.0,
    "order_type":"MARKET",
    "requested_price": null
  }
}
```

### strom.order.filled
```json
{
  "event_id":"<uuid>",
  "event_type":"strom.order.filled",
  "ts":"...",
  "correlation_id":"...",
  "producer":"execution-paper",
  "order": {
    "id":"<uuid>",
    "intent_idempotency_key":"...",
    "agent_id":"<uuid>",
    "agent_run_id":"<uuid>",
    "symbol":"...",
    "side":"BUY",
    "qty":1.0,
    "status":"FILLED",
    "filled_price": 22123.55,
    "filled_qty": 1.0,
    "fees": 0.0
  },
  "trade": {
    "id":"<uuid>",
    "order_id":"<uuid>",
    "agent_id":"<uuid>",
    "symbol":"...",
    "side":"BUY",
    "qty":1.0,
    "price":22123.55,
    "ts":"..."
  }
}
```

### strom.order.rejected
```json
{
  "event_id":"<uuid>",
  "event_type":"strom.order.rejected",
  "ts":"...",
  "correlation_id":"...",
  "producer":"risk",
  "order": {
    "intent_idempotency_key":"...",
    "agent_id":"<uuid>",
    "agent_run_id":"<uuid>",
    "symbol":"...",
    "side":"BUY",
    "qty":1.0,
    "status":"REJECTED",
    "reject_reason":"max_daily_loss_exceeded"
  }
}
```

### strom.pnl.updated
```json
{
  "event_id":"<uuid>",
  "event_type":"strom.pnl.updated",
  "ts":"...",
  "correlation_id":"...",
  "producer":"execution-paper",
  "pnl": {
    "agent_id":"<uuid>",
    "ts":"...",
    "equity":100250.25,
    "realized_pnl":250.25,
    "unrealized_pnl":0.0,
    "drawdown":0.0
  }
}
```

---

## JetStream Streams (recommended)
- STREAM `STROM_EVENTS` subjects `strom.>` retention `limits` (size/time per environment)
- Durables:
  - scheduler-consumer
  - runtime-consumer
  - risk-consumer
  - execution-consumer
  - api-stream-projection (optional)
