---
id: PP-20260521-7369c1
title: "Apps using casehub-ledger + casehub-work + casehub-qhorus together require two Hibernate persistence units"
type: rule
scope: application
applies_to: "Any casehub harness embedding all three of casehub-ledger, casehub-work, and casehub-qhorus"
severity: important
refs:
  - casehubio/aml#12
violation_hint: "Single-PU configuration with all three extensions causes bean ambiguity or EntityManager routing failure — ledger entities land on the wrong PU, or casehub-work cannot find its @Default EntityManager."
created: 2026-05-21
---

casehub-work expects a `@Default` EntityManager. casehub-qhorus always runs on a named `qhorus` datasource (platform convention). casehub-ledger's CDI producer selects by datasource name — when blank, it selects `@Default`. Putting all three on a single PU breaks one of these constraints.

**Required configuration: two persistence units**

| PU | Datasource | Hibernate packages |
|----|------------|--------------------|
| default | `default` | `io.casehub.work.runtime.model`, `io.casehub.work.runtime.filter`, app domain packages |
| qhorus | `qhorus` (named) | `io.casehub.qhorus.runtime`, `io.casehub.ledger.runtime.model`, `io.casehub.ledger.model` |

**application.properties skeleton:**

```properties
# Default PU — casehub-work + app domain
quarkus.hibernate-orm.packages=io.casehub.work.runtime.model,io.casehub.work.runtime.filter,<app.domain.package>

# Qhorus PU — casehub-qhorus + casehub-ledger
quarkus.hibernate-orm."qhorus".datasource=qhorus
quarkus.hibernate-orm."qhorus".packages=io.casehub.qhorus.runtime,io.casehub.ledger.runtime.model,io.casehub.ledger.model

# Route ledger CDI producer to the qhorus PU
casehub.ledger.datasource=qhorus

# Datasource URLs
quarkus.datasource.jdbc.url=jdbc:postgresql://localhost:5432/appdb
quarkus.datasource.qhorus.jdbc.url=jdbc:postgresql://localhost:5432/qhorusdb
```

**Why ledger goes on the qhorus PU:** casehub-qhorus already owns the `qhorus` named datasource. casehub-ledger's producer is datasource-name-routed — `casehub.ledger.datasource=qhorus` directs it to the qhorus PU, keeping the default PU clean for casehub-work. This matches claudony's validated configuration.

**Also required:** both casehub-work Hibernate packages (`runtime.model` + `runtime.filter`) — see [casehub-work-hibernate-packages.md](casehub-work-hibernate-packages.md).
