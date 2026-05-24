# Protocol: Auth Retrofit Readiness

**Applies to:** All casehubio foundation and orchestration repos
(`casehub-work`, `casehub-qhorus`, `casehub-engine`, `casehub-ledger`, `casehub-platform`).

---

## Purpose

RBAC and token-based authentication are not yet implemented in foundation services. Auth must
not be foreclosed — every design decision must keep it addable without structural rework.

---

## Gateway Topology (Current State)

**Claudony is the single authenticated entry point.** Human operators and Claude agent sessions
authenticate via Claudony (WebAuthn passkeys or `X-Api-Key`). Internal services — Qhorus,
casehub-engine, casehub-work — carry no auth annotations on their REST resources. They trust
callers implicitly, relying on network policy or mTLS for isolation in a composed deployment.

This contract is only valid when Claudony (or an equivalent auth proxy) sits in front of all
external traffic. **A standalone deployment of Qhorus, casehub-engine, or casehub-work without
Claudony exposes unauthenticated REST surfaces.** Adding authentication to a standalone
deployment requires either:
- An auth proxy (NGINX + Keycloak, AWS API Gateway + Cognito, etc.), or
- Enabling Quarkus OIDC/JWT on the target service and adding `@Authenticated` or
  `@RolesAllowed` to its REST resources.

The A2A endpoint (`POST /a2a/message:send` on Qhorus) extends this posture to the agent
surface — no token auth is applied at the Qhorus layer; the caller is trusted at the network
level.

---

## Design Rules (Keep Auth Addable)

### 1. No auth or principal logic in domain or service layers

`CurrentPrincipal` (from `casehub-platform-api`) is the only acceptable principal type.
Inject it via CDI where the actor identity is needed. Do not embed `SecurityIdentity` or
Quarkus security types in domain model or service classes — these are framework-specific and
make auth logic impossible to remove or swap.

### 2. REST resources must stay thin

Keep REST resources as thin routing shims. Business logic must not live in REST resource
methods — it must live in `@ApplicationScoped` service classes that can be tested without HTTP.
Thin resources are safe to annotate with `@Authenticated` or `@RolesAllowed` without
touching any business logic.

### 3. Queries need a structurally injectable filter

Queries that return entity lists must accept an optional principal filter parameter or use a
CDI-injectable filter bean. This lets auth be added at the query boundary by injecting a
real `CurrentPrincipal` without rewriting query method signatures.

### 4. SPI signatures must stay free of auth types

SPI interface methods must not accept or return Quarkus security types (`SecurityIdentity`,
`QuarkusPrincipal`, JWT claims). SPIs that need actor context must use `ActorType` or
`CurrentPrincipal` from `casehub-platform-api` — these are stable, framework-agnostic types.

### 5. No `@RolesAllowed` on foundation REST resources yet

Adding `@RolesAllowed` before the gateway topology is formalized would break test setups that
call foundation REST resources directly. Auth annotations are added at the integration layer
(Claudony) and at individual service surfaces only when auth retrofit is explicitly planned.

---

## When These Rules Matter Most

- Adding a new REST resource to any foundation service
- Adding a new service method that returns a list filtered by ownership
- Defining a new SPI interface that crosses a trust boundary
- Adding a new deployment configuration (standalone without Claudony)

---

**Refs:** casehubio/parent#57; `docs/PLATFORM.md §Authentication`
