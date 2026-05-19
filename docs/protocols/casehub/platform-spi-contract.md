---
id: PP-20260518-platform-spi-contract
title: "Platform SPI implementation contract — scope, mock pattern, Preference DEFAULT"
type: rule
scope: platform
applies_to: "All repos implementing casehub-platform-api SPIs"
severity: important
refs:
  - docs/protocols/casehub/typed-preference-keys.md
  - docs/protocols/casehub/engine-spi-noops-defaultbean.md
  - docs/protocols/casehub/auth-retrofit-readiness.md
created: 2026-05-18
---

# Protocol: Platform SPI Implementation Contract

**Applies to:** All repos implementing `CurrentPrincipal`, `GroupMembershipProvider`, `PreferenceProvider`, or any future SPI from `casehub-platform-api`.

---

## Rule 1 — Real `CurrentPrincipal` implementations must be `@RequestScoped`

`CurrentPrincipal` carries per-request identity. Real implementations must be
`@RequestScoped` backed by the active security context (e.g. Quarkus `SecurityIdentity`):

```java
@RequestScoped
public class SecurityCurrentPrincipal implements CurrentPrincipal {
    @Inject SecurityIdentity identity;
    @Override public String actorId() { return identity.getPrincipal().getName(); }
    @Override public Set<String> groups() { return identity.getRoles(); }
}
```

Injecting a `@RequestScoped` bean into an `@ApplicationScoped` REST resource is safe —
CDI client proxies delegate to the correct contextual instance per request.

**⚠ Do not access `CurrentPrincipal` inside reactive pipelines** (`Uni`/`Multi`) without
`@ActivateRequestContext` — the request context is not active on the executing thread.

**The mock is intentionally `@ApplicationScoped`** — `MockCurrentPrincipal` has no request
context to read from; it uses `@ConfigProperty`. `@DefaultBean` yields to any non-default
bean regardless of scope, so the mock is automatically displaced when a real implementation
is present.

---

## Rule 2 — Override the mock with a plain `@ApplicationScoped` (no `@DefaultBean`)

`casehub-platform` ships `@DefaultBean` mocks for all SPIs. To override in your deployment,
declare a plain `@ApplicationScoped` implementation — do not use `@DefaultBean`:

```java
@ApplicationScoped   // no @DefaultBean — this wins over the mock automatically
public class MyPreferenceProvider implements PreferenceProvider {
    @Override public Preferences resolve(SettingsScope scope) { ... }
}
```

`@DefaultBean` yields to any non-default qualifying bean. You do not need to exclude or
deactivate the mock; CDI picks your implementation automatically.

---

## Rule 3 — Preference records carry their own DEFAULT constant

`Preferences.get(key)` returns `null` when a key is not set. Callers must fall back to a
`DEFAULT` constant on the Preference record itself — not on the `Preferences` interface:

```java
public record HumanApprovalThreshold(int value) implements SingleValuePreference {
    public static final HumanApprovalThreshold DEFAULT = new HumanApprovalThreshold(500);
    public static final PreferenceKey<HumanApprovalThreshold> KEY =
        new PreferenceKey<>("devtown", "humanApprovalThreshold",
            DEFAULT,
            s -> new HumanApprovalThreshold(Integer.parseInt(s)));
}

// Call site — never null:
HumanApprovalThreshold t = prefs.getOrDefault(HumanApprovalThreshold.KEY);
int threshold = t.value();
```

**Why:** Default and parser are colocated with the key definition. `getOrDefault(key)` applies
`key.defaultValue()` automatically — call sites are null-free. `key.parse(raw)` enables any
string-source provider (`MockPreferenceProvider`, future `config/` module) to return typed values.

**Never** use a stringly-typed fallback — see [`typed-preference-keys.md`](typed-preference-keys.md).

---

## Rule 4 — Mock `PreferenceProvider` wires to CaseContext via `asMap()`

`MockPreferenceProvider` parses config string values to their natural Java types (Integer,
Long, Boolean, Double, List, String) for `asMap()`. `get(key)` calls `key.parse(raw)` on
String values — returns a typed value when the config string is stored as a `String` object.
Numeric/boolean values converted by `parseValue()` are accessible via `asMap()` but return
`null` from `get(key)` (see Javadoc). `asMap()` returns typed values suitable for injection
into CaseContext and any pluggable ExpressionEvaluator:

```properties
casehub.platform.preferences.defaults.devtown.humanApprovalThreshold=500
```

This yields `{"devtown.humanApprovalThreshold": 500}` (Integer) in `asMap()`. Any
ExpressionEvaluator (JQ, Lambda, or others) receives the correct Java type.

Real implementations populate the map with pre-typed values — no string-to-type parsing needed.
