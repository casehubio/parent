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
| `api` | `casehub-iot-api` | Core SPIs (`DeviceProvider`, `DeviceRegistry`), device class hierarchy, `StateChangeEvent`, `DeviceCommand`, `CommandResult`, enums (`DeviceClass`, `SensorType`, `ThermostatMode`, `ProviderStatus`), `CdiDeviceRegistry @ApplicationScoped`. Pure Java + Mutiny `provided` — no Quarkus runtime dependency. |
| `homeassistant` | `casehub-iot-homeassistant` | `HomeAssistantProvider @ApplicationScoped` — REST API + WebSocket event stream. `HomeAssistantEntityMapper` maps HA states to device hierarchy. `HomeAssistantWebSocketClient` for real-time state subscriptions with exponential backoff reconnection. `HomeAssistantRestClient` for service calls (command dispatch). Supplement types: `HomeAssistantThermostat`, `HomeAssistantLight`, `HomeAssistantLock`. Config via `@ConfigMapping`: url, token, tenancyId, reconnect params. |
| `openhab` | `casehub-iot-openhab` | `OpenHabProvider @ApplicationScoped` — REST API + SSE event stream. `OpenHabEntityMapper` maps Equipment Groups (semantic model) to device hierarchy. `OpenHabSseClient` for real-time state with Equipment-level coalescing (batches rapid item-level changes into a single Equipment-level event). `OpenHabRestClient` for item commands. Supplement types: `OpenHabThermostat`, `OpenHabLight`, `OpenHabRollershutter`. Auth: token or basic auth via `OpenHabAuthHeadersFactory` (`ClientHeadersFactory`). Config via `@ConfigMapping`: url, token, optional basicAuth, tenancyId, reconnect params, coalescing window. |
| `testing` | `casehub-iot-testing` | `MockDeviceProvider`, `MockDeviceRegistry`, `Fixtures` (Java-built fixture devices), `DeviceFixtureLoader` (YAML fixture loading), `DeviceTypeHandler` SPI (16 handlers for all device types including vendor supplements), `StateChangeEventPublisher`. Test scope only — never a compile or runtime dependency for downstream consumers. Provider modules use `<optional>true</optional>` for `DeviceTypeHandler` SPI compilation. |
| `bridge` | `casehub-iot-bridge` | Lightweight bridge runtime for cloud/hybrid deployment mode. No domain logic — pure event forwarding and command relay. |

---

## Provider Architecture

### Home Assistant

1:1 entity mapping — each HA `entity_id` maps to one `DeviceEntity`. Discovery via REST `GET /api/states`. Real-time via WebSocket: auth handshake → `subscribe_events` for `state_changed`. Reconnect with exponential backoff + jitter. Command dispatch via `POST /api/services/{domain}/{service}`.

### OpenHAB

Equipment Group mapping — one OpenHAB Equipment Group with multiple member Point items maps to a single `DeviceEntity`. Members are resolved by semantic tags (e.g. `Measurement+Temperature` → current temperature, `Control+Switch` → on/off state, `Setpoint+Temperature` → target temperature). Discovery via REST `GET /rest/items?type=Equipment&recursive=true`. Real-time via SSE `/rest/events` with Equipment-level coalescing — individual item state changes are resolved to their parent Equipment, re-mapped, and emitted as a single `StateChangeEvent` after a configurable coalescing window (default 50ms). Command dispatch via `POST /rest/items/{itemName}` — the target item is resolved from semantic tags matching the command action.

Auth: Bearer token (default) or HTTP Basic auth. Basic auth uses a CDI `ClientHeadersFactory` registered via `@RegisterProvider` on the REST clients.

---

## Testing Infrastructure

### Java Fixtures (`Fixtures`)

Static factory methods for every device type — `Fixtures.light()`, `Fixtures.thermostat()`, etc. Returns pre-built `DeviceEntity` instances with sensible defaults. Used for unit tests that need device instances without constructing builders.

### YAML Fixture Loading (`DeviceFixtureLoader`)

Loads device fixtures from YAML files via the `DeviceTypeHandler` SPI. Each device type has a handler that maps YAML fields to builder calls. 16 handlers cover all common and vendor-specific types. Equivalence tests verify that YAML-loaded fixtures produce identical objects to `Fixtures` factory methods. Enables data-driven test scenarios without Java code changes.

### StateChangeEventPublisher

Test utility that fires `StateChangeEvent` instances via CDI `fireAsync()` and captures the result. Used in `@QuarkusTest` integration tests that need to verify event handling.

---

## Depends On

Nothing in the casehubio ecosystem. Pure Java SPIs + Mutiny (`provided` scope) in `api`. Provider modules depend on Quarkus REST Client, Jackson, and WebSocket/SSE extensions.

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
