# Convention: Use quarkus-junit Dependency, Not quarkus-junit5

**Applies to:** All casehub modules with @QuarkusTest classes  
**Severity:** Important — quarkus-junit5 is deprecated and produces a warning that obscures real build output

## Problem

`io.quarkus:quarkus-junit5` is a deprecated alias that adds noise to build output and may be removed in a future Quarkus version.

## Rule

Always use `io.quarkus:quarkus-junit` in test dependencies.

## Example

```xml
<!-- Wrong -->
<dependency>
    <groupId>io.quarkus</groupId>
    <artifactId>quarkus-junit5</artifactId>
    <scope>test</scope>
</dependency>

<!-- Right -->
<dependency>
    <groupId>io.quarkus</groupId>
    <artifactId>quarkus-junit</artifactId>
    <scope>test</scope>
</dependency>
```
