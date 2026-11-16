# Playbook direction: language, levels and tests

Status: proposal, 2026-11-16. Follows the cross-repo review in `code-review-notes.md` (finding IDs such as P32 refer to that file). Scope: platform, connectors, engine, agency, ops.

**ID scheme:** language direction items are `LD-1` … `LD-10`; work steps are `WS-1` … `WS-8`; tensions are `TN-1` … `TN-7`. Finding IDs (P32, G6, etc.) come from `code-review-notes.md`. **Epic:** casehubio/parent#540. GitHub issue numbers are recorded in the cross-reference table at the end of this document.

## Goal

Onboarding happens through playbooks. The examples are organised in levels (one new concept each) and layers (one repo each). Every example teaches, documents and tests at the same time.

The levels have a third job: they measure whether the language is good. If a model cannot write a passing playbook for a level, the language or its feedback is the problem.

## Language direction

**LD-1 One semantics.** Four executors exist (platform interpreter, engine compiler path, pages scenario executor, TypeScript port). The levels are the conformance suite: each level runs on every executor that claims it, with zero expected failures. (P21, P32, P41, G6, G7, PG8)

**LD-2 Design for the LLM author.** The validator is the user interface. Expose `validate-playbook` as an MCP tool returning structured, located errors with suggestions. Serve the step catalogue per level so a model sees a small vocabulary, not 600 operations.

**LD-3 Types from the APIs.** Generated steps already have Java input and output types. Type each `capture` from them and check `${...}` references before run. Two sub-problems block this today: shaped plugins use a single all-optional record per operation, so the editor and LLM cannot see which fields are required — a per-subject variant schema would keep the pleasant surface and restore precision (P31). And `GraphQLResolverProcessor` skips `@ContextParam` parameters, so operations that take `tenancyId` from context get none when called as steps (P27). (P37)

**LD-4 Values are data, not text.** Bind variables into compiled conditions instead of substituting them into the condition string. Model output and webhook fields flow through playbooks. (P33)

**LD-5 Governance in the language.** Steps carry an effect class (read, write, irreversible, spends money) derived from annotations. `confirm:` and `approve:` are decorators that compile to the one engine gate. A playbook can then be summarised statically: what it may do and who must agree. (A1, C1, G21, P28)

**LD-6 Shaped for CBR.** A retained case stores the playbook, its bindings and the outcome. That needs stable step identity, versioned and namespaced step names. (P29)

**LD-7 Finish what is declared.** `on-error` handlers, `transform`, nested `capture` and `invoke:` either work or are removed. (P34, P35, P36, P40)

**LD-8 Specify decorator semantics.** The decorators that do execute have unspecified or silently wrong behaviour. Each needs a stated contract and a conformance test before levels can rely on them. (P38, P39)
   - `timeout`: a step that ignores interruption blocks forever; timeout wraps retry, so it bounds all attempts together — document or change.
   - `loop`: stops silently at 1,000 iterations and reports success.
   - `retry`: retries every failure including validation errors; uncategorised failure is retryable by default.
   - `parallel`/`forEach parallel`: no fail-fast, no concurrency bound.
   - `cancel`: clears the thread's interrupt flag in `finally`, swallowing a real interrupt.
   - `background`: discards the result and any error.
   - Skipped guard (`when: false`): returns the same empty success as an executed step — callers cannot distinguish skipped from executed.

**LD-9 Trust model.** `process`, `script`, `rest`, MVEL expressions, `env()` and `systemProperty()` make a playbook equivalent to arbitrary code. Before tenants or LLMs author playbooks, state: who may author at each trust tier, what step types and variable sources are available per tier, and what egress is permitted. The validator MCP tool (LD-2) hands an LLM a language that can run shell commands; that must not be the default surface. (P26, P42)

**LD-10 Durability.** The platform interpreter does not survive a restart. Engine has durable execution (event log, scheduler-backed workers, replay). State which path is the canonical durable path, and whether the platform interpreter is intentionally ephemeral or expected to gain durability. This is the main comparison axis against Temporal, Step Functions and Kestra. (P25)

## Canonical form

One file shape and one key style for the whole corpus, not per-example. Today there are two shapes (header + bare step list vs top-level `steps:`/`pools:`), mixed camelCase and kebab-case keys, and JSON Schema embedded as a string in YAML. The guide says `if` for guards; code and examples use `when`. Guide examples use bare `${risk}`; the resolver rejects bare references. `at`, `from`, `cancel`, `background` decorators are undocumented. `invoke:` is documented but throws.

Decide: one file shape, one key case (kebab-case matches YAML convention), one guard keyword. Reconcile the guide against the code — the guide is what an LLM author and the validator will consume. (P23, P24, P40)

## Levels and layers

Two axes. One business scenario runs through all five layers so the learner watches the same story grow.

| Layer | The level adds | Needed first |
|---|---|---|
| Platform | Steps, captures, flow control, coordination, agent sessions | One runner in main code; LD-7 and LD-8 |
| Connectors | A real-world action with confirmation | Confirmation that fires |
| Engine | The playbook as a durable worker in a case, with a human task | Plugin steps accepted on the engine path |
| Agency | A debate or vote as a step, with oversight | Patterns exposed as steps; governance compiled |
| Ops | Deployment through desired state with approval | Step generation on for ops; approval on every path |

Each example has:

- **A header**: `level`, `layer`, `teaches`, `builds-on`, and `rules` (see below). The tutorial index is generated from headers.
- **A paired test** that asserts the rules.
- **A negative twin** wherever a rule forbids something.
- **One file shape and one key style** (see Canonical form above).

## Tests must assert the business rules

### The problem

Asked to test a playbook, a model checks that it runs. On `main`, six of the eight execution tests for the agent series assert only `result.succeeded == true`. Such a test passes when the classifier returns the wrong class, when the approval is skipped, and when the payment goes to the wrong account. It teaches nothing and integrates nothing.

A good test is the specification of the example. A reader should learn what the playbook guarantees by reading the test alone.

### State the rules in the example

A model tests what it is told matters. Put the business rules in the header so they are explicit and countable:

```yaml
# level: 3   layer: connectors
# teaches: confirmation before an irreversible action
# rules:
#   R1: a payment over the joint-account limit requires confirmation from the second holder
#   R2: without confirmation, no payment is made
#   R3: the confirmed payment is for the requested amount and payee
#   R4: the confirmation and the payment are both recorded with the acting identity
```

### What a test must contain

1. **One named test per rule**, with the rule ID in the name.
2. **Assertions on outcomes**: captured values, the side effect that happened (or did not), the record written, who acted.
3. **A negative case for every "requires" or "must not"**: the same playbook with the condition unmet, asserting refusal and asserting that the side effect did not occur.
4. **Boundary cases** where a rule has a threshold: just under, at, just over.
5. **Simulated inputs chosen to discriminate.** If every simulated response leads to the same branch, the test proves nothing about the branch.
6. **No test whose only assertions are `succeeded` or `stepCount`.**

### Before and after

Before:

```yaml
- name: "payment playbook runs"
  steps:
    - run-playbook: 06-joint-account-payment.yaml
      capture: result
    - assertThat: result.succeeded
      equals: true
```

After (assertion paths are illustrative; use what the test engine exposes):

```yaml
- name: "R1+R3: over-limit payment is made once the second holder confirms"
  steps:
    - run-playbook: 06-joint-account-payment.yaml
      with: { amount: 1500, payee: "ACME Ltd" }
      capture: result
    - assertThat: result.captures.confirmation.outcome
      equals: CONFIRMED
    - assertThat: result.captures.payment.amount
      equals: 1500
    - assertThat: result.captures.payment.payee
      equals: "ACME Ltd"

- name: "R2: over-limit payment is refused without confirmation"
  simulate: { confirmation: DENIED }
  steps:
    - run-playbook: 06-joint-account-payment.yaml
      with: { amount: 1500, payee: "ACME Ltd" }
      capture: result
    - assertThat: result.captures.payment
      isAbsent: true
    - assertThat: result.error.type
      equals: confirmation-denied
```

### Make it enforceable, not just advised

Instructions help; checks hold.

- **Lint**: reject a test file that has no assertion other than `succeeded`/`stepCount`, or that lacks a test for each rule ID in the example's header.
- **Mutation check**: for each rule, a small set of mutations (remove the gate, change the threshold, swap the branch, alter the simulated response). At least one test must fail for each. A suite that survives a mutation does not test that rule.
- **Coverage of the playbook**: report branches and steps never executed by any test.
- **Review order**: write the rules, then the tests, then the playbook. A model given the tests first writes to them.

### Instruction block for a model writing tests

> You are writing tests for a playbook that is also a teaching example. "It ran" is not a test.
> 1. Read the `rules` in the header. If there are none, write them first and stop for review.
> 2. Write one named test per rule; put the rule ID in the name.
> 3. Assert outcomes: values produced, actions taken or not taken, records written, who acted.
> 4. For every rule that requires or forbids something, add a test where the condition is unmet and assert the refusal and the absence of the side effect.
> 5. Choose simulated inputs that would make a wrong implementation fail.
> 6. Before finishing, name one change to the playbook that would break each rule and confirm a test would catch it.

## The metric

For each level: give a model the task, that level's catalogue and the earlier levels as examples. It must produce a playbook that passes the level's tests. Track first-attempt pass rate per level. Low rates show where the language or the validator's feedback needs work. The same harness, run on test-writing, tracks mutation score.

## Tensions

Items in this document that pull against each other. Resolve before or during the work, not after.

**TN-1 One semantics (LD-1) vs durability (LD-10).** If the platform interpreter is ephemeral and engine is durable, coordination-heavy levels (barrier, quorum, deadline) will have different failure modes on each executor. Either the interpreter gains checkpointing, or the conformance suite excludes coordination from the interpreter, or "one semantics" means "one language, different guarantees" — state which.

**TN-2 LLM authoring (LD-2) vs trust model (LD-9).** The validator MCP tool makes it easy for a model to write playbooks. The default step catalogue includes `process`, `script`, `rest` and MVEL expressions, which are code execution. The tool must serve a trust-filtered catalogue, not the full one, or the first LLM-authored playbook is a shell.

**TN-3 Every API is a step vs tenant isolation (LD-3, P27, P28).** Generated steps call the SPI directly — no `@RolesAllowed`, no `@ContextParam` tenant. The "every API is a step" strategy scales the number of unguarded entry points. Fix the generator before scaling the step count.

**TN-4 Shaped plugin UX vs schema precision (LD-3, P31).** Shaped plugins read like natural language (`speaker register: Alice`), which is the differentiator. Per-subject variant schemas would give the editor and LLM correct required fields but add complexity for the step author. A code generator that emits variants from the existing `operation` enum would resolve both.

**TN-5 Finish what is declared (LD-7) vs decorator semantics (LD-8).** LD-7 covers features that do nothing. LD-8 covers features that execute but behave incorrectly. Both must be done before levels rely on them, and they compete for the same window. Decorator semantics is higher priority: a level that uses `parallel` or `retry` with today's behaviour silently passes tests that should fail.

**TN-6 Governance decorators (LD-5) vs work identity (W1/W2).** Effect classes and approval decorators compile to engine gates, and engine gates are delivered as WorkItems — but work does not check who claims or completes them. The governance language is only as strong as the weakest link. Fixing W1/W2 is a prerequisite for governance decorators to mean anything at runtime.

**TN-7 The metric vs the validator (LD-2).** If the validator gives good enough feedback, the metric measures the validator's quality, not the language's clarity. That may be fine — a good validator is the goal — but also track first-attempt pass rate *without* the validator to isolate language design from tooling quality.

## Positioning

Lead with coordination + agents + tests-in-language, not "YAML workflows." The unique combination is coordination primitives (quorum, race, barrier, correlation, deadlines) + agent sessions as first-class steps + simulation + tests in the same language. No YAML workflow tool offers all of these.

Claim type safety only after static data-flow checking is implemented (LD-3). Today's checking is schema-validated with runtime contracts — accurate, and already stronger than most competitors, but "type safe" implies compile-time guarantees that do not yet exist.

Pick one execution path as canonical and state durability plans (LD-10). An enterprise buyer compares against Temporal and Step Functions; they will ask about restarts in the first conversation.

## Generator quality

`GraphQLResolverProcessor` (P30) is 2,969 lines emitting Java with `println`, while the Spring generators use JavaPoet. It is central to the "every API is a step" strategy and the hardest file to change safely. If step count scales to 600 operations, the generator must be reliable. Consider migrating to JavaPoet or a template engine before scaling.

## Repo routing

Which repo each finding and work item lands in. Items that appear in multiple columns need coordination across sessions.

| Step | Issue | Platform | Connectors | Engine | Agency | Work |
|---|---|---|---|---|---|---|
| WS-1 Canonical runner + inert features | #541 | P32, P34, P35, P36, P40 | | | | |
| WS-2 Decorator semantics | #542 | P38, P39 | | | | |
| WS-3 Trust model | #543 | P26, P42 | | | | |
| WS-4 Canonical form | #544 | P23, P24, P40 | | | | |
| WS-5 Rules headers + lint | #545 | existing levels | | | | |
| WS-6 Types + validator + generator | #546 | P27, P30, P31, P37 | | G7 | | |
| WS-7 Engine accepts plugin steps | #547 | | | G6 | | |
| WS-8 Governance decorators | #548 | P28 | C1 | G21 | A1, A2 | W1, W2 |

**By repo:**

- **Platform** (WS-1 to WS-6): nearly all language work lives here. The canonical runner, decorator fixes, trust model, canonical form, levels infrastructure, type system, generator and validator MCP tool. This is the critical path — nothing downstream moves until the platform runner and decorator semantics are solid.
- **Engine** (WS-6 to WS-7): wire `ExecutionScope` and expression engine into the step-file bridge (G7); accept plugin steps on the compiler path (G6) so engine can run the same playbooks as the platform interpreter. Blocked on platform WS-1.
- **Connectors** (WS-8): confirmation must actually fire (C1). The `@RequiresConfirmation` annotation needs a working generator or a risk classifier that reads the step's confirmation tier. Blocked on engine gates (G21) and platform governance decorators (LD-5).
- **Agency** (WS-8): pattern governance specs (A1) and annotation processors (A2) must compile into engine gates and trust routing. Blocked on engine gates and platform governance decorators.
- **Work** (WS-8): W1/W2 — lifecycle API must derive actor and claimant from the authenticated principal, not from request parameters. This is the prerequisite for governance decorators meaning anything at runtime (TN-6). Can start independently.

**Cross-cutting** items that do not belong to one repo:
- Durability decision (LD-10): architectural, affects what "one semantics" means for platform vs engine.
- Positioning (lead with coordination + agents + tests): affects docs, README and marketing across all repos.
- Levels that span layers: a single business scenario runs through platform → connectors → engine → agency → ops. The level definitions live in platform, but the layer-specific tests live in each repo.

## Order of work

**WS-1** Canonical runner in main code; finish or remove the declared-but-inert features (LD-7).
**WS-2** Specify and fix decorator semantics (LD-8). Each decorator gets a stated contract, a conformance test, and either a fix or a documented limitation.
**WS-3** Trust model decision (LD-9): who may author, what steps and sources are available per tier. Prerequisite for the validator MCP tool in WS-6.
**WS-4** Canonical form: one file shape, one key case, reconcile the guide against the code.
**WS-5** Rules headers, the lint and the mutation check on the existing platform levels.
**WS-6** Typed captures, shaped plugin schemas (P31), generator fixes (P27, P30), and the validation MCP tool; then the authoring metric.
**WS-7** Engine path accepts plugin steps; add engine, agency and ops levels.
**WS-8** Governance decorators and negative twins at every level that has a gate. Requires W1/W2 fix in work (TN-6).

WS-1 to WS-5 are platform-only. WS-6 starts touching the generator (platform) and engine. WS-7 and WS-8 fan out. Work on W1/W2 can start in parallel with any platform step.

## Cross-reference: findings → direction → issues

Every playbook-related finding from `code-review-notes.md`, the direction item that addresses it, the work step where it is delivered, and the GitHub issue (blank until created).

| Finding | Summary | Direction | Work step | Issue |
|---|---|---|---|---|
| P21 | Three execution paths, different languages | LD-1 | WS-1 | #541 |
| P22 | Gate test expects shipped examples to fail; 4 tests for 76 examples | — | WS-5 | #545 |
| P23 | Two file shapes, mixed key case | — | WS-4 | #544 |
| P24 | Guide claims parse-time type checks; code checks at runtime | LD-3 | WS-4 | #544 |
| P25 | No durability — playbook doesn't survive restart | LD-10 | cross-cutting | #540 |
| P26 | Trust model — playbook equivalent to code | LD-9 | WS-3 | #543 |
| P27 | Generated steps skip @ContextParam tenancyId | LD-3 | WS-6 | #546 |
| P28 | Generated steps bypass @RolesAllowed | LD-5 | WS-8 | #548 |
| P29 | Step name collision from derivePluginName | LD-6 | WS-6 | #546 |
| P30 | GraphQLResolverProcessor: 2,969 lines of println | — | WS-6 | #546 |
| P31 | Shaped plugins: all-optional fields, runtime-only required | LD-3 | WS-6 | #546 |
| P32 | Only runner is in test module, no ExecutionScope | LD-1 | WS-1 | #541 |
| P33 | Template-then-evaluate conditions (injection, Norway) | LD-4 | WS-1 | #541 |
| P34 | on-error handler never runs | LD-7 | WS-1 | #541 |
| P35 | transform is a no-op | LD-7 | WS-1 | #541 |
| P36 | capture only works for top-level steps | LD-7 | WS-1 | #541 |
| P37 | @Plugin records: missing @Required not rejected, type coercion | LD-3 | WS-6 | #546 |
| P38 | Timeout blocks forever if step ignores interruption | LD-8 | WS-2 | #542 |
| P39 | Decorator robustness (loop cap, retry all, no fail-fast, etc.) | LD-8 | WS-2 | #542 |
| P40 | Guide vs code mismatches (guard names, bare refs, undocumented) | LD-7 | WS-1, WS-4 | #541, #544 |
| P41 | Compiler has own registry with different names and syntax | LD-1 | WS-7 | #547 |
| P42 | env() and systemProperty() as sources | LD-9 | WS-3 | #543 |
| G6 | Engine uses PlaybookCompiler with no plugin registry | LD-1 | WS-7 | #547 |
| G7 | StepFileCallableDispatcher: no scope, unknown action = success | LD-1 | WS-6 | #546 |
| G21 | Engine action gates not connected to platform confirmation | LD-5 | WS-8 | #548 |
| PG8 | Fourth executor (pages scenario) + TypeScript port | LD-1 | WS-7 | #547 |
| C1 | @RequiresConfirmation is inert — no generator runs it | LD-5 | WS-8 | #548 |
| A1 | Pattern governance parsed but nothing reads it | LD-5 | WS-8 | #548 |
| A2 | Annotation processors not wired from build steps | LD-5 | WS-8 | #548 |
| W1 | Lifecycle API: actor/claimant from request, not principal | — | WS-8 | #548 |
| W2 | No check that claimant is in candidateUsers/Groups | — | WS-8 | #548 |
