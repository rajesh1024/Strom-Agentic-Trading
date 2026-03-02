# Test Strategy — Agentic Trading Platform

## 1. Overview
This document outlines the testing strategy for the Agentic Trading Platform. The focus is on ensuring reliability, security, and performance of the trading agents and the risk engine.

## 2. Test Levels

### 2.1 Unit Testing
- **Scope**: Individual Pydantic models, utility functions, and standalone service methods.
- **Framework**: `pytest`.
- **Requirements**: 80%+ coverage on all new code. Mock all external dependencies (Redis, Database, Broker API).

### 2.2 Integration Testing
- **Scope**: Interaction between components (e.g., API -> SignalEngine -> RiskEngine).
- **Fixtures**: Use fixtures from `data/fixtures/` for consistent test data.
- **Environment**: Local dev environment or Docker Compose.

### 2.3 Risk & Security Testing
- **Scope**: Validation of `RiskEngine` veto power and kill switch functionality.
- **Negative Testing**: Attempt to bypass risk engine with invalid/stale data.
- **Audit Logging**: Verify that every state-changing action is logged correctly.

### 2.4 Agent Lifecycle Testing
- **Scope**: Heartbeat monitoring, idle timeouts, and retirement flows.
- **Concurrency**: Test with up to 20 concurrent agents to ensure stability.

## 3. Test Fixtures (`data/fixtures/`)
All tests must use standardized JSON fixtures to ensure consistency across the CI pipeline.

| Fixture File | Model | Description |
|--------------|-------|-------------|
| `sample_option_chain.json` | `OptionChainResponse` | Snapshot of NIFTY/BANKNIFTY option chains. |
| `sample_crypto_orderbook.json` | `CryptoOrderbook` | L2 orderbook for BTC/ETH. |
| `sample_feature_vector.json` | `FeatureVector` | Computed indicators for strategy input. |
| `sample_signals.json` | `TradeSignal` | Generated buy/sell signals. |
| `sample_portfolio.json` | `PortfolioState` | Consolidated equity and crypto holdings. |
| `sample_risk_params.json` | `RiskParams` | Global and per-agent risk limits. |
| `sample_risk_decision.json` | `RiskDecision` | Outcome of a risk check. |

## 4. Verification Commands

### Validate Fixtures
```bash
python tests/validate_fixtures.py
```

### Run All Tests
```bash
pytest packages/api/tests
```

## 5. Continuous Integration (CI)
- Every PR triggers `tests/validate_fixtures.py`.
- `pytest` runs on every commit to `develop` and `main` branches.
- Coverage reports are generated and must be reviewed if below 80%.

## 6. Edge Cases & Boundary Conditions
- **Stale Data**: Signals should NOT be generated if `stale: true`.
- **Negative Qty**: Orders should be rejected by Pydantic validation.
- **Missing Risk ID**: Orders without `risk_approval_id` must fail.
- **Market Hours**: Orders outside `09:20 - 15:15` must be rejected.
