# Authentication & Authorization

> **Scope:** Gateway topology, role conventions, outbound credential tiers, secrets management
> **Audience:** All
> **Key repos:** claudony (gateway), casehub-platform (OIDC), casehub-qhorus (channel ACL)
> **Protocols:** [auth-retrofit-readiness](https://github.com/casehubio/garden/blob/main/docs/protocols/casehub/auth-retrofit-readiness.md), [per-binding-credential-reference](https://github.com/casehubio/garden/blob/main/docs/protocols/casehub/per-binding-credential-reference.md)

## Gateway Topology

**Claudony is the single authenticated entry point** for all human operators and Claude agent sessions.

Internal foundation services (Qhorus, casehub-engine, casehub-work) carry **no auth annotations** on their REST resources — they trust callers implicitly, relying on network policy or mTLS for isolation.

**This contract is only valid when Claudony sits in front.**

A standalone deployment of Qhorus, engine, or work without Claudony requires an auth proxy or Quarkus OIDC/JWT before any external traffic is admitted.

The A2A endpoint on Qhorus (`POST /a2a/message:send`) extends this posture to the agent surface — no token auth is applied at the Qhorus layer; the caller is trusted.

See protocol: [auth-retrofit-readiness](https://github.com/casehubio/garden/blob/main/docs/protocols/casehub/auth-retrofit-readiness.md) for rules on keeping services auth-retrofit-ready while this remains implicit.

## Authentication Mechanisms

| Context | Owner | Mechanism |
|---|---|---|
| Extension-level | Consuming app | Extensions provide no auth |
| Browser → Claudony | `claudony` | WebAuthn passkeys |
| Agent → Claudony | `claudony` | `X-Api-Key` header |
| Channel write ACL | `casehub-qhorus` | `allowed_writers` on `Channel` |
| Internal service-to-service | Network boundary | Trust implicit — no token auth on Qhorus, engine, or work REST resources |
| Qhorus multi-tenant HTTP (no OIDC) | `casehub-qhorus` | `QhorusInboundCurrentPrincipal @Priority(1)` reads `X-Tenancy-ID` header — routing mechanism only, not an auth boundary |

### HTTP Inbound Tenant Routing

`QhorusInboundCurrentPrincipal @DefaultBean @ApplicationScoped` reads `X-Tenancy-ID` header via `TenancyContextFilter @PreMatching` and populates `CurrentPrincipal.tenancyId()` for all HTTP requests.

**`X-Tenancy-ID` is NOT a security boundary** — trust from network policy only.

Displaced by any `@Alternative` (test fixtures, `OidcCurrentPrincipal`).

Test deployments with both qhorus runtime and casehub-platform must add:
```properties
quarkus.arc.exclude-types=io.casehub.platform.mock.MockCurrentPrincipal
```
to prevent CDI ambiguity.

## RBAC Enforcement (`@RolesAllowed`)

Infrastructure implemented. `CurrentPrincipal.roles()` delegates to `groups()` — CaseHub group names map directly to `@RolesAllowed` without a bridge.

**Activate:** add `casehub-platform-oidc` as compile dep; `SecurityIdentityAugmentor` bridges `GroupMembershipProvider` to `SecurityIdentity.getRoles()`.

**Status:** casehub-life wired (life#40) — `@RolesAllowed` on all 5 REST resources, RBAC-differentiated risk thresholds. Other harnesses pending (parent#251 tracks adoption).

Annotations remain **inert** without the OIDC module on classpath.

**Structural constraints:**
- No auth/principal logic in domain or service layers
- Thin REST resources
- Injectable query filters
- Auth-free SPI signatures

### Role Name Convention

Role names used in `@RolesAllowed` annotations are CaseHub group names. Role names must be documented when first introduced in any harness.

**Known roles:**

| Role name | Harness | What it gates |
|---|---|---|
| `admin` | `casehub-devtown` | `MemoryAdminResource` — internal memory store admin operations |

**Convention:** role names are lowercase, domain-prefixed when ambiguous (e.g. `devtown-admin` if `admin` becomes overloaded).

`@RolesAllowed` is inert until `casehub-platform-oidc` is on classpath and OIDC is configured.

### Current Principal Identity

`CurrentPrincipal` SPI in `casehub-platform-api`:
- `actorId()` — unique identifier
- `groups()` — group membership
- `roles()` — delegates to `groups()` by convention
- `hasGroup()` — membership check
- `isSystem()` / `isAuthenticated()` — identity type
- `tenancyId()` — tenant context
- `isCrossTenantAdmin()` — cross-tenant operations

Real implementations must be `@RequestScoped`.

`MockCurrentPrincipal` `@DefaultBean` for testing.

**OIDC implementation:** `casehub-platform-oidc` ships `OidcCurrentPrincipal @RequestScoped` — reads actorId/groups from `SecurityIdentity`, `tenancyId` and `crossTenantAdmin` from fixed JWT claims. Add as compile dep to activate; displaces mock automatically.

### Group Membership Lookup

`GroupMembershipProvider` SPI — `membersOf(groupName)` returns `Set<GroupMember>` (actorId = OIDC sub = SCIM value UUID, displayName = human label).

Empty set = group unknown or has no members.

`MockGroupMembershipProvider @DefaultBean` returns empty.

**Real implementation:** `casehub-platform-scim` (`@ApplicationScoped`, displaces mock by classpath presence) — SCIM 2.0 two-step fetch, `@CacheResult`, static bearer token or OIDC client-credentials auth.

## Outbound Authentication (External Service Calls)

Three systems make outbound HTTP calls to external services: **workers** (`casehub-workers`), **connectors** (`casehub-connectors`), and **quarkus-flow `call: http` workflow steps**.

**The canonical model is Serverless Workflow 1.0's `AuthenticationPolicy`.** quarkus-flow already implements it.

Five auth types:
- **Basic** — legacy services, SMTP relay
- **Bearer** — static API tokens (Slack, Twilio, external REST APIs)
- **Digest** — HTTP digest auth (challenge-response)
- **OAuth2** — machine-to-machine, cloud APIs (GCP, Azure, AWS) via client credentials flow
- **OpenID Connect** — identity-propagating calls (token exchange or forward)
- **Named reference** — shared policy reuse via `use("salesforce-prod")`

### Three Tiers of Outbound Credentials

| Tier | Scope | Config mechanism | Example |
|---|---|---|---|
| **1 — Static deploy-time** | Fixed per deployment, single-vendor | `@ConfigProperty` (MicroProfile Config) | Twilio account SID, global Slack bot token |
| **1.5 — Per-binding config reference** | One credential per DB binding record, deploy-time config | Logical name stored in DB; resolved via `Config.getValue("casehub.<module>.credentials." + ref, String.class)` | Different Slack bot token per Qhorus channel / Slack workspace |
| **2 — Named endpoint** | Multi-endpoint, per-capability, runtime-registered | `EndpointRegistry` SPI with `credentialRef` — **resolution not yet implemented** | Worker dispatching to customer APIs with different auth per tenant |

Connectors currently use **Tier 1** (static `@ConfigProperty`), which is correct for their use case — they connect to a single vendor per connector type.

Optional modules that bind one external account per channel or entity (e.g. one Slack workspace per Qhorus channel) use **Tier 1.5**.

Workers and quarkus-flow target **Tier 2** when the secrets resolver is implemented.

### Secrets Management

Auth policies reference credentials **by name**, never inline in DB or endpoint descriptors.

The actual token lives in the runtime environment (env var or `application.properties`), not the DB.

Actual secret storage (Vault, k8s Secret, environment variable) at Tier 2 is resolved by a secrets backend — **not yet implemented**; `EndpointRegistry.credentialRef` is a forward-compatibility field only.

**"credentialRef is deferred"** means the `EndpointRegistry` SPI's `EndpointDescriptor.credentialRef` field (shipped platform#73) exists but no runtime resolver reads it. Adding `credentialRef` to an endpoint descriptor has no effect today.

Use **Tier 1.5** for per-binding credentials until a secrets backend resolver is implemented.

See protocol: [per-binding-credential-reference](https://github.com/casehubio/garden/blob/main/docs/protocols/casehub/per-binding-credential-reference.md)

## Channel Write ACL

`casehub-qhorus` enforces `allowed_writers` on `Channel` entities.

When a message is dispatched to a channel, Qhorus checks the sender's `actorId` against the channel's `allowed_writers` list. Writes from unauthorized actors are rejected.

This is application-level access control, not a cryptographic security boundary.
