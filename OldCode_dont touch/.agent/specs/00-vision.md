
# STROM — Product Vision (M0–M2 scope)

STROM is a standalone, multi-tenant, agentic trading platform that allows users to:
- Create N agents per user
- Configure per-agent frequency, instrument universe, strategy selection, indicators, and risk settings
- Run agents against a simulated market feed (M1) and paper trading (M2)
- View agent dashboards with countdown, run history, trades, and PnL
- Control/query basic agent stats via Telegram (M2)

Out of scope for M0–M2:
- Live broker execution
- User-uploaded Python strategy/indicator plugins (planned M3+)
- Vendor market data feeds
- Production multi-region deployment

Non-negotiables:
- Specs are authoritative and must be implemented as written.
- LLMs are not in the execution path for order placement in M0–M2.
