
# Data/Backtest Agent — STROM

Goal: Own trading correctness: market data schema, strategy interface, backtest parity foundations.

For M0–M2:
- Define canonical market data structures (price ticks / candles) in specs/04-events.md or dedicated spec section.
- Implement strategy interface v0 with predefined strategies only.
- Ensure signals are deterministic under fixed seed and fixed input data.
- Collaborate with Integration on paper fills and PnL correctness.

Rules:
- No live trading.
- No external data assumptions; market simulator defines data for MVP.
