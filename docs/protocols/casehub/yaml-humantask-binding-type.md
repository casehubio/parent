---
id: PP-20260520-b2a932
title: "Use humanTask binding type for WorkItem-backed human gates — not capability"
type: rule
scope: platform
applies_to: "all CaseHub harnesses (devtown, aml, clinical) writing YAML case definitions with human approval or review gates"
severity: important
refs:
  - casehub-engine schema: schema/src/main/resources/schema/CaseDefinition.yaml
  - casehub-engine api: api/src/main/java/io/casehub/api/model/HumanTaskTarget.java
  - casehub-engine api: api/src/main/java/io/casehub/api/model/converter/CaseDefinitionYamlMapper.java
violation_hint: "capability: \"human-decision:*\" binding fires no HumanTaskScheduleEvent — the WorkItem is silently never created and the case stalls in WAITING state with no error"
created: 2026-05-20
---

When a YAML case definition binding must create a casehub-work WorkItem for a human
to complete, use the `humanTask:` binding target (not `capability:`). The `capability`
path routes to WorkerProvisioner — it has no path to casehub-work WorkItem creation.
The `humanTask` path fires `HumanTaskScheduleEvent`, which `HumanTaskScheduleHandler`
(in `casehub-engine-work-adapter`) consumes to create the WorkItem. Inline mode
requires `title:`; template mode requires `templateRef:`. Both support `outputMapping:`
to write WorkItem resolution data back to the case context on completion.
