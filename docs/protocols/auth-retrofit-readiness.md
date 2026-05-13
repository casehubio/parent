---
id: PP-20260513-auth-retrofit
title: "Auth retrofit readiness — keep auth out of the domain so RBAC can be introduced cleanly"
type: rule
scope: platform
applies_to: "All casehubio repos — REST resources, services, domain, SPIs, queries"
severity: required
refs: []
violation_hint: "Auth checks in service or domain code, identity passed into use cases, or 'get all' queries with no filter hook — all make RBAC painful or impossible to add without touching domain logic"
created: 2026-05-13
---

# Protocol: Auth Retrofit Readiness

**Applies to:** All casehubio repos  
**Severity:** Required — violations force auth logic into the domain and make RBAC a rewrite, not an addition

RBAC (authentication, authorisation, role-based access control) is not yet implemented in CaseHub. It will be introduced once the platform is working end-to-end. This protocol ensures that decisions made in the meantime do not make RBAC hard to retrofit.

---

## The Five Rules

### 1 — No auth logic in domain or service layers

Auth is an incoming adapter concern. The domain never sees a principal, a role, or a permission check.

**Never:**
```java
// In a service or domain class
if (currentUser.hasRole("CASE_ADMIN")) {
    caseRuntime.startCase(...);
}
```

**When auth is introduced, it lives here:**
```java
// In a REST resource (incoming adapter)
@POST @Path("/cases")
@RolesAllowed("CASE_ADMIN")
public Uni<Response> startCase(StartCaseRequest request) { ... }
```

If a decision about what to do depends on identity, that decision belongs at the adapter boundary, not inside the use case.

---

### 2 — REST resources must stay thin

Every REST resource method must be retrofittable with `@RolesAllowed` (or equivalent) without requiring a structural refactor. This means:

- Business logic lives in a service class, not in the resource method body
- The resource method is a thin dispatcher: validate → delegate → map response
- No complex branching in resource methods that would make annotation-based auth insufficient

---

### 3 — No identity or principal passed into use cases or domain calls

Use case method signatures must not accept a user identity, principal, or session context parameter — even as a convenience.

**Never:**
```java
// In a service interface
Uni<CaseDefinition> getCaseDefinition(String id, Principal caller);
```

When visibility policies are introduced, they will be implemented as SPIs that the adapter or query layer calls — not as parameters threaded through the domain.

---

### 4 — Queries must be structurally amenable to filter injection

Avoid "get all X" queries that return the full unfiltered dataset in a way that cannot be narrowed later. Queries should be written so that a predicate or visibility policy can be injected at the query layer without rewriting the query.

**Prefer:** repository methods that accept a filter/criteria object (even if it's empty today):
```java
Uni<List<CaseInstance>> findAll(CaseInstanceFilter filter);
```

**Avoid:** hardcoded "get everything" queries with no parameter for future narrowing:
```java
Uni<List<CaseInstance>> findAll(); // no hook for visibility policy
```

If you write a `findAll()` today, note it as a known gap in the query's Javadoc so it is found when auth is introduced.

---

### 5 — SPI signatures stay free of auth types

SPI method signatures must not include principal, role, or auth token types — even if it seems convenient. SPIs are pure-Java contracts (Tier 1); auth dependencies belong in adapter-tier implementations.

---

## When Auth Is Introduced

The expected retrofit approach:

1. **Operation-level:** `@RolesAllowed` annotations on REST resource methods (Quarkus OIDC/JWT). Zero domain changes required if rules 1–2 above are followed.
2. **Data-level:** `CaseVisibilityPolicy`, `WorkItemAccessPolicy` SPIs defined in `api/` with permissive no-op defaults. Query layer calls the SPI. Application tier provides domain-specific implementations.
3. **Cross-repo consistency:** a platform protocol will govern where auth checks happen, what SPI contracts look like, and which OIDC provider is used.

---

## Checklist when writing new code

- [ ] Does this service or domain method check a role, permission, or identity? → Move to the adapter
- [ ] Does this REST resource method contain business logic that would block `@RolesAllowed` from being sufficient? → Extract to service
- [ ] Does this method accept a Principal or user context? → Remove it
- [ ] Is this query returning all records with no filter hook? → Add a criteria parameter even if empty today
- [ ] Does this SPI signature reference any auth/identity type? → Remove it
