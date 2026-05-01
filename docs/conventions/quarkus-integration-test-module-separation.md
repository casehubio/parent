# Convention: @QuarkusIntegrationTest Must Live in a Separate Maven Module

**Applies to:** All Quarkus extensions with integration tests  
**Severity:** Critical — placing @QuarkusIntegrationTest in the runtime module causes class loading failures

## Problem

`@QuarkusIntegrationTest` tests the packaged application, not the running CDI container. Placing them alongside `@QuarkusTest` classes in the runtime module causes the augmented artifact to be loaded twice, producing obscure `ClassCastException` or `CDIException`.

## Rule

All `@QuarkusIntegrationTest` classes must live in a dedicated `integration-tests/` submodule, separate from the extension runtime module.

## Example

```
casehub-work/
├── runtime/          ← @QuarkusTest classes here
├── deployment/
└── integration-tests/ ← @QuarkusIntegrationTest classes here
```
