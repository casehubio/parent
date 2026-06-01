---
id: PP-20260601-c43112
title: "Bridge-module SPIs that reference bridge-internal types live in the bridge module, not api/spi/"
type: rule
scope: platform
applies_to: "any casehub bridge module (connector-backend, engine-ledger, etc.) that defines a consumer-facing SPI"
severity: important
refs:
  - consumer-spi-placement.md
  - cross-foundation-bridge-module-placement.md
violation_hint: "A SPI in api/spi/ whose parameter or return types come from casehub-connectors-core or another dependency not in the api module's compile graph — causes compilation failure in api or forces an unwanted transitive dependency onto all api consumers"
created: 2026-06-01
---

When a bridge module defines a consumer-facing SPI whose parameter or return types come from the bridge module's own dependencies (types not present in `api/`), the SPI interface must live in the bridge module rather than `api/spi/`. Consumers who implement the SPI already depend on the bridge module to activate it — the bridge module is the correct package boundary. Placing the SPI in `api/spi/` would force `api` to depend on the bridge's dependency, polluting all `api` consumers with an unwanted transitive dependency. The `@DefaultBean` default implementation follows the same rule: it lives in the bridge module alongside the SPI. Precedent: `AutoChannelPolicy` in `casehub-qhorus-connector-backend` — its parameter type `InboundMessage` comes from `casehub-connectors-core`, which `casehub-qhorus-api` does not and must not depend on.
