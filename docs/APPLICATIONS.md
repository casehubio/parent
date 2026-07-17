# Casehubio Application Tier

> **Purpose:** Reference for application repos built on the casehubio platform. Foundation
> repo sessions do not need this document unless explicitly asked to investigate how an
> application uses a platform feature. Application repo sessions should start with
> [INDEX.md](INDEX.md) and [guides/building-apps.md](guides/building-apps.md).

---

## What the Application Tier Is

Domain-specific applications built on top of the casehubio foundation. Each application:

- Brings its own domain logic (PRs, clinical protocols, AML investigations)
- Uses foundation primitives as-is — does not modify anything below
- Owns its own database schema, REST API, and compliance obligations
- Has no knowledge of other application repos

The pattern: **bring your domain, use the platform, modify nothing below.**

---

## Repository Map

| Repo | GitHub | Domain | UI | blocks-ui Components | Status |
|------|--------|--------|-----|---------------------|--------|
| `casehub-devtown` | [casehubio/devtown](https://github.com/casehubio/devtown) | AI-assisted software development — PR review, merge queue with batch composition/bisection/SLA, trust-weighted reviewer routing, CBR-enhanced matching | Web UI (Quinoa) | work-item-inbox, trust-score-panel, channel-activity | Active |
| `casehub-aml` | [casehubio/aml](https://github.com/casehubio/aml) | Anti-money laundering investigation — FinCEN-compliant audit, SAR workflow, adaptive investigation paths, GDPR Art.17 erasure | Web UI (Quinoa) | work-item-inbox, accountability-view, investigation-view | Active |
| `casehub-clinical` | [casehubio/clinical](https://github.com/casehubio/clinical) | Clinical trial coordination — GCP/FDA compliance, multi-site sub-cases, adverse event escalation, IND deadline enforcement, GDPR patient-scoped erasure | Web UI (Quinoa + blocks-ui) | approval-gate, sla-indicator, kpi-metric-row, data-table, work-item-inbox | Active |
| `casehub-life` | [casehubio/life](https://github.com/casehubio/life) | Personal life automation — household coordination, health, finance, elder care, legal compliance; 6 case hubs (appointment, home maintenance, travel, care, contractor, financial review); AgentExec direct-call integration, GDPR actor erasure | No UI yet | — | Layers 2–6, 8 complete (work + qhorus + ledger + engine + trust routing + CBR) |
| `casehub-drafthouse` | [casehubio/drafthouse](https://github.com/casehubio/drafthouse) | MCP-driven document review + multi-participant LLM debate. 7 brainstorming MCP tools, 10 debate MCP tools, structured design-review output, document timeline, context meter, export. Multi-LLM reviewer registry (Eidos identity model). Debate session persistence with pluggable Store SPI. | Web UI (Quinoa + casehub-pages) | — | Active |
| `quarkmind` | [casehubio/quarkmind](https://github.com/casehubio/quarkmind) | StarCraft II game AI — living lab proving the CaseHub harness pattern at millisecond game-loop granularity outside regulated domains. Pattern classifier, phase-adaptive dominance, milestone-based trust scoring. | SC2 client integration | — | Active |
| `casehub-soc` | [casehubio/soc](https://github.com/casehubio/soc) | Security Operations Center — multi-agent cyber incident response, trust-weighted triage, CBR-based incident correlation, oversight-gated containment | Planned | — | Scaffold |
| `casehub-fsitrading` | [casehubio/fsitrading](https://github.com/casehubio/fsitrading) | FSI Trading — multi-agent trading automation, overnight bot management, situation detection and response, regulatory compliance (MiFID II, Dodd-Frank) | Planned | — | Scaffold |

---

## Platform Dependencies

All application repos depend on the same foundation subset:

```
casehub-devtown  ┐
casehub-aml      ├── depends on: engine + ledger + work + qhorus (+ connectors where needed)
casehub-clinical ┘
casehub-life     — depends on: full foundation stack + casehub-openclaw (Layer 7+)
casehub-drafthouse — depends on: qhorus (initially; engine + ledger + work added later)
casehub-soc      — depends on: full foundation stack (engine + ledger + work + qhorus + worker + platform)
casehub-fsitrading — depends on: full foundation stack (engine + ledger + work + qhorus + worker + platform)
```

Application repos are **opt-in and off by default** in the platform CI pipeline.
See [platform/overview.md](platform/overview.md) for the full dependency graph and build order.

---

## Capability Ownership

| Capability | Owner |
|---|---|
| Software dev domain logic (PR review, merge queue, capability tags) | `casehub-devtown` |
| AML domain logic (investigation, SAR workflow, FinCEN compliance) | `casehub-aml` |
| Clinical trial domain logic (protocol, site management, GCP/FDA) | `casehub-clinical` |
| Personal life automation (household, health, finance, care, legal) | `casehub-life` |
| MCP-driven document review (multi-LLM critique, version-tracked revisions) | `casehub-drafthouse` |
| SC2 game AI (strategy, economics, tactics, scouting plugin agents) | `quarkmind` |
| SOC domain logic (incident triage, threat intel, forensics, containment, SOC2/DORA compliance) | `casehub-soc` |
| FSI trading domain logic (strategy execution, overnight bot management, market situation detection, MiFID II/Dodd-Frank) | `casehub-fsitrading` |

All other capabilities live in the foundation. See [INDEX.md](INDEX.md) for platform discovery and [guides/building-apps.md](guides/building-apps.md) for the pattern catalogue showing what shared capabilities exist across apps.

---

## Boundary Rules for Application Repos

**Domain logic stays in the application.** If a feature requires knowledge of a specific
business domain (git, PRs, clinical protocols, AML investigations), it belongs here — not
in the foundation. Foundation repos must remain domain-agnostic.

**Do not modify foundation repos to accommodate application needs.** If the platform
doesn't support something you need, raise it as a platform capability request. The correct
flow is: define the need → propose an SPI or extension point in the foundation → implement
the application-specific behaviour using that extension point.

**Application repos do not depend on each other.** devtown, aml, and clinical are
independent. If a capability is useful across multiple applications, it belongs in the
foundation, not as a shared application library.

---

## Per-Repo Deep Dives

| Repo | Raw URL |
|------|---------|
| `casehub-devtown` | https://raw.githubusercontent.com/casehubio/parent/main/docs/repos/casehub-devtown.md |
| `casehub-aml` | https://raw.githubusercontent.com/casehubio/parent/main/docs/repos/casehub-aml.md |
| `casehub-clinical` | https://raw.githubusercontent.com/casehubio/parent/main/docs/repos/casehub-clinical.md |
| `casehub-life` | https://raw.githubusercontent.com/casehubio/parent/main/docs/repos/casehub-life.md |
| `casehub-drafthouse` | https://raw.githubusercontent.com/casehubio/parent/main/docs/repos/casehub-drafthouse.md |
| `quarkmind` | https://raw.githubusercontent.com/casehubio/parent/main/docs/repos/quarkmind.md |
| `casehub-soc` | https://raw.githubusercontent.com/casehubio/parent/main/docs/repos/casehub-soc.md |
| `casehub-fsitrading` | https://raw.githubusercontent.com/casehubio/parent/main/docs/repos/casehub-fsitrading.md |
