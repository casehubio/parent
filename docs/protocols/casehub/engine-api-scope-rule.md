---
id: PP-20260529-ce2de0
title: "Depend on casehub-engine-api (not casehub-engine) in modules that implement engine SPIs without running the engine"
type: rule
scope: platform
applies_to: "Any module implementing WorkerProvisioner, CaseChannelProvider, WorkerStatusListener, or WorkerContextProvider SPIs without embedding the full engine runtime"
severity: critical
refs:
  - ../repos/casehub-engine.md
  - ../../PLATFORM.md
violation_hint: "31+ CDI deployment problems at startup: Unsatisfied dependency for WorkerExecutionManager, CaseInstanceRepository, EventLogRepository, JobScheduler — none of the errors name the incorrect artifact"
created: 2026-05-29
---

Modules that implement casehub-engine SPIs (WorkerProvisioner, CaseChannelProvider, WorkerStatusListener, WorkerContextProvider) but do not run the full engine must declare `casehub-engine-api` — not `casehub-engine` — as their compile dependency. `casehub-engine` is the full Quarkus runtime module and ships `@ApplicationScoped` CDI beans that require persistence SPIs (`CaseInstanceRepository`, `EventLogRepository`, `JobScheduler`, `WorkerExecutionManager`) to be satisfied at augmentation time. `casehub-engine-api` is the pure-Java SPI interface module with no CDI beans and no Quarkus runtime dependency. The app module that wires everything together is the correct place for `casehub-engine` (compile or runtime scope). See also: GE-20260529-b5723e (garden entry for the symptom and diagnosis).
