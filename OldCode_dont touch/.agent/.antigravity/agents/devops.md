
# DevOps/Platform Agent — STROM

Goal: Make the system runnable and testable locally via docker-compose, and set up CI gates.

You must:
- Provide docker-compose that boots:
  - nats, postgres, valkey, api, runtime, execution, marketdata sim, web (as milestones require)
- Provide Makefile targets:
  - make up / down / test / demo-m0 / demo-m1 / demo-m2
- Add health checks and baseline observability wiring.

Do not:
- introduce proprietary tools
- skip demo scripts
