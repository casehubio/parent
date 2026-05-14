---
id: PP-20260514-f41258
title: "Gate optional Quarkus extension deps via Capabilities + ExcludedTypeBuildItem, not config flags"
type: rule
scope: universal
applies_to: "Quarkus extension runtime and deployment modules that optionally depend on another Quarkus extension"
severity: important
refs:
  - docs/protocols/universal/optional-module-pattern.md
violation_hint: "A user-facing config flag controls whether an optional extension dep is active instead of classpath presence; or an optional extension dep is compile-scope causing unconditional activation for all consumers"
created: 2026-05-14
---

When a Quarkus extension optionally depends on another Quarkus extension (e.g. `quarkus-hibernate-reactive-panache`), mark it `<optional>true</optional>` in the runtime pom so it is not transitively forced on consumers. In the deployment processor, use `Capabilities.isPresent(Capability.X)` as the `BooleanSupplier` for `@BuildStep(onlyIf/onlyIfNot=...)` rather than a user-facing config flag. Produce `ExcludedTypeBuildItem` for classes that reference the optional dep's types when the capability is absent — this prevents CDI registration and JVM classloading of those classes at runtime even though their `.class` files remain in the jar. Produce a symmetric `ExcludedTypeBuildItem` for blocking counterpart classes when the capability IS present. Add `@Priority(1)` to `@Alternative` beans in the optional stack so CDI auto-selects them when not excluded. Classpath presence is the single source of truth; no flag required from consumers.
