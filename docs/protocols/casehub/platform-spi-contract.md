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
        new PreferenceKey<>("devtown", "humanApprovalThreshold");
}

// Call site:
HumanApprovalThreshold t = prefs.get(HumanApprovalThreshold.KEY);
int threshold = t != null ? t.value() : HumanApprovalThreshold.DEFAULT.value();
```

**Why:** Defaults are discoverable alongside the key definition on the record, not scattered
across call sites. The `Preferences` interface surface stays minimal.

**Never** use a stringly-typed fallback — see [`typed-preference-keys.md`](typed-preference-keys.md).

---

## Rule 4 — Mock `PreferenceProvider` wires to JQ/CaseContext via `asMap()`

`MockPreferenceProvider` returns `String` values from `@ConfigProperty`. Typed `get()` always
returns `null` from the mock — callers must apply rule 3. `asMap()` returns the config strings,
which flow into `CaseContext` and JQ `when` conditions:

```properties
casehub.platform.preferences.defaults.devtown.humanApprovalThreshold=500
```

In a JQ expression: `.preferences."devtown.humanApprovalThreshold"` → `"500"` (string).

Real implementations that want typed values in `asMap()` must populate the map with typed
objects, not strings.
