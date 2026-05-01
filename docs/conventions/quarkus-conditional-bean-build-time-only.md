# Convention: @IfBuildProperty and @UnlessBuildProperty Are Evaluated at Build Time Only

**Applies to:** All modules using conditional bean activation  
**Severity:** Critical — setting the property in QuarkusTestProfile silently has no effect

## Problem

`@IfBuildProperty(name="X", stringValue="Y")` on a bean is evaluated during augmentation (build time), not at runtime. Setting the property in `QuarkusTestProfile.getConfigOverrides()` happens after augmentation — the bean's activation state is already baked in and cannot be changed.

## Rule

To activate/deactivate beans conditionally in tests, use `@io.quarkus.arc.profile.IfBuildProfile` with test profiles, or use `quarkus.arc.selected-alternatives` / `quarkus.arc.exclude-types` in test `application.properties`.

## Example

```properties
# src/test/resources/application.properties — evaluated at augmentation
quarkus.arc.selected-alternatives=io.casehub.qhorus.runtime.mcp.QhorusMcpTools
```
