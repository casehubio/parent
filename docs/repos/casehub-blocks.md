# casehub-blocks

**GitHub:** [casehubio/blocks](https://github.com/casehubio/blocks)  
**Platform doc:** [PLATFORM.md](https://raw.githubusercontent.com/casehubio/parent/main/docs/PLATFORM.md)

---

## Purpose

Reusable building blocks composed from foundation primitives. Sits between the foundation tier (qhorus, work, engine) and the application tier (drafthouse, claudony, openclaw, aml, clinical, life). Provides higher-level abstractions that multiple applications need but that do not belong in any single foundation library.

**What blocks does:** packages recurring cross-application patterns into tested, reusable components -- oversight gate orchestration, structured conversation management, channel agent dispatch coordination, and context tracking across case lifecycles.

**What blocks does NOT do:** application logic, UI rendering, domain-specific workflows. If the capability requires knowledge of a specific business domain, it belongs in an application repo, not here.

---

## Key Abstractions

### Oversight Gate

Reusable oversight gate orchestration -- coordinates the approval lifecycle for actions that require human review before proceeding. Composes casehub-work (WorkItem creation for the gate) with casehub-engine (case signal on gate resolution).

### Structured Conversation

Managed conversation patterns over casehub-qhorus channels -- turn-taking, topic scoping, summary extraction. Provides a higher-level API than raw channel message dispatch for applications that need structured multi-turn agent interactions.

### Channel Agent Dispatch

Coordination of agent dispatch across qhorus channels -- manages which agents participate in which channels, handles provisioning lifecycle, and routes messages to the appropriate agent based on channel context.

### Context Tracking

Cross-lifecycle context tracking -- maintains contextual state across case phases and agent interactions. Composes casehub-engine case state with casehub-qhorus channel history to provide a unified context view for downstream consumers.

---

## Module Structure

Single module -- `casehub-blocks` is a flat library, not a multi-module extension.

| Module | Artifact | Contents |
|--------|----------|----------|
| (root) | `casehub-blocks` | All building block abstractions |

---

## Current State

Scaffold -- the repository structure exists but no blocks have been extracted yet. The abstractions listed above represent the intended scope based on patterns observed across application repos. Extraction will happen incrementally as patterns are identified and consolidated from existing consumers.

---

## Depends On

| Artifact | What it uses |
|----------|-------------|
| `casehub-qhorus-api` | Channel and message SPIs for structured conversation and channel dispatch |
| `casehub-work-api` | WorkItem types for oversight gate coordination |
| `casehub-engine-api` | Case orchestration SPIs for context tracking and gate signal routing |

---

## Depended On By

| Repo | What it uses |
|------|-------------|
| `casehub-drafthouse` | (planned) Structured conversation, channel dispatch |
| `claudony` | (planned) Oversight gate, context tracking |
| `casehub-openclaw` | (planned) Oversight gate, channel dispatch |
| `casehub-aml` | (planned) Oversight gate, context tracking |
| `casehub-clinical` | (planned) Oversight gate, structured conversation |
| `casehub-life` | (planned) Context tracking, channel dispatch |

---

## Configuration

No configuration properties yet -- scaffold phase.
