---
id: PP-20260528-6b1d80
title: "Cross-foundation bridge modules live in the event-source repo as an optional submodule"
type: rule
scope: platform
applies_to: "casehub foundation repos when two peer modules need opt-in integration wiring"
severity: guidance
refs:
  - ../../PLATFORM.md
violation_hint: "A standalone repo created solely to bridge two foundation modules, or a bridge module placed in the event-consumer's repo rather than the event-source's repo"
created: 2026-05-28
---

When two peer foundation modules need an opt-in integration (module A defines the event or SPI types, module B provides the delivery infrastructure), the bridge module lives in A's repo as an optional submodule. It must appear before A's runtime module in the root `pom.xml` `<modules>` block so that other modules can take test-scope dependencies on it without build-order failures. Consuming apps activate it by adding the bridge artifact to their classpath — the bridge must never be a mandatory dependency of the runtime module. Precedents: `casehub-engine-ledger`, `casehub-engine-work-adapter` (in the engine repo), `casehub-qhorus-connectors` (in the qhorus repo, bridges `WatchdogAlertEvent` → `ConnectorService`).

**Exception — bidirectional bridges requiring runtime access:** when a bridge reacts to events from BOTH repos (e.g. `ChannelInitialisedEvent` from qhorus AND `InboundMessage` from connectors) AND requires runtime-tier classes (`ChannelGateway`, `ChannelService`) only available in one repo's runtime module, the bridge lives in the repo that owns the runtime classes. The protocol's goal — avoiding circular Maven dependencies — is still satisfied, because the bridge depends on the other repo's core module (not its runtime), preventing cycles. Precedent: `casehub-qhorus-connector-backend` (in qhorus repo) depends on `casehub-connectors-core` (connectors repo core module, not runtime) — no circular dependency.
