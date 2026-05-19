---
id: PP-20260518-case-definition-layers
title: "Three-layer case definition architecture — YAML, schema model, canonical API model, fluent DSL"
type: rule
scope: platform
applies_to: "casehub-engine (owns the layers); all CaseHub domain applications (devtown, aml, clinical, QuarkMind) when defining CasePlanModels"
severity: required
refs:
  - CNCF Serverless Workflow 1.0 specification
  - quarkus-flow (Quarkus implementation of Serverless Workflow)
  - casehub-engine-api: CaseDefinitionYamlMapper, YamlCaseHub, CaseDefinition
created: 2026-05-18
---

# Protocol: Three-Layer Case Definition Architecture

**Applies to:** casehub-engine (owns the implementation); all CaseHub harnesses (devtown, aml, clinical, QuarkMind) when writing CasePlanModels  
**Severity:** Required — collapsing layers or bypassing the mapper creates untestable or unserializable case definitions

---

## The Three Layers

This architecture is inherited from CNCF Serverless Workflow 1.0 and its Quarkus implementation (quarkus-flow). Do not reinvent it or collapse layers.

### Layer 1 — YAML

The serialized, human-readable case definition. Configurable per-deployment (or per-repo) without code changes or redeployment. Lives on the classpath as a resource file.

```yaml
name: pr-review
namespace: devtown
version: "1.0.0"
spec:
  goals:
    - name: pr-approved
      condition: ".reviews | length >= 2"
  bindings:
    - name: initial-analysis
      on: { contextChange: {} }
      when: ".pr != null and .codeAnalysis == null"
      capability: "code-analysis"
```

All expressions in YAML are **strings** evaluated by the declared expression language. The case definition declares its expression language at the top level (default: `jq`, following SW 1.0's `expressionLang` field). The mapper must use a pluggable `ExpressionEvaluatorFactory` — never hardcode `new JQExpressionEvaluator(string)`. This keeps the YAML format open to other expression languages without changing the canonical model or the mapper's callers.

### Layer 2 — Generated Schema Model (`io.casehub.model.*`)

Java classes generated from the JSON Schema (`CaseDefinition.yaml` schema file). Intermediate representation produced by Jackson YAML deserialization. Consumers never construct or hold these directly — they are an implementation detail of the mapper.

### Layer 3 — Canonical API Model (`io.casehub.api.model.CaseDefinition`)

The in-memory representation the engine operates on. Built from Layer 2 via `CaseDefinitionYamlMapper`, or built directly via the fluent DSL. This is the only model the engine, blackboard, and binding evaluator see.

---

## The Fluent DSL

`CaseDefinition.builder()`, `Binding.builder()`, `Goal.builder()` etc. produce the same canonical Layer 3 model directly — without going through YAML or the generated schema model.

```java
CaseDefinition.builder()
    .namespace("devtown")
    .name("pr-review")
    .version("1.0.0")
    .goal(Goal.builder()
        .name("pr-approved")
        .condition(ctx -> ctx.getList("reviews").size() >= 2)  // LambdaExpressionEvaluator
        .kind(GoalKind.SUCCESS)
        .build())
    .build();
```

The fluent DSL supports both `JQExpressionEvaluator` (string expressions) and `LambdaExpressionEvaluator` (Java predicates). **YAML cannot express Java lambdas.**

---

## The Subset Constraint

```
YAML-expressible ⊂ Fluent DSL-expressible
```

All YAML case definitions can be expressed using the fluent DSL. The reverse is not true: any case definition using `LambdaExpressionEvaluator` cannot round-trip to YAML.

**Consequence:** YAML is the canonical runtime format. Use the fluent DSL for tests, local construction, and any scenario where lambdas are appropriate (integration test mock conditions). Never use lambdas in a production case definition that should be configurable without redeployment.

---

## Entry Points

**Runtime (YAML-backed):** Extend `YamlCaseHub` and pass the classpath resource path.

```java
@ApplicationScoped
public class PrReviewCaseHub extends YamlCaseHub {
    public PrReviewCaseHub() {
        super("devtown/pr-review.yaml");
    }
}
```

`YamlCaseHub` lazy-loads the definition via `CaseDefinitionYamlMapper` and caches it. Use this for all production case definitions.

**Tests (fluent DSL):** Construct `CaseDefinition` directly using builders. No classpath resource required. Use `LambdaExpressionEvaluator` for binding conditions — this avoids JQ evaluation overhead and makes test failures readable.

---

## Rules

1. **Declare the expression language at the case definition level.** Follow SW 1.0's `expressionLang` field. Default is `jq`. The mapper reads this field and passes it to the `ExpressionEvaluatorFactory` — no hardcoded evaluator type.

2. **Do not hardcode `new JQExpressionEvaluator(string)` in `CaseDefinitionYamlMapper`.** Use an `ExpressionEvaluatorFactory` so the mapper is expression-language-agnostic. This is the engine gap tracked in casehubio/engine#280 (open).

3. **Do not bypass `CaseDefinitionYamlMapper`.** It is the single conversion point from YAML to the canonical model. Custom parsers or direct Jackson deserialization to `io.casehub.api.model.*` will break as the schema evolves.

2. **Do not hold `io.casehub.model.*` types outside the mapper.** Generated schema models are an implementation detail. Inject or pass `CaseDefinition` (Layer 3), not schema model objects.

3. **Do not use `LambdaExpressionEvaluator` in YAML-loaded definitions.** It cannot be expressed in YAML and will not survive serialization. If a condition cannot be expressed as JQ, reconsider the design before using a lambda in production.

4. **Do not collapse YAML and canonical model into a single type.** The separation exists so that YAML format can evolve (via schema versioning) independently of the in-memory API.

5. **Harnesses use `YamlCaseHub` for runtime case definitions.** Extend it; do not duplicate the loading and caching logic.

---

## Violation Hints

- Custom Jackson deserialization producing `io.casehub.api.model.*` directly (bypasses mapper)
- `io.casehub.model.*` types leaking into service or handler code
- `LambdaExpressionEvaluator` in a case definition that is registered via YAML at startup
- A harness loading YAML without `YamlCaseHub` or `CaseDefinitionYamlMapper`
