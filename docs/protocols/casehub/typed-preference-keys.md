---
id: PP-20260517-2cd5f0
title: "Use typed PreferenceKey<T> for SPI configuration — never stringly-typed get(String, Class<?>)"
type: rule
scope: platform
applies_to: "All casehubio SPI configuration and preference resolution — casehub-platform-api and consumers"
severity: important
refs:
  - docs/protocols/casehub/auth-retrofit-readiness.md
  - casehubio/parent#26
violation_hint: "get(String key, Class<T> type) in a preference or configuration SPI — string key with class parameter indicates stringly-typed lookup that should be a typed key"
created: 2026-05-17
---

# Protocol: Typed Preference Keys

**Applies to:** All SPI configuration and preference interfaces in casehubio  
**Severity:** Important — stringly-typed configuration breaks at runtime; typed keys fail at compile time

When building SPI-based configuration or preference interfaces, use typed keys. The key encodes the return type; the compiler infers the correct type at the call site. No string keys, no `Class<?>` parameters, no casts.

This pattern is proven at scale in Drools (`OptionKey<T>` / `SingleValueOption` / `MultiValueOption`).

---

## The Pattern

**Three moving parts:**

**1 — Marker interfaces (in casehub-platform-api)**
```java
public interface CasePreference {}
public interface SingleValuePreference extends CasePreference {}
public interface MultiValuePreference extends CasePreference {}
```

**2 — Typed key (in casehub-platform-api)**
```java
public class PreferenceKey<T extends CasePreference> {
    private final String namespace;
    private final String name;
    public PreferenceKey(String namespace, String name) { ... }
}
```

**3 — Typed lookup (in CasePreferences interface)**
```java
public interface CasePreferences {
    // Return type T inferred from key — no cast, no Class<?> parameter
    <T extends SingleValuePreference> T get(PreferenceKey<T> key);
    <T extends MultiValuePreference> T get(PreferenceKey<T> key, String subKey);
    Map<String, Object> asMap(); // for CaseContext/JQ injection
}
```

---

## Defining a Preference (application layer)

Each preference is a typed value object with a static `KEY` constant:

```java
// DevTown defines this — not in platform-api
public record HumanApprovalThreshold(int value)
    implements SingleValuePreference {

    public static final PreferenceKey<HumanApprovalThreshold> KEY =
        new PreferenceKey<>("devtown", "humanApprovalThreshold");
}

public record SecurityReviewRequired(boolean value)
    implements SingleValuePreference {

    public static final PreferenceKey<SecurityReviewRequired> KEY =
        new PreferenceKey<>("devtown", "securityReviewRequired");
}
```

---

## Usage — compile-time safe

```java
CasePreferences prefs = provider.resolve(scope);

// Return type inferred from KEY — no cast, no Class<?>, no string
HumanApprovalThreshold threshold = prefs.get(HumanApprovalThreshold.KEY);
int value = threshold.value();

// Wrong key type is a compile error, not a runtime ClassCastException
```

**Never:**
```java
// Stringly-typed — string key + Class<?> parameter = runtime failure risk
int threshold = prefs.get("humanApprovalThreshold", Integer.class);
```

---

## Multi-value preferences

For preferences with multiple values distinguished by a sub-key (e.g. per-reviewer-type thresholds):

```java
public record ReviewerThreshold(String reviewerType, int threshold)
    implements MultiValuePreference {

    public static final PreferenceKey<ReviewerThreshold> KEY =
        new PreferenceKey<>("devtown", "reviewerThreshold");
}

// Usage — subKey distinguishes the value
ReviewerThreshold senior = prefs.get(ReviewerThreshold.KEY, "senior");
ReviewerThreshold security = prefs.get(ReviewerThreshold.KEY, "security");
```

---

## Why this applies beyond preferences

The same pattern applies to any SPI where a caller retrieves a typed value by key:
- Future configuration SPIs
- Strategy registries where multiple named strategies exist
- Any `get(key) → typed value` pattern

If you are writing `get(String, Class<T>)` anywhere in an SPI, consider whether a typed key is the right design.
