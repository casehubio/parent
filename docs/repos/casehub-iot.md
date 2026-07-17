# casehub-iot

**GitHub:** [casehubio/iot](https://github.com/casehubio/iot)  
**Platform doc:** [PLATFORM.md](https://raw.githubusercontent.com/casehubio/parent/main/docs/PLATFORM.md)

---

## Purpose

Typed IoT device abstraction layer for the CaseHub ecosystem. Provides a Matter-aligned device class hierarchy, reactive SPIs for device discovery and command dispatch, and CDI-based state change events. Provider modules implement the SPIs for specific platforms (Home Assistant, OpenHAB). Application repos consume the `api` module and receive a unified device model regardless of the underlying home automation platform.

**`api` is a public API surface — semver discipline applies from first release.** Community automations in casehub-life and downstream depend on it.

---

## Key Abstractions

### DeviceProvider SPI

The `DeviceProvider` CDI SPI is the provider contract. Four methods: `providerId()`, `discover() → Uni<List<DeviceEntity>>`, `dispatch(DeviceCommand) → Uni<CommandResult>`, and `status() → ProviderStatus`. Provider implementations are CDI `@ApplicationScoped` beans — auto-discovered. Discovery returns the full device inventory; dispatch sends a command to a specific device; status reports connection health.

### DeviceRegistry SPI

The `DeviceRegistry` CDI SPI is the consumer contract. Methods: `findById(String)`, `findByClass(Class<T>)`, `findByTenancyId(String)`, `findAll()`, `refresh() → Uni<Void>`. `CdiDeviceRegistry` is the `@ApplicationScoped` default — aggregates all `DeviceProvider` beans and delegates.

### Device Class Hierarchy

`DeviceEntity` is the abstract root. All device types extend it with domain-specific fields and a typed `Builder`. Device classes are aligned with the Matter Device Type Library.

| Type | Class | Key Fields |
|------|-------|------------|
| `SwitchDevice` | `SWITCH` | `on` |
| `LightDevice` | `LIGHT` | `on`, `brightness` |
| `ThermostatDevice` | `THERMOSTAT` | `currentTemperature`, `targetTemperature`, `mode` |
| `SensorDevice` | `SENSOR` | `sensorType`, `numericValue`, `unit` |
| `PresenceSensor` | `PRESENCE_SENSOR` | `present`, `lastSeen` |
| `PowerSensor` | `POWER_SENSOR` | `power`, `energy`, `voltage`, `current` |
| `LockDevice` | `LOCK` | `locked` |
| `CoverDevice` | `COVER` | `position`, `moving` |
| `MediaPlayerDevice` | `MEDIA_PLAYER` | `volume` |
| `FanDevice` | `FAN` | `on` |
| `CameraDevice` | `CAMERA` | `streaming` |

Every `DeviceEntity` carries `deviceId`, `deviceClass`, `label`, `available`, `lastUpdated`, and `tenancyId`. The `capabilities()` method returns a `Map<String, Object>` used by `StateChangeEvent.deriveChangedCapabilities()` to compute change sets.

### Vendor Supplement Types

Provider modules extend common types only for fields that have no cross-vendor equivalent. Common interface first, supplement last resort.

**Home Assistant:** `HomeAssistantThermostat` (preset mode, swing mode, HVAC action), `HomeAssistantLight` (color mode, effect), `HomeAssistantLock` (lock state enum from HA).

**OpenHAB:** `OpenHabThermostat` (heating/cooling demand), `OpenHabLight` (HSB colour), `OpenHabRollershutter` (OH-specific cover with inverted position semantics).

### StateChangeEvent

CDI async event fired when a device's state changes. Carries `before`, `after`, `changedCapabilities` set, `timestamp`, and `providerId`. Fired via `fireAsync()` — consumers must use `@ObservesAsync`. The `deriveChangedCapabilities()` static method compares `capabilities()` maps to produce the diff.

### DeviceCommand

Immutable command record: `targetDeviceId`, `action`, `parameters`, `source`, `correlationId`. Static factory methods for common actions: `turnOn`, `turnOff`, `setTemperature`, `lock`, `unlock`, `setPosition`, `setVolume`. Action constants: `ACTION_TURN_ON`, `ACTION_TURN_OFF`, `ACTION_SET_TEMPERATURE`, `ACTION_LOCK`, `ACTION_UNLOCK`, `ACTION_SET_POSITION`, `ACTION_SET_VOLUME`.

---

## Module Structure

| Module | Artifact | Contents |
|--------|----------|----------|
| `api` | `casehub-iot-api` | Core SPIs (`DeviceProvider`, `DeviceRegistry`), device class hierarchy, `StateChangeEvent`, `DeviceCommand`, `CommandResult`, enums (`DeviceClass`, `SensorType`, `ThermostatMode`, `ProviderStatus`), `CdiDeviceRegistry @ApplicationScoped`. Pure Java + Mutiny `provided`. **Note:** Jackson annotations added for `DeviceTypeIdResolver` polymorphic serialization (iot#5) — `api` is no longer a zero-framework-dependency module. |
| `homeassistant` | `casehub-iot-homeassistant` | `HomeAssistantProvider @ApplicationScoped` — REST API + WebSocket event stream. `HomeAssistantEntityMapper` maps HA states to device hierarchy. `HomeAssistantWebSocketClient` for real-time state subscriptions with exponential backoff reconnection. `HomeAssistantRestClient` for service calls (command dispatch). Supplement types: `HomeAssistantThermostat`, `HomeAssistantLight`, `HomeAssistantLock`. Config via `@ConfigMapping`: url, token, tenancyId, reconnect params. |
| `openhab` | `casehub-iot-openhab` | `OpenHabProvider @ApplicationScoped` — REST API + SSE event stream. Layered Equipment+Thing discovery: `OpenHabEntityMapper` maps Equipment Groups (semantic model), `OpenHabThingResolver` maps Things via two-signal model (thing-type category + channel itemType inference). `OpenHabSseClient` 4-phase pipeline with dual cache layers and `ThingStatusInfoChangedEvent` tracking. `OpenHabDeviceBuilder` shared between paths. `OpenHabRestClient` for item commands. Supplement types: `OpenHabThermostat`, `OpenHabLight`, `OpenHabRollershutter`. Auth: token or basic auth via `OpenHabAuthHeadersFactory` (`ClientHeadersFactory`). Config via `@ConfigMapping`: url, token, optional basicAuth, tenancyId, reconnect params, coalescing window, `thingDiscoveryEnabled` (default true). |
| `testing` | `casehub-iot-testing` | `MockDeviceProvider`, `MockDeviceRegistry`, `Fixtures` (Java-built fixture devices), `DeviceFixtureLoader` (YAML fixture loading), `DeviceTypeHandler` SPI (16 handlers for all device types including vendor supplements), `StateChangeEventPublisher`. Test scope only — never a compile or runtime dependency for downstream consumers. Provider modules use `<optional>true</optional>` for `DeviceTypeHandler` SPI compilation. |
| `bridge-persistence-memory` | `casehub-iot-bridge-persistence-memory` | In-memory `BridgeAuditStore` implementation — relocates original in-memory store with correct CDI priority. Used for testing and ephemeral deployments. |
| `bridge-persistence-jpa` | `casehub-iot-bridge-persistence-jpa` | JPA `BridgeAuditStore` — durable audit persistence with JSONB message storage (iot#38). Flyway migrations, Testcontainers PostgreSQL for tests. Configurable `@Scheduled` purge job for audit data retention (iot#40). |
| `bridge` | `casehub-iot-bridge` | Local bridge agent — event relay with CDI filter chain, WebSocket client to bridge-server. Runs on-premises or at the edge; forwards `StateChangeEvent` to cloud consumers and relays commands back. |
| `bridge-server` | `casehub-iot-bridge-server` | Cloud-side library: `BridgeDeviceProvider implements DeviceProvider` — remote (bridged) devices look local to cloud consumers via the `DeviceProvider` SPI. `DeviceTypeIdResolver` for compound type ID serialization. 6 deployment topologies: SaaS, hybrid, multi-site, constrained edge, dev, multiple consumers (iot#5). |
| `webapp-api` | `casehub-iot-webapp-api` | Operational console API types — situational awareness view models, IoT action definitions. Pure Java. |
| `webapp-drools` | `casehub-iot-webapp-drools` | `IoTActionRiskClassifier` — Drools-based risk classification for IoT webapp actions (migrated to `StaticSetStrategy` — iot#47). |
| `webapp` | `casehub-iot-webapp` | Operational console Quarkus application — REST endpoints, JPA entities, quinoa frontend build. Provides IoT situational awareness dashboard (iot#44). |

---

## Provider Architecture

### Home Assistant

1:1 entity mapping — each HA `entity_id` maps to one `DeviceEntity`. Discovery via REST `GET /api/states`. Real-time via WebSocket: auth handshake → `subscribe_events` for `state_changed`. Reconnect with exponential backoff + jitter. Command dispatch via `POST /api/services/{domain}/{service}`.

### OpenHAB

Equipment Group mapping — one OpenHAB Equipment Group with multiple member Point items maps to a single `DeviceEntity`. Members are resolved by semantic tags (e.g. `Measurement+Temperature` → current temperature, `Control+Switch` → on/off state, `Setpoint+Temperature` → target temperature). Discovery via REST `GET /rest/items?type=Equipment&recursive=true`. Real-time via SSE `/rest/events` with Equipment-level coalescing — individual item state changes are resolved to their parent Equipment, re-mapped, and emitted as a single `StateChangeEvent` after a configurable coalescing window (default 50ms). Command dispatch via `POST /rest/items/{itemName}` — the target item is resolved from semantic tags matching the command action.

Auth: Bearer token (default) or HTTP Basic auth. Basic auth uses a CDI `ClientHeadersFactory` registered via `@RegisterProvider` on the REST clients.

### Thing-Scoped Discovery (Layered Equipment + Thing)

OpenHAB discovery now operates in two layers. Phase 1 discovers Equipment Groups (semantic model). Phase 2 discovers Things directly via `OpenHabThingResolver` — resolves `OpenHabThingDto` and its linked items to `ResolvedDeviceFields` using a two-signal model: thing-type category (binding metadata) merged with channel itemType inference. Priority-based channel scanning (Color > Dimmer > Rollershutter > Player > Power/Energy > Thermostat > Temperature > Humidity > Switch > Contact > Number). `OpenHabDeviceBuilder` is shared between Equipment and Thing paths. `OpenHabSseClient.connect()` runs a 4-phase pipeline: Equipment mapping → Thing index build (enhancing Equipment availability from Thing status) → Thing mapping for unmapped Things (`thingDiscoveryEnabled()` config, default `true`) → item state fetch for unmapped Things. Dual cache layers: `equipmentCache`/`deviceCache` (Equipment path) and `thingCache`/`thingDeviceCache` (Thing path). SSE `ThingStatusInfoChangedEvent` updates availability on both layers.

### SSE Device Status Streaming

`DeviceSseResource` (`GET /api/devices/stream`) produces `SERVER_SENT_EVENTS`. Sends initial "snapshot" operation with all devices, then streams "replace" operations on `@ObservesAsync StateChangeEvent`. Filters by tenancy ID.

---

## Testing Infrastructure

### Java Fixtures (`Fixtures`)

Static factory methods for every device type — `Fixtures.light()`, `Fixtures.thermostat()`, etc. Returns pre-built `DeviceEntity` instances with sensible defaults. Used for unit tests that need device instances without constructing builders.

### YAML Fixture Loading (`DeviceFixtureLoader`)

Loads device fixtures from YAML files via the `DeviceTypeHandler` SPI. Each device type has a handler that maps YAML fields to builder calls. 16 handlers cover all common and vendor-specific types. Equivalence tests verify that YAML-loaded fixtures produce identical objects to `Fixtures` factory methods. Enables data-driven test scenarios without Java code changes.

### StateChangeEventPublisher

Test utility that fires `StateChangeEvent` instances via CDI `fireAsync()` and captures the result. Used in `@QuarkusTest` integration tests that need to verify event handling.

---

## CBR Infrastructure

IoT situation resolution via case-based reasoning. Implemented across `webapp-api` (pure logic) and `webapp` (CDI wiring).

**Feature schemas** (`IoTCbrFeatureSchemas`): 4 `CbrFeatureSchema` instances — `hvacAnomaly()`, `safetyAlert()`, `securityAlert()`, `genericResponse()`. Each includes common fields (deviceClass, roomType, hourOfDay, dayType, season) plus schema-specific fields. Uses `CbrFeatureSchema`, `FeatureField`, `SimilaritySpec` from `io.casehub.neocortex.memory.cbr`.

**Retrieval** (`IoTCbrRetrievalService`): wraps `CbrCaseMemoryStore`, builds `CbrQuery`, returns `List<ResolutionSuggestion>` with `caseId`, `similarityScore`, `problem`, `solution`, `outcome`, `confidence`, `matchedFeatures`, `featureSimilarities`, `planSteps`.

**Feature extractors** (`IoTCbrFeatureExtractors`): static extractors per case type — `extractHvacAnomalyFeatures`, `extractSafetyAlertFeatures`, `extractSecurityAlertFeatures`, `extractGenericResponseFeatures`. Derives temporal features (hourOfDay, dayType, season) from `eventTimestamp`.

**Confidence model** (`ResolutionConfidence`): `bestSimilarity`, `outcomeConsistency`, `matchCount`, `ConfidenceLevel` (HIGH/MEDIUM/LOW/NONE). Static `compute()` method.

**CDI wiring**: `IoTCbrSchemaRegistration` (`@ApplicationScoped`) registers all schemas on `@Observes StartupEvent`. `IoTCbrRetrievalServiceProducer` CDI `@Produces` method.

**REST**: `GET /api/cases/{caseId}/suggestions` retrieves CBR suggestions. `POST /api/cases/{caseId}/suggestions/{pastCaseId}/accept` accepts a suggestion and writes `suggestedPlan` into the CaseContext.

---

## Bridge Deployment

**Docker**: `bridge/src/main/docker/Dockerfile.jvm` — based on `eclipse-temurin:21-jre-alpine`, non-root user (UID 1001), Quarkus app layout, port 8080. `bridge/docker-compose.yml` — single-service compose (image `ghcr.io/casehubio/iot-bridge:latest`, host network, env_file `.env`, volume mount for event persistence, health check via `/q/health/ready`).

**Deployment guide**: `bridge/DEPLOYMENT.md` — architecture diagram, prerequisites, quick start, full configuration reference (bridge agent, event store, Home Assistant, OpenHAB config tables), network requirements, data persistence, updating, troubleshooting (health check failures, auto-discovery, cloud connection, event replay, memory), security considerations, multi-platform support (amd64, arm64).

---

## Depends On

Nothing in the casehubio ecosystem (except `casehub-neocortex` for CBR — `CbrCaseMemoryStore`, `CbrFeatureSchema`, `FeatureField`, `SimilaritySpec` used by webapp-api). `api` module: Pure Java SPIs + Mutiny (`provided` scope) + Jackson annotations for `DeviceTypeIdResolver` (iot#5). Provider modules depend on Quarkus REST Client, Jackson, and WebSocket/SSE extensions.

## Depended On By

| Repo | Module | What it uses |
|------|--------|-------------|
| `casehub-life` | `app` | Device discovery, state events, command dispatch for household automation |
| `casehub-ops` | `iot` | IoT desired-state domain implementation (research) |

---

## Configuration

### Home Assistant (`casehub.iot.ha.*`)

| Property | Required | Default | Purpose |
|----------|----------|---------|---------|
| `casehub.iot.ha.url` | yes | — | HA instance URL |
| `casehub.iot.ha.token` | yes | — | Long-lived access token |
| `casehub.iot.ha.tenancy-id` | yes | — | Multi-tenant isolation key |
| `casehub.iot.ha.reconnect-base-seconds` | no | `5` | Backoff base |
| `casehub.iot.ha.reconnect-max-seconds` | no | `300` | Backoff cap |
| `casehub.iot.ha.ping-interval-seconds` | no | `30` | WebSocket keep-alive |
| `casehub.iot.ha.pong-timeout-seconds` | no | `10` | Pong deadline |

### OpenHAB (`casehub.iot.openhab.*`)

| Property | Required | Default | Purpose |
|----------|----------|---------|---------|
| `casehub.iot.openhab.url` | yes | — | OpenHAB instance URL |
| `casehub.iot.openhab.token` | yes (unless basic auth) | — | API token |
| `casehub.iot.openhab.basic-auth.username` | no | — | Basic auth username |
| `casehub.iot.openhab.basic-auth.password` | no | — | Basic auth password |
| `casehub.iot.openhab.tenancy-id` | yes | — | Multi-tenant isolation key |
| `casehub.iot.openhab.reconnect-base-seconds` | no | `5` | Backoff base |
| `casehub.iot.openhab.reconnect-max-seconds` | no | `300` | Backoff cap |
| `casehub.iot.openhab.coalesce-window-ms` | no | `50` | SSE event coalescing window |
| `casehub.iot.openhab.thing-discovery-enabled` | no | `true` | Enable Thing-scoped discovery (Phase 3 of layered pipeline) |
