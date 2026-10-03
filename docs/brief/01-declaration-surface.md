# The Declaration Surface

*Express intent without writing code — in YAML, Java, or visual tools.*

---

## What It Is

The Declaration Surface is how intent enters the platform. Domain
experts, developers, and operations teams describe *what they want* —
cases, agents, reconciliation graphs, routing rules, playbooks — and
the platform turns those declarations into executable models.

CaseHub offers multiple declaration surfaces, each designed for a
different audience. YAML is the primary surface: a domain expert who
understands the business problem can declare a complete case
definition, agent roster, routing strategy, and reconciliation
topology without writing a line of Java. Developers who prefer typed
APIs use the Java DSL and annotations. For reconciliation graphs
specifically, an experimental TypeScript surface is in development.
All surfaces compile to the same runtime model and execute on the same
Java engine.

This is not configuration. These are complete, validated,
schema-enforced declarations that define application behaviour.
A YAML case definition is not a config file read at startup — it is
parsed, validated, cross-referenced against the SPI registry, and
compiled into an executable case plan model with the same fidelity as
hand-written Java.

---

## Key Capabilities

### YAML Case Definitions

The core declaration surface. A single YAML file can define a complete
case lifecycle: case structure, agent bindings, worker dispatch rules,
oversight gates, planning strategies, and context bindings. Progressive
complexity — a flat YAML file suffices for simple cases, while
directory conventions support complex multi-file applications.

Case definitions support:
- **Case structure** — stages, plan items, completion semantics
  (All, M-of-N, FirstWins), entry/exit sentries
- **Agent bindings** — which agents participate, capability
  requirements, routing signal weights
- **Worker dispatch** — capability matching, concurrency budgets,
  persistent vs. reinvoked sessions, dispatch modes
  (orchestrated/choreographed)
- **Oversight gates** — risk classification rules, M-of-N quorum
  requirements, escalation policies
- **Context bindings** — JQ/MVEL/JEXL expressions that connect case
  data to worker inputs and outputs
- **Goal expressions** — completion conditions with Boolean algebra
  and JQ predicates

### Java DSL and Annotations

Developers who prefer compile-time safety use Java annotations
(`@Case`, `@Binding`, `@Stage`) or the programmatic DSL to declare
case definitions. Build-time code generation validates the declaration
against the SPI registry, catching errors that YAML would defer to
startup.

Annotations support the same full feature set as YAML — the two
surfaces are peers, not a primary and a subset. A project can mix
both: YAML for business-facing case definitions, annotations for
infrastructure-level plumbing.

### Agent Descriptors in YAML

Agents are not string-described roles. Each agent on the platform has
a structured YAML descriptor covering four layers:

1. **Identity** — name, vocabulary-grounded type, organisational
   membership, classification across 12+ systems (MBTI, Big Five,
   DISC, Belbin, Enneagram, and more)
2. **Capabilities** — typed capability declarations with health
   probing (7-step sealed status hierarchy from Ready to
   BehavioralViolation)
3. **Disposition** — personality profile (Jungian cognitive function
   model), voice characteristics (register, accent, speech patterns),
   behavioural constraints
4. **Goals & constraints** — BDI-inspired goals with lifecycle states
   and temporal horizons, operational boundaries

YAML preprocessing enriches descriptors with variables, `forEach`
expansion, `when` conditions, and CSV data sources — enabling bulk
agent definitions from spreadsheet-style rosters.

### Multi-Surface Graph Declaration

For desired-state reconciliation graphs, three declaration surfaces
exist:

- **Annotations** — `@DesiredState`, `@Node`, `@DependsOn`,
  `@GraphRule` (pattern matching with `@Match`, `@DirectDep`,
  `@Reaches`, `@NotExists`, cardinality constraints),
  `@GraphInvariant` (universal quantification). Full compile-time
  validation.
- **YAML** — `META-INF/desiredstate/*.yaml` with `NodeSpecRegistry`,
  variable resolution, reusable parameterised modules with
  cross-module references.
- **TypeScript** *(POC/planned)* — `defineGraph()`, `defineLifecycle()`,
  `node()` helpers producing typed JSON envelopes. Three modules exist
  as a proof of concept; when production-ready, the TypeScript surface
  will provide a typed data structure that maps to the same schema as
  YAML — still compiled and executed by Java.

All surfaces produce the same `GoalCompiler` beans. Cross-surface
rules allow Java `@GraphRule` annotations to apply to YAML- or
TypeScript-defined graphs. Build-time validation catches unknown node
types, dangling dependencies, and cycles regardless of which surface
declared them.

### YAML-CBR Bridge (Playbooks That Learn)

Case-based reasoning integrates with the declaration surface through
playbooks: YAML-defined resolution strategies that the CBR engine
retrieves, adapts, and applies based on similarity to past cases.
Outcomes feed back into the CBR store, so playbooks improve with use.

This closes a loop that most platforms leave open: domain experts
declare the initial strategy in YAML, the platform executes it, CBR
evaluates the outcome, and future cases benefit from accumulated
experience — all without code changes.

### YAML Plugin System

For desired-state reconciliation, the YAML plugin system allows
complete resource lifecycle definitions in YAML alone. A single plugin
file declares:

- Spec schema and validation
- Actual-state detection (how to observe reality)
- Provisioning steps (how to reconcile the gap)
- Fault policies (what to do when things fail)
- CBR features (what signals to feed into learning)
- RAS situations (what drift to detect)

Built-in step primitives (`rest-call`, `json-extract`,
`compare-state`, `assert`) compose into complex provisioning
workflows. Custom compound primitives extend the vocabulary.
A declarative test framework (`*.test.yaml`) with embedded WireMock
and shell sandbox infrastructure allows plugin authors to verify their
work without writing Java tests.

No comparable system exists. Kubernetes operators require Go or Java.
Terraform providers require Go. CaseHub YAML plugins require zero
programming knowledge for complete, self-healing resource lifecycle
management.

### LSP & IDE Intelligence

The declaration surface is not just files — it's an authored
experience. A full LSP (Language Server Protocol) server for CaseHub
YAML formats provides schema-aware completion, diagnostics, hover
documentation, and refactoring support. The schema registry drives
all of it — as new YAML declaration capabilities are added to the
platform, the LSP server picks them up automatically.

An IntelliJ plugin surfaces these capabilities natively: inline
validation, navigation to referenced definitions, rename refactoring
across YAML declarations, and quick-fix suggestions when declarations
reference unknown types or misspell strategy names.

This makes the "YAML is the declaration surface" promise practical.
Domain experts don't need to memorise schema structures — the IDE
tells them what's valid, suggests completions, and catches errors
before anything runs.

### yaml-core — The Composition Engine

Underneath every YAML surface sits yaml-core: a pure Java YAML
processing engine providing variable resolution, for-each expansion,
truthiness evaluation, CSV parsing, and a module system. Zero external
dependencies. J2CL-transpilable for browser use.

yaml-core is shared infrastructure — the engine's case definitions,
the desiredstate's plugin system, and the pages framework's dashboard
declarations all build on the same composition primitives. When
yaml-core gains a feature (e.g. conditional `when` blocks), every
declaration surface gains it simultaneously.

### Binding Expressions

Three expression engines connect declarations to runtime data:

- **JQ** — the default, evaluating against the working context layer.
  Ideal for JSON transformation and data extraction.
- **MVEL** — typed POJO context evaluation. Ideal for business rules
  with compile-time type checking.
- **JEXL** — template expression evaluation. Ideal for string
  interpolation and dynamic content.

Per-expression language override via `{lang: expr}` syntax allows
mixing engines within a single case definition. Config and secret
injection via `$config` and `$secret` scopes means expressions can
reference business configuration and credentials without hard-coding
values.

---

## What Makes It Different

### vs. BPMN (Camunda, jBPM)

BPMN is XML-based, diagram-first, and tied to a specific execution
model (directed-graph workflow). Modifying a BPMN process requires a
graphical editor or XML manipulation. CaseHub's YAML is text-first —
it lives in version control, diffs cleanly, reviews in pull requests,
and generates from templates. More importantly, YAML declares
*intent*, not *control flow*. The platform's Blackboard Architecture
decides how to execute the intent, rather than following a prescribed
graph of steps.

### vs. Python (LangChain, CrewAI, AutoGen)

Python agent frameworks require programming to define agent behaviour.
The declaration IS the code — there is no separation between what the
system should do and how it does it. CaseHub separates declaration
(YAML) from execution (Java). A domain expert changes routing
strategy by editing a YAML file; the enterprise Java platform
underneath handles execution, tenancy, audit, and accountability
without any changes to code.

### vs. JSON Configuration

Many platforms use JSON for configuration — OpenAI function calling
schemas, AWS Step Functions state machines, Temporal workflow
definitions. These are typically configuration of a single capability,
not a declaration surface that spans an entire platform. CaseHub's
YAML covers cases, agents, routing, reconciliation, playbooks,
plugins, and agent identity through one consistent declaration model.

### The Real Differentiator

The declaration surface is not just "YAML support." It is the
principle that domain knowledge belongs to domain experts and
execution infrastructure belongs to the platform. Every capability
added to CaseHub — from oversight gates to CBR learning to
desired-state reconciliation — is accessible through YAML. The
surface grows as the platform grows. A domain expert who learned YAML
case definitions can declare agent routing, reconciliation graphs,
and fault recovery playbooks using the same patterns and conventions.

---

## How Deep It Goes

The Declaration Surface spans multiple repos and hundreds of modules:

| Component | Scope | Scale |
|-----------|-------|-------|
| Engine YAML DSL | Case definitions, bindings, routing, oversight | 68 modules (44 non-example) |
| Engine annotations | `@Case`, `@Binding`, `@Stage`, build-time codegen | Same modules, annotation processing layer |
| Desiredstate surfaces | Annotations, YAML, TypeScript (POC) | 37 modules |
| Desiredstate YAML plugins | Zero-Java resource lifecycle | Plugin parser, validator (Levenshtein suggestions), provisioner, test framework |
| Eidos descriptors | 4-layer agent identity in YAML | 14 modules, 303 Java source files |
| Eidos YAML preprocessing | Variables, forEach, when, CSV data sources | Integrated with platform yaml-core |
| Expression engines | JQ, MVEL, JEXL with scope injection | 3 engines in platform expression registry |
| Playbook bridge | CBR-integrated YAML strategies | Engine CBR modules |

Three expression engines. Three+ declaration surfaces (YAML, Java
DSL, annotations, with TypeScript planned). Schema validation on all
surfaces. Build-time error detection. Progressive complexity from flat
files to multi-directory applications.

---

## What It Gains from the Platform

Every declaration surface resolves through the same infrastructure:

- **One CDI registry** — a YAML case definition and an annotated Java
  case definition register in the same `CaseDefinitionRegistry`. They
  are indistinguishable at runtime.
- **One tenancy model** — every declaration is tenant-scoped. A YAML
  plugin for tenant A cannot see or affect tenant B's resources.
- **One expression engine registry** — JQ, MVEL, and JEXL expressions
  in YAML case definitions use the same `ExpressionEngineRegistry` as
  binding expressions in annotated cases.
- **One validation pipeline** — build-time validation catches errors
  (unknown types, dangling references, cycles, schema violations)
  regardless of which surface produced the declaration.
- **One SPI resolution** — `NamedStrategy` convention from platform
  means all strategy types (routing, decomposition, planning) resolve
  the same way whether referenced from YAML or Java.

This consistency means a new declaration surface — like the planned
TypeScript DSL — automatically inherits the entire platform's
validation, tenancy, expression evaluation, and SPI resolution without
reimplementation.

---

## Connections to Other Areas

The Declaration Surface is the entry point. Every other capability
area receives its instructions through declarations:

- **[Agentic Orchestration](02-agentic-orchestration.md)** —
  orchestration patterns are selected and configured through case
  definition bindings
- **[AI Knowledge & Learning](03-ai-knowledge-learning.md)** — CBR
  playbooks are declared in YAML, feeding the learning loop
- **[Enterprise Execution](04-enterprise-execution.md)** — case
  definitions drive the execution engine; oversight gates and routing
  are declared, not coded
- **[Accountability & Governance](05-accountability-governance.md)** —
  protocol enforcement rules and compliance requirements are
  declaration-driven
- **[Convergence & Situational Awareness](06-convergence-situational-awareness.md)** —
  desired-state graphs and YAML plugins are declarations that drive
  reconciliation
- **[Agent Identity & Cognition](07-agent-identity-cognition.md)** —
  agent descriptors are YAML declarations consumed by the identity
  system
- **[The Shared Foundation](08-shared-foundation.md)** — expression
  engines, tenancy, and SPI resolution are the infrastructure that
  makes all declarations work
- **[The Application Surface](09-application-surface.md)** — visual
  builders provide a graphical alternative to YAML authoring

---

## Architecture

![Declaration Surface Architecture](../images/brief/01-declaration-surface.svg)

The declaration surface spans three audiences and converges on one
runtime model. YAML files, annotated Java classes, and (planned)
TypeScript definitions all compile through surface-specific parsers
into the same CDI bean registry. The runtime engine consumes beans —
it does not know or care which surface produced them. Expression
engines, validation, and SPI resolution are shared infrastructure
provided by the platform foundation.
