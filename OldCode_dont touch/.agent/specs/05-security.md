
# STROM — Security & IAM (M0–M2)

## 1) Threat Model (M0–M2)
Primary risks:
- Unauthorized access to agent controls (start/stop) and data
- Leakage of API keys/secrets (future: model/broker keys)
- Cross-tenant data exposure
- Event injection (malicious publishing to NATS)

## 2) Auth Modes

### A) Dev Auth Mode (Allowed in M0–M2)
- API accepts a header: `X-Dev-User-Email`
- API maps email to users table (create-on-first-seen)
- This mode MUST be clearly isolated to dev environments via env var `STROM_AUTH_MODE=dev`.
- Production MUST NOT run in dev mode.

### B) Production Target (M3+)
- Keycloak OIDC:
  - API validates JWT signature and `aud` and `iss`
  - user identity from `sub` and `email`
- RBAC scopes:
  - `strom:paper:write`, `strom:paper:read`
  - `strom:live:write`, `strom:live:read` (future)
- Admin scopes for ops only

## 3) Tenant Isolation
- All rows are scoped by user_id.
- API must enforce `user_id` checks on every agent_id query.
- Never trust client-provided user_id.

## 4) Secrets Management (future keys; stub in M0–M2)
- Target: OpenBao
- Rules:
  - secrets never stored in plaintext DB
  - secrets never logged
  - access policies per tenant

## 5) NATS Security (M0–M2 local)
- Local dev may run NATS without auth.
- Production target:
  - NATS accounts/users
  - publish/subscribe permissions by service
  - TLS

## 6) Audit Logging (M0–M2 minimal)
Log these actions with correlation_id:
- agent create/update/delete
- agent start/stop
- strategy catalog reads (optional)
