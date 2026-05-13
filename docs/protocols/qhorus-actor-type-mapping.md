---
id: PP-20260508-8f317e
title: "All ActorType values must map to the canonical casehub ledger vocabulary"
type: rule
scope: platform
applies_to: "All casehubio projects that assign or resolve ActorType"
severity: important
refs: []
violation_hint: "Missing protocol signals (agent card, instanceId, x-qhorus-actor-type header) cause AI agents to be classified as HUMAN"
created: 2026-05-08
---

# Qhorus Actor Type Mapping Convention

## ActorType Vocabulary

All casehubio projects use `io.casehub.ledger.api.model.ActorType`:

| Value | Meaning |
|---|---|
| `AGENT` | Autonomous AI agent acting programmatically |
| `HUMAN` | Human user acting through a UI, API, or messaging platform |
| `SYSTEM` | Automated system process (scheduler, rule engine, pipeline) |

## Channel Backend Alignment

Qhorus backend interfaces are named after `ActorType`:
- `AgentChannelBackend` → `ActorType.AGENT`
- `HumanParticipatingChannelBackend` → `ActorType.HUMAN`
- `HumanObserverChannelBackend` → `ActorType.HUMAN`

## Sender ID Conventions

| Context | Sender ID format | Resolves to |
|---|---|---|
| Human inbound via participating backend | `human:{externalSenderId}` | `ActorType.HUMAN` |
| Human signal via observer backend | `human:{externalSenderId}` | `ActorType.HUMAN` |
| Human approval response | `Senders.HUMAN` = `"human"` | `ActorType.HUMAN` |
| AI agent | Qhorus `instanceId` or persona format | `ActorType.AGENT` |

## A2A Protocol Role Mapping

| A2A role | Qhorus ActorType | Notes |
|---|---|---|
| `"user"` | `HUMAN` | Explicit rule in `ActorTypeResolver` — implemented in casehubio/ledger#75 |
| `"agent"` | `AGENT` | Explicit rule in `ActorTypeResolver` — implemented in casehubio/ledger#75 |

## Interop Contract for A2A AI Callers

An A2A caller that is an AI agent SHOULD signal this by:
1. Registering as a Qhorus Instance before calling
2. Including an Agent Card URL in request metadata
3. Using a sender ID in versioned persona format (`model:persona@version`)
4. Setting the `x-qhorus-actor-type: AGENT` header

Without any of these signals, the caller is conservatively classified as `HUMAN`.

## A2A Sender Identity Resolution Chain (A2AActorResolver)

When an inbound A2A message carries `role:"user"`, Qhorus resolves the sender's
`ActorType` via a 6-step chain in `A2AActorResolver` (casehubio/qhorus#135):

1. `x-qhorus-actor-type` HTTP header (`HUMAN` / `AGENT` / `SYSTEM`) — explicit override; invalid values silently fall through
2. `metadata.agentId` present in Instance registry → `AGENT`
3. `metadata.agentCardUrl` non-blank → `AGENT` (A2A-native identity signal, survives relay)
4. `metadata.agentId` matches versioned persona format (e.g. `claude:analyst@v1`) → `AGENT`
5. `metadata.agentId` matches `system` or `system:*` → `SYSTEM`
6. Default → `HUMAN` (conservative — demands more accountability, not less)

For `role:"agent"`: unconditional `AGENT` — the chain does not apply.

The sender string recorded in the message is constructed to correctly classify
via `ActorTypeResolver.resolve()`: `AGENT` → `agentId` (if structured) or `"agent"`;
`HUMAN` → `"human:" + (agentId ?? role)`; `SYSTEM` → `agentId` or `"system"`.

Refs: casehubio/qhorus#131, casehubio/qhorus#135
