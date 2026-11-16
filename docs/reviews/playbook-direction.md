# Playbook direction: language, levels and tests

Status: proposal, 2026-11-16. Follows the cross-repo review in `code-review-notes.md` (finding IDs such as P32 refer to that file). Scope: platform, connectors, engine, agency, ops.

## Goal

Onboarding happens through playbooks. The examples are organised in levels (one new concept each) and layers (one repo each). Every example teaches, documents and tests at the same time.

The levels have a third job: they measure whether the language is good. If a model cannot write a passing playbook for a level, the language or its feedback is the problem.

## Language direction

1. **One semantics.** Four executors exist (platform interpreter, engine compiler path, pages scenario executor, TypeScript port). The levels are the conformance suite: each level runs on every executor that claims it, with zero expected failures. (P21, P32, P41, G6, G7, PG8)
2. **Design for the LLM author.** The validator is the user interface. Expose `validate-playbook` as an MCP tool returning structured, located errors with suggestions. Serve the step catalogue per level so a model sees a small vocabulary, not 600 operations.
3. **Types from the APIs.** Generated steps already have Java input and output types. Type each `capture` from them and check `${...}` references before run. (P37)
4. **Values are data, not text.** Bind variables into compiled conditions instead of substituting them into the condition string. Model output and webhook fields flow through playbooks. (P33)
5. **Governance in the language.** Steps carry an effect class (read, write, irreversible, spends money) derived from annotations. `confirm:` and `approve:` are decorators that compile to the one engine gate. A playbook can then be summarised statically: what it may do and who must agree. (A1, C1, G21, P28)
6. **Shaped for CBR.** A retained case stores the playbook, its bindings and the outcome. That needs stable step identity, versioned and namespaced step names. (P29)
7. **Finish what is declared.** `on-error` handlers, `transform`, nested `capture` and `invoke:` either work or are removed. (P34, P35, P36, P40)

## Levels and layers

Two axes. One business scenario runs through all five layers so the learner watches the same story grow.

| Layer | The level adds | Needed first |
|---|---|---|
| Platform | Steps, captures, flow control, coordination, agent sessions | One runner in main code; item 7 above |
| Connectors | A real-world action with confirmation | Confirmation that fires |
| Engine | The playbook as a durable worker in a case, with a human task | Plugin steps accepted on the engine path |
| Agency | A debate or vote as a step, with oversight | Patterns exposed as steps; governance compiled |
| Ops | Deployment through desired state with approval | Step generation on for ops; approval on every path |

Each example has:

- **A header**: `level`, `layer`, `teaches`, `builds-on`, and `rules` (see below). The tutorial index is generated from headers.
- **A paired test** that asserts the rules.
- **A negative twin** wherever a rule forbids something.
- **One file shape and one key style.**

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

## Order of work

1. Canonical runner in main code; finish or remove the declared-but-inert features.
2. Rules headers, the lint and the mutation check on the existing platform levels.
3. Typed captures and the validation MCP tool; then the authoring metric.
4. Engine path accepts plugin steps; add engine, agency and ops levels.
5. Governance decorators and negative twins at every level that has a gate.
