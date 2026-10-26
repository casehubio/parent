<!-- Generated — do not edit -->
# Cross-Repo SPI Implementations

SPIs with implementations across multiple repos. For each SPI:
the interface and every implementation found across the platform.

## ActionRiskClassifier

| Repo | Implementation |
|------|---------------|
| api | `ChainedActionRiskClassifier` |
| runtime | `CallbackActionRiskClassifier` |
| webapp-api | `IoTActionRiskClassifier` |

## ActorIdentityProvider

| Repo | Implementation |
|------|---------------|
| ledger-core | `PassThroughActorIdentityProvider` |
| runtime | `InternalActorIdentityProvider` |

## AgentChannelBackend

| Repo | Implementation |
|------|---------------|
| notification-bridge-core | `NotificationChannelBackendCore` |
| runtime-core | `QhorusChannelBackend` |

## AgentGraphBackfill

| Repo | Implementation |
|------|---------------|
| eidos-core | `NoOpAgentGraphBackfill` |
| graph | `JpaAgentGraphBackfill` |

## AgentGraphQuery

| Repo | Implementation |
|------|---------------|
| eidos-core | `NoOpAgentGraphQuery` |
| graph | `JpaAgentGraphQuery` |

## AgentGraphStore

| Repo | Implementation |
|------|---------------|
| eidos-core | `NoOpAgentGraphStore` |
| graph | `JpaAgentGraphStore` |

## AgentRegistry

| Repo | Implementation |
|------|---------------|
| persistence-memory | `InMemoryAgentRegistry` |
| runtime | `JpaAgentRegistry` |
| runtime-core | `NoOpAgentRegistry` |

## AgentRoutingStrategy

| Repo | Implementation |
|------|---------------|
| agency-core | `CbrAgentRoutingStrategy` |
| agency-core | `LlmAgentRoutingStrategy` |
| api | `ComposableAgentRoutingStrategy` |

## AgentSelector

| Repo | Implementation |
|------|---------------|
| eidos-routing | `EngineAwareAgentSelector` |
| runtime | `SimpleAgentSelector` |

## AgentStateStore

| Repo | Implementation |
|------|---------------|
| eidos-core | `NoOpAgentStateStore` |
| persistence-memory | `InMemoryAgentStateStore` |
| runtime | `JpaAgentStateStore` |

## AgentTrustProvider

| Repo | Implementation |
|------|---------------|
| memory | `NoOpAgentTrustProvider` |
| runtime | `TrustScoreAgentTrustProvider` |

## BehavioralSignalStore

| Repo | Implementation |
|------|---------------|
| eidos-core | `NoOpBehavioralSignalStore` |
| persistence-memory | `InMemoryBehavioralSignalStore` |
| runtime | `JpaBehavioralSignalStore` |

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
| runtime-core | `ExpressionSetStrategy` |

## CapabilityHealth

| Repo | Implementation |
|------|---------------|
| engine-support-core | `A2ACapabilityHealth` |
| engine-support-core | `McpCapabilityHealth` |
| runtime | `DefaultCapabilityHealth` |
| runtime-core | `NoOpCapabilityHealth` |

## CaseEventRecorder

| Repo | Implementation |
|------|---------------|
| api | `NoOpCaseEventRecorder` |
| runtime-core | `DefaultCaseEventRecorder` |

## CaseMemoryStore

| Repo | Implementation |
|------|---------------|
| memory-api | `DelegatingCaseMemoryStore` |
| memory-core | `CaseEnrichmentPipeline` |
| memory-inmem | `InMemoryMemoryStore` |
| memory-jpa | `JpaMemoryStore` |
| memory-mem0 | `Mem0CaseMemoryStore` |
| memory-spring-jpa | `SpringMemoryStore` |
| memory-sqlite | `SqliteMemoryStore` |

## CaseOutcomeObserver

| Repo | Implementation |
|------|---------------|
| api | `ScreeningOrchestrator` |
| runtime | `CbrCaseRetainObserver` |
| runtime-core | `NoOpCaseOutcomeObserver` |

## CaseRetriever

| Repo | Implementation |
|------|---------------|
| rag-core | `HybridCaseRetriever` |
| rag-core | `PayloadBoostCaseRetriever` |
| rag-crossencoder | `CorrectiveCaseRetriever` |
| rag-crossencoder | `RerankingCaseRetriever` |
| rag-expansion | `QueryExpandingCaseRetriever` |
| rag-testing | `InMemoryCaseRetriever` |
| rag-tracking | `TrackingCaseRetriever` |

## CbrRetrievalTracker

| Repo | Implementation |
|------|---------------|
| memory-cbr-tracking | `SqliteCbrRetrievalTracker` |
| memory-testing | `InMemoryCbrRetrievalTracker` |

## ChannelActivityBroadcaster

| Repo | Implementation |
|------|---------------|
| postgres-broadcaster | `PostgresChannelActivityBroadcaster` |
| postgres-broadcaster-spring | `SpringPostgresChannelActivityBroadcaster` |
| runtime-core | `NoOpChannelActivityBroadcaster` |

## ChannelBackend

| Repo | Implementation |
|------|---------------|
| a2a-outbound | `A2AOutboundBackend` |
| a2a-push-notification-core | `PushNotificationBackendCore` |
| agent-bridge | `AgentProviderBackend` |
| runtime | `A2AChannelBackend` |
| testing | `RecordingChannelBackend` |

## ChannelBindingStore

| Repo | Implementation |
|------|---------------|
| persistence-memory | `InMemoryChannelBindingStore` |
| runtime | `JpaChannelBindingStore` |

## ChannelManager

| Repo | Implementation |
|------|---------------|
| cluster | `ChannelManagerDecorator` |
| runtime-core | `ChannelService` |

## ChannelMembershipStore

| Repo | Implementation |
|------|---------------|
| persistence-memory | `InMemoryChannelMembershipStore` |
| runtime | `JpaChannelMembershipStore` |

## ChannelProtocol

| Repo | Implementation |
|------|---------------|
| agency-core | `ConversationProtocol` |
| agency-core | `JudgmentProtocol` |
| agency-core | `NegotiationProtocol` |
| runtime-core | `ContributionRequiredProtocol` |
| runtime-core | `RequestResponseProtocol` |
| runtime-core | `RoundRobinProtocol` |
| runtime-core | `TaskCompletionProtocol` |

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
| ledger-core | `TrustGatedAttestationPolicy` |
| runtime-core | `StoredCommitmentAttestationPolicy` |

## CommitmentStore

| Repo | Implementation |
|------|---------------|
| persistence-memory | `InMemoryCommitmentStore` |
| runtime | `JpaCommitmentStore` |

## ConsumerMessaging

| Repo | Implementation |
|------|---------------|
| cluster | `RoutingConsumerMessaging` |
| runtime-core | `MessageService` |

## ContentSummariser

| Repo | Implementation |
|------|---------------|
| agency-core | `HeuristicMessageSummariser` |
| agency-core | `LlmContentSummariser` |
| agency-core | `TieredContentSummariser` |
| summarisation | `VerbatimContentSummariser` |
| summarisation-api | `VerbatimContentSummariser` |

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

## CursorStore

| Repo | Implementation |
|------|---------------|
| rag-core | `FileCursorStore` |
| rag-testing | `InMemoryCursorStore` |

## DataStore

| Repo | Implementation |
|------|---------------|
| persistence-memory | `InMemoryDataStore` |
| runtime | `JpaDataStore` |

## DecompositionStrategy

| Repo | Implementation |
|------|---------------|
| agency-core | `CapabilityDependencyDecomposition` |
| agency-core | `ForwardReasoningDecomposition` |
| agency-core | `HeuristicDecomposition` |
| agency-core | `HybridDecomposition` |
| agency-core | `IdentityDecomposition` |
| agency-core | `LlmDecomposition` |
| agency-core | `SequenceStrategy` |
| agency-core | `StaticDecomposition` |
| planning-core | `GoapDecompositionStrategy` |
| planning-core | `LlmDecompositionStrategy` |
| planning-core | `PortfolioDecompositionStrategy` |

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

## DispositionEvolution

| Repo | Implementation |
|------|---------------|
| eidos-core | `NoOpDispositionEvolution` |
| runtime | `DefaultDispositionEvolution` |

## DispositionHealth

| Repo | Implementation |
|------|---------------|
| eidos-core | `NoOpDispositionHealth` |
| runtime | `DefaultDispositionHealth` |

## DispositionSignalStore

| Repo | Implementation |
|------|---------------|
| eidos-core | `NoOpDispositionSignalStore` |
| persistence-memory | `InMemoryDispositionSignalStore` |
| runtime | `JpaDispositionSignalStore` |

## EmbeddingIngestor

| Repo | Implementation |
|------|---------------|
| rag-core | `DedupEmbeddingIngestor` |
| rag-core | `QdrantEmbeddingIngestor` |
| rag-testing | `InMemoryEmbeddingIngestor` |

## EventDispatcher

| Repo | Implementation |
|------|---------------|
| runtime | `VertxEventDispatcher` |
| runtime-spring | `SpringEventDispatcher` |

## EventSource

| Repo | Implementation |
|------|---------------|
| agency-core | `SwarmEventSource` |
| desiredstate | `IoTEventSource` |

## ExclusionPolicy

| Repo | Implementation |
|------|---------------|
| examples | `ExpiringExclusionPolicy` |
| examples | `ExpiringExclusionPolicy` |
| runtime-core | `CommaSeparatedExclusionPolicy` |

## ExecutionBackend

| Repo | Implementation |
|------|---------------|
| agency-core | `CancellableBackend` |
| engine-adapter-core | `EngineHostedBackend` |

## ExecutionEventListener

| Repo | Implementation |
|------|---------------|
| agency-core | `ChannelTeardownListener` |
| agency-core | `EventLogListener` |
| agency-core | `LedgerExecutionListener` |
| agency-core | `MetricsListener` |
| agency-core | `ResultCollector` |
| engine-adapter-core | `CheckpointingListener` |

## ExpressionEngine

| Repo | Implementation |
|------|---------------|
| expression-core | `JQExpressionEngine` |
| expression-core | `JexlExpressionEngine` |
| expression-core | `MvelExpressionEngine` |
| runtime | `MvelExpressionEngine` |
| runtime-core | `JQExpressionEngine` |
| runtime-core | `LambdaExpressionEngine` |

## ExpressionEngineRegistry

| Repo | Implementation |
|------|---------------|
| expression-core | `DefaultExpressionEngineRegistry` |
| platform-core | `NoOpExpressionEngineRegistry` |
| runtime | `DefaultExpressionEngineRegistry` |

## GoalEvolution

| Repo | Implementation |
|------|---------------|
| api | `DefaultGoalEvolution` |
| eidos-core | `NoOpGoalEvolution` |
| runtime | `DefaultGoalEvolution` |

## GoalSignalStore

| Repo | Implementation |
|------|---------------|
| api | `InMemoryGoalSignalStore` |
| eidos-core | `NoOpGoalSignalStore` |
| persistence-memory | `InMemoryGoalSignalStore` |

## GraphCaseMemoryStore

| Repo | Implementation |
|------|---------------|
| memory | `NoOpCaseMemoryStore` |
| memory-graphiti | `GraphitiCaseMemoryStore` |

## HolidayCalendar

| Repo | Implementation |
|------|---------------|
| runtime | `CompanyHolidayCalendar` |
| runtime-core | `ConfigHolidayCalendar` |
| runtime-core | `ICalHolidayCalendar` |

## HumanParticipatingChannelBackend

| Repo | Implementation |
|------|---------------|
| connector-backend-core | `ConnectorChannelBackendCore` |
| slack-channel | `SlackChannelBackend` |
| slack-channel-core | `SlackChannelBackendCore` |

## ImplementationRoutingStrategy

| Repo | Implementation |
|------|---------------|
| ledger-core | `TrustWeightedImplementationRoutingStrategy` |
| runtime-core | `NoOpImplementationRoutingStrategy` |

## InboundNormaliser

| Repo | Implementation |
|------|---------------|
| runtime-core | `DefaultInboundNormaliser` |
| slack-channel-core | `SlackInboundNormaliser` |

## InferenceModel

| Repo | Implementation |
|------|---------------|
| inference-inmem | `InMemoryInferenceModel` |
| inference-runtime | `OnnxInferenceModel` |

## InstanceStore

| Repo | Implementation |
|------|---------------|
| persistence-memory | `InMemoryInstanceStore` |
| runtime | `JpaInstanceStore` |

## JudgmentVerifier

| Repo | Implementation |
|------|---------------|
| agency-core | `CompositeVerifier` |
| agency-core | `NoOpVerifier` |
| engine-adapter-core | `LlmEvaluationVerifier` |
| engine-adapter-core | `SchemaValidationVerifier` |
| runtime-core | `AcceptAllVerifier` |
| runtime-core | `EvidencePresenceVerifier` |

## LedgerEntryRepository

| Repo | Implementation |
|------|---------------|
| ledger-core | `NoOpLedgerEntryRepository` |
| ledger-spring-jpa | `SpringJpaLedgerEntryRepository` |
| persistence-memory | `InMemoryLedgerEntryRepository` |
| runtime | `JpaLedgerEntryRepository` |
| runtime | `QhorusLedgerEntryRepository` |
| testing | `NoOpLedgerEntryRepository` |

## LoopControl

| Repo | Implementation |
|------|---------------|
| planning-core | `PlanningStrategyLoopControl` |
| runtime-core | `ChoreographyLoopControl` |

## MessageObserver

| Repo | Implementation |
|------|---------------|
| agency-core | `ChannelEventAdapter` |
| agency-core | `ChannelObserver` |
| cache | `CachePopulationObserver` |
| compliance-report | `JudgmentVerificationObserver` |
| engine-support-core | `InboundWorkItemBridge` |
| kafka-observer | `KafkaMessageObserver` |
| kafka-observer-spring | `SpringKafkaMessageObserver` |
| notification-bridge-core | `NotificationBridgeObserverCore` |
| runtime | `PeerReviewAutoTrigger` |
| runtime | `PeerReviewResponseHandler` |
| runtime-core | `InProcessMessageBus` |
| webhook-observer | `WebhookMessageObserver` |
| websocket-observer | `WebSocketMessageObserver` |
| websocket-observer-spring | `SpringWebSocketMessageObserver` |

## MessageStore

| Repo | Implementation |
|------|---------------|
| cache | `CachingMessageStore` |
| persistence-memory | `InMemoryMessageStore` |
| runtime | `JpaMessageStore` |

## MetadataExtractor

| Repo | Implementation |
|------|---------------|
| rag-core | `YamlFrontmatterExtractor` |
| rag-query-augmentation | `QueryAugmentingMetadataExtractor` |

## MultiModalEmbedder

| Repo | Implementation |
|------|---------------|
| inference-api | `MatryoshkaMultiModalEmbedder` |
| inference-bge-m3 | `BgeM3Embedder` |
| rag-cache | `CachingMultiModalEmbedder` |
| rag-core | `SeparateModelEmbedder` |

## QueryExpander

| Repo | Implementation |
|------|---------------|
| rag-expansion | `LlmQueryExpander` |
| rag-expansion | `NoOpQueryExpander` |
| rag-expansion | `StepBackQueryExpander` |
| rag-expansion | `TemplateQueryExpander` |
| rag-testing | `InMemoryQueryExpander` |

## ReactionStore

| Repo | Implementation |
|------|---------------|
| persistence-memory | `InMemoryReactionStore` |
| runtime | `JpaReactionStore` |

## ReflectionSynthesizer

| Repo | Implementation |
|------|---------------|
| agency | `LlmReflectionSynthesizer` |
| cognition | `LlmReflectionSynthesizer` |
| memory | `NoOpReflectionSynthesizer` |

## RelevanceEvaluator

| Repo | Implementation |
|------|---------------|
| rag-api | `ColBertRelevanceEvaluator` |
| rag-crossencoder | `CrossEncoderRelevanceEvaluator` |
| rag-testing | `InMemoryRelevanceEvaluator` |

## RenderedPromptCache

| Repo | Implementation |
|------|---------------|
| eidos-core | `NoOpRenderedPromptCache` |
| persistence-memory | `InMemoryRenderedPromptCache` |

## RetrievalTracker

| Repo | Implementation |
|------|---------------|
| rag-testing | `InMemoryRetrievalTracker` |
| rag-tracking | `SqliteRetrievalTracker` |

## RoutingSignalProvider

| Repo | Implementation |
|------|---------------|
| agency-core | `CoordinationSignalProvider` |
| agency-core | `DispositionAwareRouting` |
| agency-core | `ModelPreferenceSignalProvider` |
| agency-core | `PlanCompositionAnalyser` |
| agency-core | `PredecessorAnalyser` |
| engine-support-core | `SemanticSignalProvider` |
| ledger-core | `TrustSignalProvider` |
| runtime-core | `ExperienceSignalProvider` |
| runtime-core | `GoalSignalProvider` |
| runtime-core | `PersonalitySignalProvider` |
| runtime-core | `WorkloadSignalProvider` |

## SkillMatcher

| Repo | Implementation |
|------|---------------|
| examples | `KeywordSkillMatcher` |
| work-support-core | `EmbeddingSkillMatcher` |

## SkillProfileProvider

| Repo | Implementation |
|------|---------------|
| ai | `WorkerProfileSkillProfileProvider` |
| work-support-core | `CapabilitiesSkillProfileProvider` |
| work-support-core | `CompositeSkillProfileProvider` |
| work-support-core | `ResolutionHistorySkillProfileProvider` |

## SlaBreachPolicy

| Repo | Implementation |
|------|---------------|
| runtime | `CallbackSlaBreachPolicyDecorator` |
| runtime | `DeclarativeSlaBreachPolicy` |
| runtime | `PreferenceSlaBreachPolicyDecorator` |
| runtime-core | `NoOpSlaBreachPolicy` |

## SpaceStore

| Repo | Implementation |
|------|---------------|
| persistence-memory | `InMemorySpaceStore` |
| runtime | `JpaSpaceStore` |

## StepOutcomeObserver

| Repo | Implementation |
|------|---------------|
| runtime | `RetrievalFeedbackObserver` |
| runtime-core | `NoOpStepOutcomeObserver` |

## SummaryUpdateHook

| Repo | Implementation |
|------|---------------|
| agency-core | `ChannelSummariser` |
| runtime-core | `NoOpSummaryUpdateHook` |

## SystemPromptRenderer

| Repo | Implementation |
|------|---------------|
| cognition | `CognitiveSystemPromptRenderer` |
| runtime | `EidosSystemPromptRenderer` |

## TemplateRegistry

| Repo | Implementation |
|------|---------------|
| persistence-memory | `InMemoryTemplateRegistry` |
| runtime | `CdiTemplateRegistry` |

## ThreadSummaryStore

| Repo | Implementation |
|------|---------------|
| agency-core | `NoOpThreadSummaryStore` |
| persistence-memory | `InMemoryThreadSummaryStore` |
| runtime | `JpaThreadSummaryStore` |

## TopicStore

| Repo | Implementation |
|------|---------------|
| persistence-memory | `InMemoryTopicStore` |
| runtime | `JpaTopicStore` |

## TrustScoreSource

| Repo | Implementation |
|------|---------------|
| agent-card-signing | `IdentityVerificationTrustDecorator` |
| agent-card-signing-core | `IdentityVerificationTrustDecoratorCore` |
| ledger-core | `ComputedTrustSourceCore` |
| ledger-core | `MaterializedTrustSourceCore` |
| runtime | `CachedTrustScoreSource` |
| runtime | `ComputedTrustScoreSource` |
| runtime | `MaterializedTrustScoreSource` |

## VocabularyRegistry

| Repo | Implementation |
|------|---------------|
| runtime | `CdiVocabularyRegistry` |
| runtime-core | `NoOpVocabularyRegistry` |

## WatchdogStore

| Repo | Implementation |
|------|---------------|
| persistence-memory | `InMemoryWatchdogStore` |
| runtime | `JpaWatchdogStore` |

## WorkItemObserver

| Repo | Implementation |
|------|---------------|
| qhorus | `QhorusCompensationAdapter` |
| qhorus | `QhorusWorkItemLifecycleAdapter` |
| webapp | `WorkItemOutcomeRecorder` |

## WorkerExecutionGuard

| Repo | Implementation |
|------|---------------|
| resilience-core | `PoisonPillWorkerExecutionGuard` |
| runtime-core | `AllowAllWorkerExecutionGuard` |

## WorkerFunctionProvider

| Repo | Implementation |
|------|---------------|
| engine-adapter-core | `PatternWorkerFunctionProvider` |
| engine-support-core | `A2AWorkerFunctionProvider` |
| engine-support-core | `FlowWorkerFunctionProvider` |
| engine-support-core | `McpWorkerFunctionProvider` |
| engine-support-core | `ReActWorkerFunctionProvider` |

## WorkerProvisioner

| Repo | Implementation |
|------|---------------|
| runtime | `CallbackWorkerProvisionerDecorator` |
| runtime-core | `NoOpWorkerProvisioner` |
| testing | `TestWorkerProvisioner` |

## WorkerSelectionStrategy

| Repo | Implementation |
|------|---------------|
| core | `ClaimFirstStrategy` |
| core | `LeastLoadedStrategy` |
| core | `RoundRobinStrategy` |
| runtime | `CallbackWorkerSelectionStrategyDecorator` |
| work-support-core | `SemanticWorkerSelectionStrategy` |

