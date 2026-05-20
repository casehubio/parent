---
id: PP-20260520-981c85
title: "Internal inputData is Map<String,Object>; public entry points accept Object"
type: rule
scope: repo
applies_to: "casehub-engine — WorkflowExecutor, WorkerExecutionManager, all internal handlers"
severity: guidance
refs:
  - repos/casehub-engine.md
violation_hint: >
    Adding Map<String,Object> to a public-facing CaseHub or CaseHubRuntime startCase
    overload, or questioning why internal handler parameters use Map instead of a
    typed domain object.
created: 2026-05-20
---

Internal `inputData` parameters in handlers, executors, and schedulers are
`Map<String, Object>` because they hold post-evaluation data — the result of
applying `inputMapping` expressions against `CaseContext`. This is correct at
the engine-internal layer: by the time `inputData` reaches `WorkflowExecutor`,
`WorkerExecutionManager`, or any scheduler, it has already been deserialized and
evaluated. Public entry points (`CaseHub.startCase`, `CaseHubRuntime.startCase`)
should accept `Object` to align with `Flow.instance(Object)`, allowing callers to
pass Maps, POJOs, or any JSON-serializable type — migration tracked in
casehubio/engine#302.
