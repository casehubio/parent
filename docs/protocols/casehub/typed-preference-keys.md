---
id: PP-20260517-2cd5f0
title: "Use typed PreferenceKey<T> for SPI configuration — key carries namespace, name, defaultValue, and string parser"
type: rule
scope: platform
applies_to: "All casehubio SPI configuration and preference resolution — casehub-platform-api and consumers"
severity: important
refs:
  - docs/protocols/casehub/auth-retrofit-readiness.md
  - docs/protocols/casehub/platform-spi-contract.md
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
public record PreferenceKey<T extends Preference>(String namespace, String name, T defaultValue, Function<String, T> parser) {
    public PreferenceKey {
        Objects.requireNonNull(namespace, "namespace must not be null");
        Objects.requireNonNull(name, "name must not be null");
        Objects.requireNonNull(defaultValue, "defaultValue must not be null");
        Objects.requireNonNull(parser, "parser must not be null");
    }
    public String qualifiedName() { return namespace + "." + name; }
    /** Parses a raw (already-interpolated) string into a typed preference instance. */
    public T parse(String raw) { return parser.apply(raw); }
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
        new PreferenceKey<>("devtown", "humanApprovalThreshold",
            DEFAULT,
            s -> new HumanApprovalThreshold(Integer.parseInt(s)));
}

public record SecurityReviewRequired(boolean value)
    implements SingleValuePreference {

    public static final PreferenceKey<SecurityReviewRequired> KEY =
        new PreferenceKey<>("devtown", "securityReviewRequired");
}
```

---

## Parser contract

The `parser` function receives a raw string that has **already been interpolated** — all
`${ENV_VAR}` and `${system.property}` references are resolved before `key.parse()` is
called. The parser is responsible only for type conversion, not interpolation.

This is the casehub equivalent of Drools `ClockTypeOption.get(String)` — each option type
knows how to construct itself from a string. The parser is colocated with the key definition
so defaults and parsing logic are in the same place.

```java
// Good — parser colocated with key and default
public static final PreferenceKey<HumanApprovalThreshold> KEY =
    new PreferenceKey<>("devtown", "humanApprovalThreshold",
        new HumanApprovalThreshold(500),              // default (null guard only)
        s -> new HumanApprovalThreshold(Integer.parseInt(s)));  // parser

// Real business defaults live in the harness preferences file, not in Java
```

**`Function` equality trap:** `PreferenceKey` is a record with a `Function` component.
Java records include all components in `equals()`/`hashCode()`, but `Function` instances
only have identity equality — two separately-created keys with the same namespace/name will
NOT be `equals()`. Always use `key.qualifiedName()` as map keys, not the `PreferenceKey`
object itself.

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
