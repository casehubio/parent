---
id: PP-20260521-d06f58
title: "Consider varargs type capture over Class<T> when type flows into a lambda"
type: principle
scope: universal
applies_to: "Java API design — methods that accept Class<T> solely to infer T for a lambda or typed operation"
severity: advisory
refs:
  - GE-20260412-e51f12
violation_hint: "API accepts Class<T> whose only use is to type a lambda — callers pass Foo.class with no other effect"
created: 2026-05-21
---

When an API accepts `Class<T>` solely to infer `T` for a lambda or typed operation, the varargs type-capture pattern lets the compiler infer `T` from the lambda itself — eliminating the explicit `Class<T>` argument at the call site.

```java
// Before — caller must pass the class explicitly
public <T> Result<T> query(Class<T> type, Function<T, ?> fn) { ... }
query(Person.class, p -> p.getName())

// After — T inferred from lambda; Class<T> argument gone
@SafeVarargs
public <T> Result<T> query(Function<T, ?> fn, T... typeCapture) { ... }
query(p -> p.getName())
```

The varargs array is never populated at runtime. `typeCapture.getClass().getComponentType()` gives the erased raw class if needed.

**Apply when all hold:**
- `Class<T>` is accepted as a parameter
- Its sole use is to type a lambda at the call site
- The method has no other real vararg parameter

**Do not apply when:**
- A real vararg parameter already exists (two vararg parameters are not allowed)
- The full generic type is needed at runtime (`List<String>.class` — varargs gives only `List.class`)
- `Class<T>` is stored, reflected on, or used for instantiation beyond what the raw class supports
- The API is public-facing and the unused parameter would surprise consumers (add Javadoc if used)

**Apply at new API design time only.** No retrofit of existing APIs is required.

Full worked examples: GE-20260412-e51f12 (`jvm/java-dsl-design.md`), including Drools DSL usage.
