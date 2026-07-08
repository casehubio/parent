# Platform Overview

> **Scope:** Tier architecture, repository map, build order, upstream framework alignment
> **Audience:** All
> **Key repos:** All
> **Protocols:** None specific

## What We're Building

A production-grade, compliance-first infrastructure stack for multi-agent AI systems on Quarkus. Targeted at regulated deployments (EU AI Act Art.12, GDPR Art.17/22).

Four tiers, always kept separate:

- **Foundation** — audit ledger, human task primitives, agent communication mesh, outbound connectors. Independently embeddable in any Quarkus app. Domain-agnostic.
- **Orchestration** — `casehub-engine` coordinates agents via hybrid choreography+blackboard. Depends on foundation only.
- **Integration** — `claudony` wires everything together and surfaces it in a browser dashboard. Depends on orchestration.
- **Application** — domain-specific applications built on the foundation. Each is a separate repo with no domain knowledge in the foundation. The pattern: bring your domain logic, use foundation primitives, modify nothing below.

## Repository Map

| Repo | GitHub | One-liner | Tier |
|------|--------|-----------|------|
| `casehub-parent` | [casehubio/parent](https://github.com/casehubio/parent) | BOM, CI dashboards, full-stack build tooling | — |
| `casehub-platform` | [casehubio/platform](https://github.com/casehubio/platform) | Zero-dep foundational SPIs — Path, Preferences, Identity. Memory SPI types migrated to neocortex | Foundation |
| `casehub-worker` | [casehubio/casehub-worker](https://github.com/casehubio/casehub-worker) | Worker primitive foundation — Worker, Capability, WorkerFunction, WorkerResult, WorkerOutcome | Foundation |
| `casehub-ledger` | [casehubio/ledger](https://github.com/casehubio/ledger) | Immutable tamper-evident audit ledger + trust scoring | Foundation |
| `casehub-work` | [casehubio/work](https://github.com/casehubio/work) | Human task lifecycle (WorkItem inbox, SLA, delegation, routing) | Foundation |
| `casehub-qhorus` | [casehubio/qhorus](https://github.com/casehubio/qhorus) | Peer-to-peer agent communication mesh | Foundation |
| `casehub-connectors` | [casehubio/connectors](https://github.com/casehubio/connectors) | Outbound and inbound message connectors (Slack, Teams, SMS, email) | Foundation |
| `casehub-iot` | [casehubio/iot](https://github.com/casehubio/iot) | Typed IoT device abstraction layer — DeviceEntity hierarchy (Matter-aligned) | Foundation |
| `casehub-ras` | [casehubio/casehub-ras](https://github.com/casehubio/casehub-ras) | Reticular Activating System — situational awareness and reactive case creation | Foundation |
| `casehub-desiredstate` | [casehubio/casehub-desiredstate](https://github.com/casehubio/casehub-desiredstate) | Generic desired-state management runtime | Foundation |
| `casehub-blocks` | [casehubio/blocks](https://github.com/casehubio/blocks) | Reusable building blocks composed from qhorus, engine, work primitives | Foundation-adjacent |
| `casehub-blocks-ui` | [casehubio/blocks-ui](https://github.com/casehubio/blocks-ui) | Shared UI components for CaseHub applications | Foundation-adjacent |
| `casehub-engine` | [casehubio/engine](https://github.com/casehubio/engine) | Hybrid choreography+blackboard orchestration engine | Orchestration |
| `claudony` | [casehubio/claudony](https://github.com/casehubio/claudony) | Remote Claude CLI sessions + unified ecosystem dashboard | Integration |
| `casehub-openclaw` | [casehubio/openclaw](https://github.com/casehubio/openclaw) | CaseHub × OpenClaw integration | Integration |
| `casehub-workers` | [casehubio/workers](https://github.com/casehubio/workers) | HTTP, Camel, and GitHub Actions worker dispatch adapters | Integration |
| `casehub-ops` | [casehubio/casehub-ops](https://github.com/casehubio/casehub-ops) | Domain implementations of casehub-desiredstate SPIs for CaseHub-specific deployment concerns | Integration |
| `casehub-eidos` | [casehubio/eidos](https://github.com/casehubio/eidos) | Agent identity — descriptor, discovery registry, vocabulary system, system prompt generation | Foundation |
| `casehub-neocortex` | [casehubio/neocortex](https://github.com/casehubio/neocortex) | ONNX neural text inference + LangChain4j RAG integration + agent memory SPI | Foundation |
| `casehub-pages` | [casehubio/casehub-pages](https://github.com/casehubio/casehub-pages) | Web application framework (TypeScript/Yarn foundation module) | Foundation |
| `casehub-devtown` | [casehubio/devtown](https://github.com/casehubio/devtown) | PR review automation, merge queue management, GitHub integration | Application |
| `casehub-aml` | [casehubio/aml](https://github.com/casehubio/aml) | Anti-money laundering case management | Application |
| `casehub-clinical` | [casehubio/clinical](https://github.com/casehubio/clinical) | Clinical adverse event investigation | Application |
| `casehub-life` | [casehubio/life](https://github.com/casehubio/life) | Personal life automation | Application |
| `casehub-drafthouse` | [casehubio/drafthouse](https://github.com/casehubio/drafthouse) | Document review and multi-participant LLM debate | Application |
| `casehub-soc` | [casehubio/soc](https://github.com/casehubio/soc) | Security operations center | Application |
| `casehub-fsitrading` | [casehubio/fsitrading](https://github.com/casehubio/fsitrading) | Financial services trading compliance | Application |
| `quarkmind` | [casehubio/quarkmind](https://github.com/casehubio/quarkmind) | StarCraft II game AI | Application |
| `flow` (scaffold) | [mdproctor/flow](https://github.com/mdproctor/flow) | Reference deployment | Application |

## Build / Dependency Order

```
casehub-parent              (BOM — publish first; all others import it)
  casehub-platform          (no casehubio deps — foundational SPIs)
  casehub-worker            (no casehubio deps — Worker, Capability primitives)
  casehub-ledger            (no casehubio deps)
  casehub-connectors        (no casehubio deps)
  casehub-iot               (depends on casehub-platform-api for CloudEvent)
  casehub-work              (api: depends on casehub-platform-api)
  casehub-qhorus            (depends on casehub-ledger)
  casehub-eidos             (depends on casehub-ledger)
  casehub-neocortex         (memory-api: zero casehubio deps; rag-*: depends on platform-api)
  casehub-engine            (depends on casehub-work-core + optionally ledger + eidos-api)
  casehub-ras               (depends on casehub-platform-api + engine-api)
  casehub-desiredstate      (depends on casehub-platform-api)
  casehub-blocks            (depends on qhorus-api, work-api, engine-api)
  casehub-blocks-ui         (TypeScript/Yarn; depends on casehub-pages)
  casehub-engine-ai         (optional — depends on engine-api)
  casehub-engine-flow       (optional — depends on engine-common only)
  claudony                  (depends on qhorus + implements engine SPIs)
  casehub-openclaw          (depends on qhorus + engine SPIs)
  casehub-workers           (depends on engine-api + engine-common)
  casehub-ops               (depends on desiredstate + platform-api)

  — Application tier (opt-in, off by default in CI) —
  casehub-life
  casehub-drafthouse
  quarkmind
  casehub-soc
  casehub-fsitrading
```

## Upstream Consistency — Serverless Workflow 1.0 and quarkus-flow

CaseHub is built on top of CNCF Serverless Workflow 1.0 (via quarkus-flow). Before designing any new abstraction in casehub-engine or any harness, check whether Serverless Workflow 1.0 or quarkus-flow already defines it. Consistency with upstream is preferred over reinvention.

This applies to: execution models, case/workflow definition structure, trigger types, expression evaluation, worker/activity contracts, sub-case/sub-workflow composition, and any serialization format decisions.

**The check:** if a concept exists in Serverless Workflow 1.0 or quarkus-flow — use the same name, the same shape, and the same semantics. If CaseHub must diverge (e.g. to add compliance or trust concerns), document the divergence explicitly.

**Known inheritors of this principle:**
- Case definition three-layer architecture (YAML → schema model → canonical API model + fluent DSL) — aligned with Serverless Workflow 1.0 structure
