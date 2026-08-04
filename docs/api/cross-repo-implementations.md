<!-- Generated — do not edit -->
# Cross-Repo SPI Implementations

SPIs with implementations across multiple repos. For each SPI:
the interface and every implementation found across the platform.

## AgentRoutingStrategy

| Repo | Implementation |
|------|---------------|
| blocks | `CbrAgentRoutingStrategy` |
| blocks | `LlmAgentRoutingStrategy` |
| runtime | `ComposableAgentRoutingStrategy` |

## CandidateSetStrategy

| Repo | Implementation |
|------|---------------|
| api | `JqCandidateSetStrategy` |
| api | `StaticSetStrategy` |
| runtime | `ExpressionSetStrategy` |

## CaseEventRecorder

| Repo | Implementation |
|------|---------------|
| api | `NoOpCaseEventRecorder` |
| runtime | `DefaultCaseEventRecorder` |

## CaseOutcomeObserver

| Repo | Implementation |
|------|---------------|
| api | `ScreeningOrchestrator` |
| runtime | `CbrCaseRetainObserver` |
| runtime | `NoOpCaseOutcomeObserver` |

## ExpressionEngine

| Repo | Implementation |
|------|---------------|
| expression | `JQExpressionEngine` |
| expression | `JexlExpressionEngine` |
| expression | `MvelExpressionEngine` |
| runtime | `JQExpressionEngine` |
| runtime | `LambdaExpressionEngine` |

## ExpressionEngineRegistry

| Repo | Implementation |
|------|---------------|
| expression | `DefaultExpressionEngineRegistry` |
| platform | `NoOpExpressionEngineRegistry` |
| runtime | `DefaultExpressionEngineRegistry` |

## ImplementationRoutingStrategy

| Repo | Implementation |
|------|---------------|
| ledger | `TrustWeightedImplementationRoutingStrategy` |
| runtime | `NoOpImplementationRoutingStrategy` |

## LoopControl

| Repo | Implementation |
|------|---------------|
| planning | `PlanningStrategyLoopControl` |
| runtime | `ChoreographyLoopControl` |

## RoutingSignalProvider

| Repo | Implementation |
|------|---------------|
| blocks | `CoordinationSignalProvider` |
| blocks | `DispositionAwareRouting` |
| blocks | `PlanCompositionAnalyser` |
| blocks | `PredecessorAnalyser` |
| engine-ai | `SemanticSignalProvider` |
| ledger | `TrustSignalProvider` |
| runtime | `ExperienceSignalProvider` |
| runtime | `GoalSignalProvider` |
| runtime | `PersonalitySignalProvider` |
| runtime | `WorkloadSignalProvider` |

## WorkerExecutionGuard

| Repo | Implementation |
|------|---------------|
| resilience | `PoisonPillWorkerExecutionGuard` |
| runtime | `AllowAllWorkerExecutionGuard` |

