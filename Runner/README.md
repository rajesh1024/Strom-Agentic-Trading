# STROM Wave Runner — Antigravity Task Dispatcher

Upload your `strom_antigravity_tasks.xlsx` and get wave-by-wave prompts ready to paste into Antigravity agents.

## Quick Start

```bash
cd strom-wave-runner
npx serve . -l 3333 -s
```

Then open http://localhost:3333 in your browser.

**Or just double-click `index.html`** — it works as a standalone file too.

## How It Works

1. Upload your Excel task file
2. Tasks are organized into 8 dependency-ordered waves
3. Expand any task → see full details + copyable prompt
4. Click **Copy Prompt** → paste into the matching Antigravity agent
5. Check off tasks as they complete
6. Once a wave is 100% done, the next wave unlocks
7. Progress auto-saves in your browser (localStorage)

## Waves

| Wave | Name | Tasks | Focus |
|------|------|-------|-------|
| 1 | Kickoff | 5 | Scaffolds — all agents work in parallel |
| 2 | Foundation | 8 | DB, Events, CI, API client, Agent base |
| 3 | Services | 12 | Market data, brokers, features, WS, LLM |
| 4 | Core Logic | 8 | Signal engine, Risk engine, Tools, Onboarding |
| 5 | Integration | 11 | Execution, Portfolio, Kill switch, Supervisor |
| 6 | Advanced | 6 | Backtest, Sub-agents, Test suites |
| 7 | Validation | 3 | Integration + E2E tests |
| 8 | Hardening | 2 | Load test + Security audit |
