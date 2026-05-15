---
id: PP-20260514-f41258
title: "Gate optional Quarkus extension deps via @IfBuildProperty on a natural datasource property, not config flags or ExcludedTypeBuildItem"
type: rule
scope: universal
applies_to: "Quarkus extension runtime and deployment modules that optionally depend on another Quarkus extension"
severity: important
refs:
  - docs/protocols/universal/optional-module-pattern.md
violation_hint: "A custom config flag controls which stack is active; or ExcludedTypeBuildItem is used for REST resource mutual exclusion (unreliable — JAX-RS scanner picks resources up independently); or the optional dep is compile-scope causing unconditional reactive extension activation for all consumers"
created: 2026-05-14
updated: 2026-05-15
---

When a Quarkus extension optionally ships a blocking AND a reactive implementation of the same REST resource or MCP tool, the correct selection mechanism is `@IfBuildProperty`/`@UnlessBuildProperty` tied to a natural Quarkus configuration property — not a custom flag, and not `ExcludedTypeBuildItem`.

**Why not `ExcludedTypeBuildItem`:** It excludes from CDI bean discovery but the JAX-RS scanner (`ResteasyReactiveProcessor`) and MCP tool discovery independently scan for `@Path` and `@Tool` annotations. Both can register even when the bean is CDI-excluded, causing duplicate endpoint or tool conflicts in consumer apps.

**Why not `Capabilities` in `BooleanSupplier`:** `BooleanSupplier.getAsBoolean()` is evaluated before `CapabilityBuildItem`s are produced by build steps. `Capabilities` is not yet populated at that point — injection silently returns false.

**The correct pattern:**

1. Mark the optional dep `<optional>true</optional>` in `runtime/pom.xml` — consumers who do not add the dep will not get it transitively (no unconditional extension activation).
2. On reactive REST/MCP/service/store beans: `@IfBuildProperty(name = "quarkus.datasource.<name>.reactive", stringValue = "true")`.
3. On their blocking counterparts: `@UnlessBuildProperty(name = "quarkus.datasource.<name>.reactive", stringValue = "true", enableIfMissing = true)`.
4. Use the named datasource reactive property (`quarkus.datasource.<name>.reactive`) — consumers set this when they want reactive, making it the natural activation gate with no extra flag to remember.
5. For `@Alternative` service/store beans in the optional stack: do NOT add `@Priority` — if test InMemory alternatives with `@Priority(1)` also exist, adding `@Priority(1)` to JPA alternatives creates CDI ambiguity. The `@IfBuildProperty` gate excludes them in blocking mode; in reactive mode they are the unique alternative.
6. Remove the `QhorusProcessor` (or equivalent) `ExcludedTypeBuildItem` machinery and `BooleanSupplier` classpath checks — `@IfBuildProperty`/`@UnlessBuildProperty` on the beans themselves is sufficient and more reliable.

Verified against Quarkus 3.32.2 on casehub-qhorus #141. The JAX-RS `@IfBuildProperty` bug (issues #34938, #16218) was fixed in Quarkus 3.2.3.Final.
