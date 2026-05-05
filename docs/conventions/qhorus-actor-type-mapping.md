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
| `"user"` | `HUMAN` | Explicit rule in `ActorTypeResolver` (casehubio/ledger#75) |
| `"agent"` | `AGENT` | Explicit rule in `ActorTypeResolver` (casehubio/ledger#75) |

## Interop Contract for A2A AI Callers

An A2A caller that is an AI agent SHOULD signal this by:
1. Registering as a Qhorus Instance before calling
2. Including an Agent Card URL in request metadata
3. Using a sender ID in versioned persona format (`model:persona@version`)
4. Setting the `x-qhorus-actor-type: AGENT` header

Without any of these signals, the caller is conservatively classified as `HUMAN`.

Refs: casehubio/qhorus#131, casehubio/qhorus#135
