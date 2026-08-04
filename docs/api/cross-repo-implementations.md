<!-- Generated — do not edit -->
# Cross-Repo SPI Implementations

SPIs with implementations across multiple repos. For each SPI:
the interface and every implementation found across the platform.

## ActionRiskClassifier

| Repo | Implementation |
|------|---------------|
| api | `ChainedActionRiskClassifier` |
| app | `DemoGateClassifier` |
| webapp-api | `IoTActionRiskClassifier` |

## ActualStateAdapter

| Repo | Implementation |
|------|---------------|
| app | `KubernetesActualStateAdapter` |
| app | `StubActualStateAdapter` |
| compliance | `ComplianceActualStateAdapter` |
| deployment | `DeploymentActualStateAdapter` |
| infra | `InfraActualStateAdapter` |
| iot | `IoTActualStateAdapter` |
| testing | `MockActualStateAdapter` |

## AgentGraphBackfill

| Repo | Implementation |
|------|---------------|
| graph | `JpaAgentGraphBackfill` |
| runtime | `NoOpAgentGraphBackfill` |

## AgentGraphQuery

| Repo | Implementation |
|------|---------------|
| graph | `JpaAgentGraphQuery` |
| runtime | `NoOpAgentGraphQuery` |

## AgentGraphStore

| Repo | Implementation |
|------|---------------|
| graph | `JpaAgentGraphStore` |
| runtime | `NoOpAgentGraphStore` |

## AgentRegistry

| Repo | Implementation |
|------|---------------|
| persistence-memory | `InMemoryAgentRegistry` |
| runtime | `JpaAgentRegistry` |

## AgentRoutingStrategy

| Repo | Implementation |
|------|---------------|
| blocks | `CbrAgentRoutingStrategy` |
| blocks | `LlmAgentRoutingStrategy` |
| runtime | `ComposableAgentRoutingStrategy` |

## AgentStateStore

| Repo | Implementation |
|------|---------------|
| persistence-memory | `InMemoryAgentStateStore` |
| runtime | `JpaAgentStateStore` |
| runtime | `NoOpAgentStateStore` |

## ApprovalEvaluator

| Repo | Implementation |
|------|---------------|
| app | `K8sApprovalEvaluator` |
| compliance | `ComplianceApprovalEvaluator` |
| deployment | `DeploymentApprovalEvaluator` |
| infra | `InfraApprovalEvaluator` |
| iot | `IoTApprovalEvaluator` |

## BehavioralSignalStore

| Repo | Implementation |
|------|---------------|
| persistence-memory | `InMemoryBehavioralSignalStore` |
| runtime | `JpaBehavioralSignalStore` |
| runtime | `NoOpBehavioralSignalStore` |

## BridgeAuditStore

| Repo | Implementation |
|------|---------------|
| bridge-persistence-jpa | `JpaBridgeAuditStore` |
| bridge-persistence-memory | `InMemoryBridgeAuditStore` |
| bridge-server | `NoOpBridgeAuditStore` |

## CandidateSetStrategy

| Repo | Implementation |
|------|---------------|
| api | `JqCandidateSetStrategy` |
| api | `StaticSetStrategy` |
| runtime | `ExpressionSetStrategy` |

## CaseChannelProvider

| Repo | Implementation |
|------|---------------|
| casehub | `ClaudonyCaseChannelProvider` |
| casehub | `OpenClawCaseChannelProvider` |
| runtime | `NoOpCaseChannelProvider` |

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

## CaseTrigger

| Repo | Implementation |
|------|---------------|
| runtime | `DefaultCaseTrigger` |
| testing | `MockCaseTrigger` |

## ChannelActivityBroadcaster

| Repo | Implementation |
|------|---------------|
| postgres-broadcaster | `PostgresChannelActivityBroadcaster` |
| runtime | `NoOpChannelActivityBroadcaster` |

## ChannelBackend

| Repo | Implementation |
|------|---------------|
| casehub | `OpenClawChannelBackend` |
| runtime | `A2AChannelBackend` |
| testing | `RecordingChannelBackend` |

## ChannelBindingStore

| Repo | Implementation |
|------|---------------|
| persistence-memory | `InMemoryChannelBindingStore` |
| runtime | `JpaChannelBindingStore` |

## ChannelMembershipStore

| Repo | Implementation |
|------|---------------|
| persistence-memory | `InMemoryChannelMembershipStore` |
| runtime | `JpaChannelMembershipStore` |

## ChannelStore

| Repo | Implementation |
|------|---------------|
| persistence-memory | `InMemoryChannelStore` |
| runtime | `JpaChannelStore` |

## ChannelSummaryStore

| Repo | Implementation |
|------|---------------|
| persistence-memory | `InMemoryChannelSummaryStore` |
| runtime | `JpaChannelSummaryStore` |

## CommitmentAttestationPolicy

| Repo | Implementation |
|------|---------------|
| ledger | `TrustGatedAttestationPolicy` |
| runtime | `StoredCommitmentAttestationPolicy` |

## CommitmentStore

| Repo | Implementation |
|------|---------------|
| persistence-memory | `InMemoryCommitmentStore` |
| runtime | `JpaCommitmentStore` |

## ConfigurationAdapter

| Repo | Implementation |
|------|---------------|
| runtime | `NoOpConfigurationAdapter` |
| testing | `MockConfigurationAdapter` |

## ConfigurationRetriever

| Repo | Implementation |
|------|---------------|
| runtime | `NoOpConfigurationRetriever` |
| testing | `MockConfigurationRetriever` |

## CorrelationKeyExtractor

| Repo | Implementation |
|------|---------------|
| api | `DefaultCorrelationKeyExtractor` |
| ras-adapter | `DesiredStateCorrelationKeyExtractor` |

## CrossTenantChannelStore

| Repo | Implementation |
|------|---------------|
| persistence-memory | `InMemoryCrossTenantChannelStore` |
| runtime | `JpaCrossTenantChannelStore` |

## CrossTenantChannelSummaryStore

| Repo | Implementation |
|------|---------------|
| persistence-memory | `InMemoryCrossTenantChannelSummaryStore` |
| runtime | `JpaCrossTenantChannelSummaryStore` |

## CrossTenantCommitmentStore

| Repo | Implementation |
|------|---------------|
| persistence-memory | `InMemoryCrossTenantCommitmentStore` |
| runtime | `JpaCrossTenantCommitmentStore` |

## CrossTenantMessageStore

| Repo | Implementation |
|------|---------------|
| persistence-memory | `InMemoryCrossTenantMessageStore` |
| runtime | `JpaCrossTenantMessageStore` |

## CrossTenantWatchdogStore

| Repo | Implementation |
|------|---------------|
| persistence-memory | `InMemoryCrossTenantWatchdogStore` |
| runtime | `JpaCrossTenantWatchdogStore` |

## DataStore

| Repo | Implementation |
|------|---------------|
| persistence-memory | `InMemoryDataStore` |
| runtime | `JpaDataStore` |

## DeliveryCursorStore

| Repo | Implementation |
|------|---------------|
| persistence-memory | `InMemoryDeliveryCursorStore` |
| runtime | `JpaDeliveryCursorStore` |

## DeviceProvider

| Repo | Implementation |
|------|---------------|
| bridge-server | `BridgeDeviceProvider` |
| homeassistant | `HomeAssistantProvider` |
| openhab | `OpenHabProvider` |
| testing | `MockDeviceProvider` |

## DeviceRegistry

| Repo | Implementation |
|------|---------------|
| api | `CdiDeviceRegistry` |
| testing | `MockDeviceRegistry` |

## DispositionSignalStore

| Repo | Implementation |
|------|---------------|
| persistence-memory | `InMemoryDispositionSignalStore` |
| runtime | `JpaDispositionSignalStore` |
| runtime | `NoOpDispositionSignalStore` |

## EventSource

| Repo | Implementation |
|------|---------------|
| app | `KubernetesEventSource` |
| app | `StubEventSource` |
| compliance | `ComplianceEventSource` |
| deployment | `DeploymentEventSource` |
| infra | `InfraEventSource` |
| iot | `IoTEventSource` |
| testing | `CannedEventSource` |

## ExclusionPolicy

| Repo | Implementation |
|------|---------------|
| examples | `ExpiringExclusionPolicy` |
| examples | `ExpiringExclusionPolicy` |
| runtime | `CommaSeparatedExclusionPolicy` |

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

## FaultCountStore

| Repo | Implementation |
|------|---------------|
| api | `InMemoryFaultCountStore` |
| persistence-jpa | `JpaFaultCountStore` |

## FaultPolicy

| Repo | Implementation |
|------|---------------|
| api | `ThresholdFaultPolicy` |
| app | `KubernetesFaultPolicy` |
| app | `StubFaultPolicy` |
| compliance | `ComplianceFaultPolicy` |
| deployment | `DeploymentFaultPolicy` |
| infra | `InfraFaultPolicy` |
| iot | `IoTFaultPolicy` |
| runtime | `CbrFaultPolicy` |

## Ganglion

| Repo | Implementation |
|------|---------------|
| api | `JavaSwitchGanglion` |
| ras-drools | `DroolsGanglion` |
| runtime | `EvidenceExtractingGanglion` |
| runtime | `ExpressionRulesGanglion` |
| runtime | `NaiveBayesGanglion` |
| testing | `MockGanglion` |

## GanglionStateStore

| Repo | Implementation |
|------|---------------|
| persistence-jpa | `JpaGanglionStateStore` |
| runtime | `InMemoryGanglionStateStore` |

## GoalCompiler

| Repo | Implementation |
|------|---------------|
| compliance | `ComplianceGoalCompiler` |
| deployment | `DeploymentGoalCompiler` |
| infra | `InfraGoalCompiler` |
| iot | `IoTGoalCompiler` |

## GoalSignalStore

| Repo | Implementation |
|------|---------------|
| persistence-memory | `InMemoryGoalSignalStore` |
| runtime | `NoOpGoalSignalStore` |

## HumanParticipatingChannelBackend

| Repo | Implementation |
|------|---------------|
| connector-backend | `ConnectorChannelBackend` |
| slack-channel | `SlackChannelBackend` |

## ImplementationRoutingStrategy

| Repo | Implementation |
|------|---------------|
| ledger | `TrustWeightedImplementationRoutingStrategy` |
| runtime | `NoOpImplementationRoutingStrategy` |

## InboundNormaliser

| Repo | Implementation |
|------|---------------|
| runtime | `DefaultInboundNormaliser` |
| slack-channel | `SlackInboundNormaliser` |

## InstanceActorIdProvider

| Repo | Implementation |
|------|---------------|
| casehub | `ClaudonyInstanceActorIdProvider` |
| runtime | `DefaultInstanceActorIdProvider` |

## InstanceStore

| Repo | Implementation |
|------|---------------|
| persistence-memory | `InMemoryInstanceStore` |
| runtime | `JpaInstanceStore` |

## LedgerEntryRepository

| Repo | Implementation |
|------|---------------|
| persistence-memory | `InMemoryLedgerEntryRepository` |
| runtime | `JpaLedgerEntryRepository` |
| runtime | `NoOpLedgerEntryRepository` |
| runtime | `QhorusLedgerEntryRepository` |
| testing | `NoOpLedgerEntryRepository` |

## LoopControl

| Repo | Implementation |
|------|---------------|
| planning | `PlanningStrategyLoopControl` |
| runtime | `ChoreographyLoopControl` |

## MessageObserver

| Repo | Implementation |
|------|---------------|
| blocks | `ChannelEventAdapter` |
| casehub | `ChannelContextWindowObserver` |
| casehub | `ScenarioObserver` |
| casehub-engine-inbound | `InboundWorkItemBridge` |
| kafka-observer | `KafkaMessageObserver` |
| notification-bridge | `NotificationBridgeObserver` |
| runtime | `InProcessMessageBus` |
| runtime | `PeerReviewAutoTrigger` |
| runtime | `PeerReviewResponseHandler` |
| webhook-observer | `WebhookMessageObserver` |
| websocket-observer | `WebSocketMessageObserver` |

## MessageStore

| Repo | Implementation |
|------|---------------|
| persistence-memory | `InMemoryMessageStore` |
| runtime | `JpaMessageStore` |

## NodeProvisioner

| Repo | Implementation |
|------|---------------|
| app | `KubernetesNodeProvisioner` |
| app | `StubNodeProvisioner` |
| compliance | `ComplianceNodeProvisioner` |
| deployment | `DeploymentNodeProvisioner` |
| infra | `InfraNodeProvisioner` |
| iot | `IoTNodeProvisioner` |
| testing | `MockNodeProvisioner` |

## OversightGateService

| Repo | Implementation |
|------|---------------|
| casehub | `OversightGateService` |
| runtime | `NoOpOversightGateService` |

## PendingApprovalHandler

| Repo | Implementation |
|------|---------------|
| runtime | `NoOpPendingApprovalHandler` |
| testing | `MockPendingApprovalHandler` |
| work-adapter | `WorkItemPendingApprovalHandler` |

## PlanStore

| Repo | Implementation |
|------|---------------|
| api | `InMemoryPlanStore` |
| app | `JpaPlanStore` |

## ProvisionerConfigRegistry

| Repo | Implementation |
|------|---------------|
| deployment | `DeploymentProvisionerConfigRegistry` |
| runtime | `NoOpProvisionerConfigRegistry` |

## RasTriggerPolicy

| Repo | Implementation |
|------|---------------|
| runtime | `DefaultRasTriggerPolicy` |
| webapp-api | `IoTSuppressionTriggerPolicy` |

## ReactionStore

| Repo | Implementation |
|------|---------------|
| persistence-memory | `InMemoryReactionStore` |
| runtime | `JpaReactionStore` |

## RenderedPromptCache

| Repo | Implementation |
|------|---------------|
| persistence-memory | `InMemoryRenderedPromptCache` |
| runtime | `NoOpRenderedPromptCache` |

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

## SituationDefinitionProvider

| Repo | Implementation |
|------|---------------|
| ras-adapter | `DesiredStateSituationDefinitionProvider` |
| runtime | `YamlSituationDefinitionProvider` |
| webapp | `JpaRuntimeSituationDefinitionProvider` |

## SituationQueryService

| Repo | Implementation |
|------|---------------|
| persistence-jpa | `JpaSituationQueryService` |
| persistence-memory | `InMemorySituationQueryService` |

## SituationRecompiler

| Repo | Implementation |
|------|---------------|
| app | `StubSituationRecompiler` |
| runtime | `CbrSituationRecompiler` |

## SituationSource

| Repo | Implementation |
|------|---------------|
| app | `StubSituationSource` |
| runtime | `DefaultSituationSource` |

## SituationStore

| Repo | Implementation |
|------|---------------|
| persistence-jpa | `JpaSituationStore` |
| persistence-memory | `InMemorySituationStore` |

## SkillMatcher

| Repo | Implementation |
|------|---------------|
| ai | `EmbeddingSkillMatcher` |
| examples | `KeywordSkillMatcher` |

## SpaceStore

| Repo | Implementation |
|------|---------------|
| persistence-memory | `InMemorySpaceStore` |
| runtime | `JpaSpaceStore` |

## SummaryUpdateHook

| Repo | Implementation |
|------|---------------|
| blocks | `ChannelSummariser` |
| runtime | `NoOpSummaryUpdateHook` |

## TemplateRegistry

| Repo | Implementation |
|------|---------------|
| persistence-memory | `InMemoryTemplateRegistry` |
| runtime | `CdiTemplateRegistry` |

## TopicStore

| Repo | Implementation |
|------|---------------|
| persistence-memory | `InMemoryTopicStore` |
| runtime | `JpaTopicStore` |

## TransitionExecutor

| Repo | Implementation |
|------|---------------|
| engine-adapter | `CaseTransitionExecutor` |
| runtime | `SimpleTransitionExecutor` |
| testing | `MockTransitionExecutor` |

## WatchdogStore

| Repo | Implementation |
|------|---------------|
| persistence-memory | `InMemoryWatchdogStore` |
| runtime | `JpaWatchdogStore` |

## WorkerContextProvider

| Repo | Implementation |
|------|---------------|
| casehub | `ClaudonyWorkerContextProvider` |
| runtime | `EmptyWorkerContextProvider` |

## WorkerExecutionGuard

| Repo | Implementation |
|------|---------------|
| resilience | `PoisonPillWorkerExecutionGuard` |
| runtime | `AllowAllWorkerExecutionGuard` |

## WorkerProvisioner

| Repo | Implementation |
|------|---------------|
| casehub | `ClaudonyWorkerProvisioner` |
| casehub | `OpenClawWorkerProvisioner` |
| runtime | `NoOpWorkerProvisioner` |

## WorkerRuntime

| Repo | Implementation |
|------|---------------|
| runtime | `DefaultWorkerRuntime` |
| workers-camel | `CamelWorkerRuntime` |
| workers-github-actions | `GitHubActionsWorkerRuntime` |
| workers-http | `HttpWorkerRuntime` |
| workers-k8s | `K8sWorkerRuntime` |
| workers-mcp | `McpWorkerRuntime` |
| workers-script | `ScriptWorkerRuntime` |

## WorkerSelectionStrategy

| Repo | Implementation |
|------|---------------|
| ai | `SemanticWorkerSelectionStrategy` |
| core | `ClaimFirstStrategy` |
| core | `LeastLoadedStrategy` |
| core | `RoundRobinStrategy` |

## WorkerStatusListener

| Repo | Implementation |
|------|---------------|
| casehub | `ClaudonyWorkerStatusListener` |
| casehub | `OpenClawWorkerStatusListener` |
| runtime | `NoOpWorkerStatusListener` |

