# Drill-Down — The Declaration Surface

*Schema, codegen, composition, and expression evaluation — the machinery beneath YAML.*

---

## Architecture Overview

The declaration surface compiles YAML, Java annotations, and
(experimentally) TypeScript into executable runtime models. Three
parallel pipelines converge on one CDI registry:

1. **YAML pipeline** — `CaseDefinition.yaml` is parsed by
   `CaseDefinitionYamlParser`, pre-processed by yaml-core's
   `VariableResolver` and `ForEachExpander`, validated against
   `CaseDefinitionSchema`, and registered as a `CaseDefinition`
   CDI bean.

2. **Annotation pipeline** — `@Case`, `@Binding`, `@Stage`
   annotations are processed at build time by
   `CasehubRecordCodegen`, which emits YAML-equivalent records
   into `api/target/generated-sources/yaml-records/`. The
   generated records register through the same parser path.

3. **TypeScript pipeline** *(POC)* — `defineGraph()` and
   `defineLifecycle()` helpers in desiredstate's `ts-dsl` modules
   produce typed JSON envelopes. These compile to
   `GoalCompiler` beans via the same Java backend.

At runtime, the `CaseDefinitionRegistry` holds all compiled
definitions. The engine does not know which surface produced them.

yaml-core sits beneath every YAML surface across the entire platform.
Engine case definitions, desiredstate plugin manifests, pages
dashboard declarations, and eidos agent descriptors all build on the
same `VariableResolver`, `ForEachExpander`, `ModuleExpander`, and
`StepRuntime` primitives.

---

## SPI Contracts

### Expression Engine Registry

`ExpressionEngineRegistry` (platform-api) resolves expression
languages by name and evaluates expressions against typed contexts.

| Interface | Methods | Governs |
|-----------|---------|---------|
| `ExpressionEngine` | `evaluate(String expr, Object context)`, `supports(String lang)` | Single-language evaluation |
| `ExpressionEngineRegistry` | `resolve(String lang)`, `evaluateAll(...)` | Language dispatch |
| `PropertySource` | `get(String key)`, `getSecret(String key)` | `$config` and `$secret` scope injection |

Three engines ship:

- **JQ** — evaluates against `context.layer(ContextLayer.WORKING).asJsonNode()`. Default for case bindings.
- **MVEL3** — typed POJO context. Business rules with compile-time type checking.
- **JEXL3** — template expression evaluation. String interpolation and dynamic content.

Per-expression language override via `{lang: expr}` syntax. Config
and secret injection via `$config` and `$secret` scopes are available
to all three engines through the shared `PropertySource` abstraction.

### YAML Processing SPIs

| Interface | Methods | Governs |
|-----------|---------|---------|
| `VariableResolver` | `resolve(String template, Map<String, Object> sources)` | `${var}` substitution with pluggable sources and deferred prefixes |
| `ForEachExpander` | `expand(JsonNode node, Map<String, Object> context)` | Inline + named groups, `when` conditions, ID-keyed results |
| `ModuleExpander` | `expand(YamlModule module, TypedExpandedModule<T> target)` | Composable YAML sections with typed expansion |
| `StepRuntime` | `execute(Step step, StepContext context)` | YAML-declared action pipeline execution |
| `PluginProcessor` | APT-based | Compile-time plugin discovery and registration |

### Case Definition Schema

`CaseDefinition.yaml` is the canonical schema source. The
`CaseDefinitionSchema` validates:

- Case structure (stages, plan items, completion semantics)
- Agent bindings (capability requirements, routing weights)
- Worker dispatch (concurrency budgets, session scope, dispatch mode)
- Oversight gates (risk classification rules, quorum requirements)
- Context bindings (expression language, input/output mappings)
- Goal expressions (Boolean algebra, JQ predicates)

Validation produces structured errors with path-based diagnostics,
not string messages.

---

## Data Model

### YAML Record Codegen

`CasehubRecordCodegen` (codegen module) reads two inputs:

1. `schema/src/main/resources/schema/CaseDefinition.yaml` — the
   canonical schema
2. `schema/src/main/resources/schema/yaml-record-mappings.yaml` —
   type overrides, aliases, extra fields

It emits Java records into
`api/target/generated-sources/yaml-records/` under
`io.casehub.api.model.converter.yaml`. Records regenerate on
`mvn compile`. Hand-written exceptions: `YamlAgentDescriptor`
(inner records pattern), `JsonNodeForEachAdapter` (utility).

### Case Definition Model

The compiled model is a hierarchy of immutable records:

| Type | Contains | Key fields |
|------|----------|------------|
| `CaseDefinition` | Top-level case | `name`, `stages`, `bindings`, `goals`, `oversight` |
| `StageDefinition` | Stage within a case | `name`, `planItems`, `completionSemantics`, `sentries` |
| `BindingDefinition` | Worker binding | `capability`, `dispatchMode`, `concurrencyBudget`, `routingWeights` |
| `GoalExpression` | Completion condition | Boolean algebra nodes with JQ predicate leaves |
| `OversightGateDefinition` | Gate configuration | `riskLevel`, `quorum`, `escalationPolicy` |

Completion semantics are an enum: `All`, `MOfN(int m)`,
`FirstWins`. Dispatch modes: `ORCHESTRATED`, `CHOREOGRAPHED`.

### Plugin Step Primitives

The YAML plugin system for desiredstate reconciliation provides
built-in step primitives:

| Primitive | Purpose |
|-----------|---------|
| `rest-call` | HTTP request with variable-templated URL, headers, body |
| `json-extract` | JQ extraction from response body into context variables |
| `compare-state` | Diff desired vs actual state, produce delta |
| `assert` | Boolean assertion with structured diagnostic on failure |
| `shell` | Sandboxed shell execution for system-level operations |

Custom compound primitives extend the vocabulary. The declarative
test framework (`*.test.yaml`) provides embedded WireMock and shell
sandbox infrastructure for YAML-only testing.

---

## Runtime Behaviour

### YAML Compilation Flow

```
YAML file on classpath
    │
    ▼
VariableResolver — resolve ${vars} from sources
    │
    ▼
ForEachExpander — expand forEach blocks, evaluate when conditions
    │
    ▼
ModuleExpander — compose YamlModule sections
    │
    ▼
CaseDefinitionYamlParser — parse into CaseDefinition records
    │
    ▼
CaseDefinitionSchema — validate structure, cross-reference SPIs
    │
    ▼
CaseDefinitionRegistry — CDI registration as named bean
```

The YAML application framework supports progressive complexity.
A single flat YAML file suffices for simple cases. Directory
conventions (`META-INF/casehub/`, named subdirectories) support
complex multi-file applications with module composition.

### LSP Server Lifecycle

The LSP server registers on startup and watches the schema
registry. As new YAML declaration capabilities are added to the
platform, the LSP picks them up automatically. The IntelliJ
plugin surfaces LSP capabilities natively: inline validation,
navigation to referenced definitions, rename refactoring across
YAML declarations, and quick-fix suggestions for unknown types
or misspelled strategy names.

---

## Extension Points

| Extension | Mechanism | Effect |
|-----------|-----------|--------|
| New expression language | Implement `ExpressionEngine`, register as CDI bean | Available via `{lang: expr}` syntax across all surfaces |
| New YAML variable source | Implement `PropertySource` | Available as `$prefix.key` in all YAML templates |
| New plugin step primitive | Implement step handler, register via APT `PluginProcessor` | Available as YAML step type in plugin manifests |
| New case definition source | Implement `CaseDefinitionProvider` CDI bean | Loaded alongside YAML and annotation sources |
| Custom completion semantics | Implement `CompletionStrategy` | Available in stage definitions |
| Custom risk classifier | Implement `ActionRiskClassifier` CDI bean | Composable with existing classifiers (most-restrictive-wins) |

---

## Module Map

| Module | Provides | Key types |
|--------|----------|-----------|
| `yaml-core` | YAML composition engine | `VariableResolver`, `ForEachExpander`, `ModuleExpander` |
| `yaml-jackson` | Jackson integration | Dynamic section capture, `JsonNodeForEachAdapter` |
| `yaml-step` | Step runtime | `StepRuntime`, `Step`, `StepContext` |
| `yaml-plugin` | Plugin system | `PluginProcessor` (APT), plugin manifest parsing |
| `yaml-csv` | CSV data source | CSV parsing for forEach expansion |
| `expression-core` | Expression engine abstraction | `ExpressionEngine`, `ExpressionEngineRegistry` |
| `expression-jq` | JQ engine | JQ evaluation against `ContextLayer.WORKING` |
| `expression-mvel` | MVEL3 engine | Typed POJO context evaluation |
| `expression-jexl` | JEXL3 engine | Template expression evaluation |
| `codegen` | YAML record code generation | `CasehubRecordCodegen` |
| `schema` | Canonical schema definitions | `CaseDefinition.yaml`, `yaml-record-mappings.yaml` |
| `engine-api` | Case definition model | `CaseDefinition`, `StageDefinition`, `BindingDefinition` |
| `engine-yaml` | YAML case parser | `CaseDefinitionYamlParser`, `CaseDefinitionSchema` |
| `engine-lsp` | LSP server | Schema-aware completion, diagnostics, hover |
