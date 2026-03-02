
# STROM — Backtesting (Stub for M0–M2)

Backtesting is planned for M3+, but M0–M2 must preserve parity constraints.

## 1) Parity Rule (Non-negotiable)
Backtest and Live/Paper must share:
- same strategy logic
- same indicator/feature computation
- same risk engine
- same order intent schema

Only these swap:
- market data provider (historical replay vs live/sim)
- execution provider (fill simulator vs broker)

## 2) Backtest State Machine (planned)
- REQUESTED → RUNNING → COMPLETED | FAILED

## 3) Historical Replay (planned)
- Replay publishes the same `strom.market.tick` and `strom.agent.tick` events with accelerated time.
- Results must populate the same tables: orders/trades/positions/pnl_snapshots.

## 4) Outputs (planned)
- backtest report artifact (json + html)
- per-run metrics (sharpe, max drawdown, win rate)
