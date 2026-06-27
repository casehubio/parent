# Casehubio Application Tier

> **Purpose:** Reference for application repos built on the casehubio platform. Foundation
> repo sessions do not need this document unless explicitly asked to investigate how an
> application uses a platform feature. Application repo sessions should load both this
> document and [PLATFORM.md](PLATFORM.md).

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

| Repo | GitHub | Domain | Status |
|------|--------|--------|--------|
| `casehub-devtown` | [casehubio/devtown](https://github.com/casehubio/devtown) | AI-assisted software development — PR review, merge queue, trust-weighted reviewer routing | Active |
| `casehub-aml` | [casehubio/aml](https://github.com/casehubio/aml) | Anti-money laundering investigation — FinCEN-compliant audit, SAR workflow, adaptive investigation paths | Active |
| `casehub-clinical` | [casehubio/clinical](https://github.com/casehubio/clinical) | Clinical trial coordination — GCP/FDA compliance, multi-site sub-cases, adverse event escalation | Active |
| `casehub-life` | [casehubio/life](https://github.com/casehubio/life) | Personal life automation — household coordination, health, finance, elder care, legal compliance; tutorial: OpenClaw as execution layer. Layer 9 (planned): `casehub-iot` integration — Home Assistant and OpenHAB device abstraction, device-driven case types, community automation marketplace | Layer 2 (casehub-work) |
| `casehub-drafthouse` | [casehubio/drafthouse](https://github.com/casehubio/drafthouse) | MCP-driven document review — four MCP tools live: `start_review`, `update_selection`, `query_review`, `end_review` (`DraftHouseMcpTools @ApplicationScoped`). Structured agent-to-agent debate loop (review manifest), deterministic summary projection via `ChannelProjection<ReviewState>`, LangChain4j + Claude Agent SDK provider pattern. `ReviewSessionResource` (deprecated REST) removed. | Active |
| `quarkmind` | [mdproctor/quarkmind](https://github.com/mdproctor/quarkmind) | StarCraft II game AI — living lab proving the CaseHub harness pattern at millisecond game-loop granularity outside regulated domains | Active |
| `casehub-soc` | [casehubio/soc](https://github.com/casehubio/soc) | Security Operations Center — multi-agent cyber incident response, trust-weighted triage, CBR-based incident correlation, oversight-gated containment | Scaffold |
| `casehub-fsitrading` | [casehubio/fsitrading](https://github.com/casehubio/fsitrading) | FSI Trading — multi-agent trading automation, overnight bot management, situation detection and response, regulatory compliance (MiFID II, Dodd-Frank) | Scaffold |

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
See [PLATFORM.md — Build Order](PLATFORM.md) for the full dependency graph.

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

All other capabilities live in the foundation. See [PLATFORM.md — Capability Ownership](PLATFORM.md).

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
