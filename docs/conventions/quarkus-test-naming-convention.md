# Convention: @QuarkusTest Classes Must Be Named *Test.java, Never *IT.java

**Applies to:** All modules with @QuarkusTest classes  
**Severity:** Critical — *IT.java is picked up by maven-failsafe-plugin, produces "Tests run: 0" with no error

## Problem

`*IT.java` files are collected by maven-failsafe-plugin, not maven-surefire-plugin. When both are on the classpath but the test is intended as a `@QuarkusTest` (surefire), failsafe runs it in isolation and reports "Tests run: 0" silently.

## Rule

All `@QuarkusTest` classes must end in `Test.java`. Reserve `IT.java` suffix for actual integration tests run by failsafe with a packaged artifact.

## Example

```
// Wrong
WorkItemServiceIT.java  ← collected by failsafe, reports 0 tests

// Right
WorkItemServiceTest.java ← collected by surefire, runs normally
```
