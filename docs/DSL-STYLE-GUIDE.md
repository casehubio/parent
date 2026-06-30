# CaseHub DSL Style Guide

How we design fluent Java APIs across the CaseHub platform, with reference to
LangChain4j and Quarkus Flow as peer influences.

---

## Principles

1. **Code should read like a declaration, not a construction**
2. **Pattern name is the entry point** — the first thing you read tells you what you're building
3. **Concerns attach to what they modify** — transformations, conditions, and policies sit next to the thing they govern
4. **Overload for expressiveness** — JQ strings for config-like use, typed predicates for code, evaluator instances for reuse
5. **Defaults are opinionated, overrides are easy** — pre-composed builders provide sensible defaults; any concern can be swapped

---

## The Three Influences

### LangChain4j — Pattern-Named Builders

LangChain4j's agentic DSL uses the workflow pattern as the entry point. You
know what you're building from the first token.

```java
// Sequential pipeline
SequentialAgentService.builder()
    .subAgents(writer, editor, reviewer)
    .outputName("story")
    .build()

// Loop with exit condition
LoopAgentService.builder()
    .subAgents(scorer, editor)
    .maxIterations(5)
    .exitCondition(scope -> scope.readState("score", 0.0) >= 0.8)
    .build()

// Conditional routing
ConditionalAgentService.builder()
    .subAgents(scope -> scope.readState("category") == MEDICAL, medicalExpert)
    .subAgents(scope -> scope.readState("category") == LEGAL, legalExpert)
    .build()

// Supervisor (LLM-driven)
SupervisorAgentService.builder(PLANNER_MODEL)
    .subAgents(classifier, medicalExpert, legalExpert, technicalExpert)
    .maxAgentsInvocations(5)
    .outputName("result")
    .build()
```

**What works well:**
- Pattern type is immediately visible — `SequentialAgentService`, `LoopAgentService`
- Agents compose — a `LoopAgentService` can be a sub-agent of a `SequentialAgentService`
- Shared state (`Cognisphere`) is implicit — agents write to `outputName` keys
- Typed and untyped variants — `builder()` vs `builder(TypedInterface.class)`

**What we learn from this:**
- Name the builder after what you're building, not after the mechanism
- Keep agent declaration separate from workflow composition
- Support nesting — any workflow can be a component of another workflow

**Declarative alternative (annotations):**

```java
@SequenceAgent(outputName = "story", subagents = {
    @Subagent(agentClass = CreativeWriter.class, outputName = "story"),
    @Subagent(agentClass = StyleEditor.class, outputName = "story")
})
public interface StoryCreator {
    @Agent
    String write(@V("topic") String topic);
}
```

LangChain4j offers both fluent and annotation-based declaration. CaseHub
similarly offers builder APIs and YAML case definitions.

---

### Quarkus Flow FuncDSL — Tasks as Composable Steps

Quarkus Flow's FuncDSL treats a workflow as a sequence of composable task steps.
Each step type has its own factory method with data flow transformations attached
directly.

```java
// Sequential with data transformation
workflow("call4papers").tasks(
    function("validate", (Proposal p) -> p, Proposal.class)
        .inputFrom((Submission s) -> new Proposal(s), Submission.class),
    function("score", (Proposal p) -> calculateScore(p), Proposal.class)
        .outputAs((Integer s) -> new ProposalScore(s, s >= 7)),
    http("notify").POST().body("${$context}").endpoint(notifyUrl)
).build()

// Parallel fan-out
workflow("parallel-check").tasks(
    fork("checkBoth",
        http("inventory").POST().endpoint(inventoryUrl),
        http("credit").POST().endpoint(creditUrl)
    )
).build()

// Conditional routing
workflow("route").tasks(
    switchWhenOrElse(
        (Order o) -> o.total() > 100,
        "expedited", "standard", Order.class),
    post("expedited", url + "/expedite").then(FlowDirectiveEnum.END),
    post("standard", url + "/standard")
).build()

// Loop with forEach
workflow("process-orders").tasks(
    forEach(OrdersPayload::orders,
        tasks(post("$item.id", processUrl).exportAsTaskOutput())
    )
).build()

// Event-driven with human-in-the-loop
workflow("newsletter").tasks(
    agent("draft", drafter::write, Request.class),
    emitJson("ready", "review.required", Draft.class),
    listen("review", toOne(consumed("review.done"))),
    switchWhenOrElse(h -> ok(h), "send", "revise", Review.class),
    function("revise", editor::edit, Review.class).then("ready"),
    consume("send", draft -> mail.send(draft), Draft.class)
).build()
```

**What works well:**
- Task steps read top-to-bottom like a procedure
- Data flow transformations (`.inputFrom()`, `.outputAs()`, `.exportAs()`) attach directly to the task they modify
- Static imports (`set()`, `function()`, `fork()`, `listen()`, `switchWhenOrElse()`) create a vocabulary
- JQ expressions and Java lambdas interchangeably — `.inputFrom("$.cart")` or `.inputFrom((Cart c) -> c.items())`
- Event handling is a first-class step type, not a separate mechanism

**What we learn from this:**
- Transformations should be co-located with the step, not declared separately
- A step vocabulary via static imports makes the DSL read like a domain language
- Support both JQ strings and typed lambdas for the same operation
- Events and conditions are steps in the flow, not metadata on the flow

---

### CaseHub — Nested Builders with Expression Overloads

CaseHub's existing builders follow a nested composition pattern. Each domain
concept (case, worker, binding, goal, stage) has its own builder, and they
compose by nesting.

```java
// Case definition with all components
CaseDefinition.builder()
    .namespace("review")
    .name("DocumentReview")
    .version("1.0.0")
    .capabilities(
        Capability.builder()
            .name("analyse")
            .inputSchema("{ doc: .document }")
            .outputSchema("{ analysis: .analysis }")
            .build())
    .workers(
        Worker.builder()
            .name("analyser")
            .capabilities(analyseCap)
            .function(new WorkerFunction.Sync(input -> analyse(input)))
            .build())
    .bindings(
        Binding.builder()
            .name("on-document-ready")
            .capability(analyseCap)
            .on(new ContextChangeTrigger(".document != null"))
            .when(".status == \"pending\"")
            .build())
    .goals(
        Goal.builder()
            .name("reviewComplete")
            .condition(".review.complete == true")
            .kind(GoalKind.SUCCESS)
            .build())
    .completion(GoalExpression.allOf(successGoal))
    .build()
```

**Expression overloads — the CaseHub convention:**

CaseHub consistently offers three ways to express conditions, letting the
developer choose the right level of abstraction:

```java
// JQ string — config-like, readable, serialisable to YAML
Goal.builder().condition(".done == true")

// Typed predicate — compile-time safe, IDE-navigable
Goal.builder().condition(ctx -> ctx.query(".done", Boolean.class))

// ExpressionEvaluator — reusable, testable independently
Goal.builder().condition(new JQExpressionEvaluator(".done == true"))
```

This three-way overload appears consistently across:
- `Goal.condition()`
- `Stage.entryCondition()` / `.exitCondition()`
- `Binding.when()`
- `Milestone.completionCriteria()` / `.entryCriteria()`

**Stage builder — fluent with factory shortcuts:**

```java
// Full builder
Stage.builder("intake")
    .entryCondition(ctx -> true)
    .exitCondition(".stage == \"complete\"")
    .autocomplete(true)
    .repeatable(true)
    .binding("on-docs-received")
    .build()

// Factory shortcut for common case
Stage.alwaysActivate("intake")
    .withBinding("on-docs-received")
    .withBinding("on-approval")
```

**Work items in Quarkus Flow — CaseHub's extension:**

```java
workflow("approval").tasks(
    workItem("legalReview")
        .title("Legal review required")
        .candidateGroups("legal-team")
        .priority(WorkItemPriority.HIGH)
        .payloadFrom((Draft d) -> d.toJson())
        .buildTask(Draft.class),
    function("finalise", this::archive, String.class)
).build()
```

**What works well:**
- Nested builders mirror the domain hierarchy — a case *contains* workers, bindings, goals
- Expression overloads give developers choice without API proliferation
- Factory shortcuts (`Stage.alwaysActivate()`) reduce boilerplate for common patterns
- Accumulating methods (`.panel()` singular + `.panels()` varargs) build lists incrementally
- `WorkItemsFlow` extends FuncDSL naturally — human tasks are just another step type

---

## CaseHub DSL Conventions

These conventions apply to all new builder APIs across the platform.

### 1. Entry Point Names the Thing

The builder's factory method or class name should tell you what you're building.

```java
// Good — I know what I'm building
supervisor(chatModel)
debate()
voting()
CaseDefinition.builder()
Stage.builder("intake")
workflow("newsletter")

// Bad — I have to read the arguments to know
ExecutionModel.of(new LlmSelectedRouting<>(), ...)
new GenericBuilder().setType("supervisor")
```

### 2. Three-Way Expression Overloads

Wherever a condition, predicate, or expression is accepted, provide all three:

```java
.terminate(goalReached(".done == true"))                // JQ string
.terminate(goalReached(ctx -> ctx.isComplete()))         // typed predicate
.terminate(goalReached(evaluator))                       // evaluator instance
```

This is a platform convention, not a per-module choice. It appears in engine
(Goal, Stage, Binding, Milestone), work (WorkItem conditions), and should
appear in blocks (agentic orchestration).

### 3. Static Factory Imports for Vocabulary

Concern implementations should be importable as a vocabulary:

```java
import static io.casehub.blocks.agentic.Routing.*;
import static io.casehub.blocks.agentic.Activation.*;
import static io.casehub.blocks.agentic.Termination.*;

orchestration("pipeline")
    .route(llmSelected(chatModel))
    .activate(onPredecessorComplete())
    .terminate(goalReached(".pipeline.done"))
    .build()
```

Like Quarkus Flow's `set()`, `function()`, `fork()`, `listen()` — the static
imports create a domain language.

### 4. Defaults Are Opinionated

Pre-composed builders provide sensible defaults. Override only what differs.

```java
// Supervisor defaults: routing=llmSelected, activation=onResult,
// aggregation=passThrough, decomposition=none, termination=llmDecides
supervisor(chatModel)
    .agents(reviewer, implementor)
    .terminate(goalReached(".complete"))    // override just termination
    .build()
```

Document the defaults in the builder's Javadoc. A developer should be able to
use the pre-composed builder without knowing the five concerns exist.

### 5. Transformations Attach to What They Modify

Following Quarkus Flow's `.inputFrom()` / `.outputAs()` pattern — data
transformations sit on the step they transform, not in a separate declaration.

```java
// Good — transformation is co-located
function("score", scorer::evaluate, Proposal.class)
    .inputFrom((Submission s) -> s.toProposal())
    .outputAs((Score s) -> Map.of("score", s.value()))

// Bad — transformation declared elsewhere
function("score", scorer::evaluate, Proposal.class)
// ... 20 lines later ...
transform("score", s -> Map.of("score", s.value()))
```

### 6. Nesting for Hierarchy, Chaining for Sequence

Use nested builders when the structure is hierarchical (case contains workers,
HTN task contains subtasks). Use method chaining when the structure is
sequential or configurational.

```java
// Hierarchical — nested builders
htn()
    .task(compound("analyse",
        method(when(".hasData"), sequence(extract, transform)),
        method(when(".needsCollection"), sequence(collect, extract, transform))
    ))
    .build()

// Sequential/configurational — method chaining
supervisor(chatModel)
    .agents(a, b, c)
    .maxInvocations(10)
    .terminate(goalReached(".done"))
    .build()
```

### 7. Composability — Any Pattern Can Be a Component

Following LangChain4j's model — a composed workflow should be usable as an
agent in another workflow:

```java
var reviewLoop = loop()
    .agents(reviewer, editor)
    .exitCondition(ctx -> ctx.readState("score") >= 0.8)
    .build();

var pipeline = sequence()
    .agents(drafter, reviewLoop, publisher)
    .build();
```

### 8. Terminal `.build()` Returns an Immutable Instance

All builders terminate with `.build()`. The returned instance is immutable.
Validation happens at build time — missing required fields throw
`IllegalStateException` with a descriptive message.

---

## Pattern: Pre-Composed vs Compositional

New execution model APIs should offer both levels:

**Pre-composed** — pattern name as entry point, defaults for all five concerns:
```java
supervisor(chatModel).agents(...).build()
debate().debaters(...).judge(...).build()
voting().evaluators(...).strategy(majorityVote()).build()
```

**Compositional** — explicit concern selection for custom patterns:
```java
orchestration("custom")
    .route(bidEvaluated(costWeighted()))
    .decompose(goapGraph(capabilities))
    .activate(onPredecessorComplete())
    .aggregate(collectAll())
    .terminate(goalReached(".done"))
    .build()
```

The pre-composed builders are implemented *on top of* the compositional
builder — they're convenience, not a separate mechanism. A `supervisor()` call
returns a builder pre-configured with `route(llmSelected(...))`,
`activate(onResult())`, etc.

---

## Anti-Patterns

### Don't expose implementation in the API

```java
// Bad — I'm constructing implementation classes
ExecutionModel.of(
    new LlmSelectedRouting<>(chatModel),
    new IdentityDecomposition<>(),
    new OnExplicitDispatch<>(),
    new PassThrough<>(),
    new GoalReached<>(condition)
)

// Good — static factories hide implementation
supervisor(chatModel)
    .terminate(goalReached(condition))
    .build()
```

### Don't separate configuration from the thing it configures

```java
// Bad — routing config is disconnected from the builder
var routing = RoutingConfig.builder().strategy("llm").model(chatModel).build();
var model = ExecutionModel.builder().routingConfig(routing).build();

// Good — routing is a method on the builder with a factory
orchestration("pipeline").route(llmSelected(chatModel)).build()
```

### Don't use string constants where types would do

```java
// Bad — stringly typed
.strategy("MAJORITY_VOTE")

// Good — static factory or enum
.strategy(majorityVote())
```

### Don't force all five concerns when defaults suffice

```java
// Bad — I have to specify everything even for a simple supervisor
orchestration("review")
    .route(llmSelected(chatModel))
    .decompose(none())
    .activate(onResult())
    .aggregate(passThrough())
    .terminate(llmDecides())
    .build()

// Good — pre-composed with defaults
supervisor(chatModel).agents(reviewer, editor).build()
```

---

## Summary

| Convention | Source | Applied Where |
|-----------|--------|--------------|
| Pattern name as entry point | LangChain4j | All execution model builders |
| Tasks as composable steps | Quarkus Flow | FuncDSL integration, step-based workflows |
| Three-way expression overloads | CaseHub | Every condition/predicate across the platform |
| Static factory imports for vocabulary | Quarkus Flow | Concern implementations (routing, activation, termination) |
| Nested builders for hierarchy | CaseHub | Case definitions, HTN task trees |
| Transformations co-located with steps | Quarkus Flow | Data flow in workflows |
| Pre-composed + compositional levels | All three | Execution model API surface |
| Composability (pattern as component) | LangChain4j | Any workflow usable as agent in another |
