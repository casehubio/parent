---
id: PP-20260512-5f055d
title: "Use Optional only when absence is the method's primary return contract"
type: rule
scope: platform
applies_to: "All Java code across the casehub ecosystem"
severity: guidance
refs: []
violation_hint: "Optional on an entity getter, a map accessor (get(key)), a method parameter, a field, or a collection return type — or Optional.get() called without a presence check"
created: 2026-05-12
---

Use `Optional<T>` as a method return type only when all three hold: (1) finding or
computing the value is the method's entire purpose, (2) absence is a normal expected
outcome — not an error or an unset field, and (3) returning null would overwhelmingly
likely cause the caller to NPE. Canonical examples: `Stream.findFirst()`,
`findById(id)`, `Config.get(key)`. Do not use Optional for: getters on entities,
DTOs, or domain objects (use nullable T); map/store accessors — callers have
`contains()` and `getOrDefault()`; method parameters (use overloads); fields
(Optional is not serializable and breaks JPA/Jackson/Hibernate); collection returns
(return empty collection); nested `Optional<Optional<T>>` (use flatMap). When using
Optional: never return null from an Optional-returning method — return
`Optional.empty()`; never call `get()` directly — use `orElse()`, `orElseThrow()`,
or `ifPresent()`; prefer `orElseGet(() -> expr)` over `orElse(expr)` when the
default involves any computation, since `orElse()` always evaluates its argument.
The JavaParser approach — Optional on all return types as a blanket null-replacement
— is the anti-pattern this rule prevents.
