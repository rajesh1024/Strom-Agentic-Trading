
# STROM — API Contracts (M0–M2)

Base URL: `/api/v1`
Auth: See specs/05-security.md

## Common
### GET /health
Response 200:
```json
{"status":"ok"}
```

### GET /metrics
Prometheus text or JSON (implementation choice). Must exist.

---

## Agents
### POST /agents
Request:
```json
{
  "name": "NIFTY Paper Agent",
  "mode": "paper",
  "frequency_seconds": 60,
  "universe": {"symbols":["NSE:NIFTY50-INDEX"]},
  "strategy_ids": ["00000000-0000-0000-0000-000000000001"],
  "strategy_params": [
    {"strategy_id":"00000000-0000-0000-0000-000000000001","params":{"ema_fast":9,"ema_slow":21}}
  ],
  "risk_profile": {
    "max_risk_per_trade_pct": 1.0,
    "max_daily_loss_pct": 3.0,
    "max_open_positions": 3,
    "cooldown_seconds": 30,
    "max_notional_exposure_pct": 100.0
  },
  "capital": 100000.00
}
```
Response 201:
```json
{"id":"<uuid>"}
```

### GET /agents
Response 200:
```json
{
  "items":[
    {
      "id":"<uuid>",
      "name":"...",
      "mode":"paper",
      "frequency_seconds":60,
      "universe":{"symbols":["..."]},
      "strategy_ids":["<uuid>"],
      "risk_profile":{...},
      "capital":100000.00,
      "is_enabled":false,
      "status":"CREATED",
      "created_at":"...",
      "updated_at":"..."
    }
  ]
}
```

### GET /agents/{agent_id}
Response 200: (same shape as list item)

### PATCH /agents/{agent_id}
Request (partial allowed):
```json
{
  "name":"New Name",
  "frequency_seconds":120,
  "universe":{"symbols":["NSE:NIFTY50-INDEX","NSE:BANKNIFTY-INDEX"]},
  "strategy_ids":["..."],
  "strategy_params":[{"strategy_id":"...","params":{}}],
  "risk_profile":{...},
  "capital":120000.00
}
```
Response 200:
```json
{"status":"updated"}
```

### DELETE /agents/{agent_id}
Response 204: empty

### POST /agents/{agent_id}/start
Response 200:
```json
{"status":"started"}
```
Side effect: publish `strom.agent.start_requested`

### POST /agents/{agent_id}/stop
Response 200:
```json
{"status":"stopped"}
```
Side effect: publish `strom.agent.stop_requested`

---

## Runs / Stats
### GET /agents/{agent_id}/runs?limit=50
Response 200:
```json
{
  "items":[
    {
      "id":"<uuid>",
      "tick_time":"...",
      "started_at":"...",
      "completed_at":"...",
      "status":"COMPLETED",
      "error_message":null
    }
  ]
}
```

### GET /agents/{agent_id}/stats
Response 200:
```json
{
  "agent_id":"<uuid>",
  "status":"RUNNING",
  "is_enabled":true,
  "next_tick_eta_seconds": 42,
  "last_run_status":"COMPLETED",
  "last_run_at":"...",
  "equity": 100250.25,
  "realized_pnl": 250.25,
  "unrealized_pnl": 0.00,
  "open_positions": 1,
  "today_trades": 2
}
```

---

## Trades / Orders / Positions / PnL
### GET /agents/{agent_id}/orders?limit=100
Response 200:
```json
{"items":[{"id":"<uuid>","symbol":"...","side":"BUY","qty":1,"status":"FILLED","filled_price":123.45,"created_at":"..."}]}
```

### GET /agents/{agent_id}/trades?limit=100
Response 200:
```json
{"items":[{"id":"<uuid>","symbol":"...","side":"BUY","qty":1,"price":123.45,"ts":"..."}]}
```

### GET /agents/{agent_id}/positions
Response 200:
```json
{"items":[{"symbol":"...","net_qty":1,"avg_price":123.45,"updated_at":"..."}]}
```

### GET /agents/{agent_id}/pnl?limit=200
Response 200:
```json
{"items":[{"ts":"...","equity":100250.25,"realized_pnl":250.25,"unrealized_pnl":0.0,"drawdown":0.0}]}
```

---

## Strategy Catalog (Predefined)
### GET /strategies
Response 200:
```json
{
  "items":[
    {
      "id":"00000000-0000-0000-0000-000000000001",
      "key":"ema_crossover",
      "name":"EMA Crossover",
      "description":"Buy when fast EMA crosses above slow EMA; Sell when crosses below.",
      "params_schema": {
        "type":"object",
        "properties":{"ema_fast":{"type":"integer"},"ema_slow":{"type":"integer"}},
        "required":["ema_fast","ema_slow"]
      }
    }
  ]
}
```

---

## Live Stream (for dashboard)
M0–M2: use SSE to avoid complex WS auth.
### GET /agents/{agent_id}/stream  (SSE)
Event types:
- `run` (run status updates)
- `order` (order status updates)
- `pnl` (pnl snapshot updates)
- `log` (optional structured log lines)

Each SSE message data must be JSON matching DB schema fields.
