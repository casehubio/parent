# Convention: Human Governance Channels Must Restrict allowedTypes

**Applies to:** All projects using the Qhorus NormativeChannelLayout oversight channel
**Severity:** Important — wrong type silently corrupts the governance record and drops content

## The Problem

The oversight channel is the human governance layer: agents post QUERY when they need
a human decision; humans post COMMAND to inject directives. If a UI dropdown defaults
to EVENT (the telemetry type), the message is accepted by the work channel but its
content is null (see `qhorus-event-content-null.md`), and no obligation is created.
The governance act disappears silently — it appears in the feed with no content and
has no effect on any agent's CommitmentStore.

## The Rule

**Always create the oversight channel with `allowedTypes=QUERY,COMMAND`.** This rejects
EVENT, STATUS, DONE, FAILURE, and HANDOFF at the MCP layer before they reach the
database — a clear `MessageTypeViolationException` rather than silent corruption.

```
create_channel("case-{id}/oversight", "Human governance", "APPEND",
               allowed_types="QUERY,COMMAND")
```

Human actors post:
- **COMMAND** — a directive to an agent ("proceed", "hold", "escalate")
- **QUERY** — a question to an agent ("what is the scope of finding #2?")

Human actors never post EVENT. EVENT is machine telemetry — it has no governance
semantics and its content is always null.

**UI interjection docks** that target the oversight channel should:
1. Query the channel's `allowedTypes` and filter the type dropdown accordingly
2. Default to COMMAND, not EVENT

## Where This Applies

Claudony's interjection dock, any dashboard panel that allows posting to oversight,
and any test that creates the NormativeChannelLayout. The three-channel setup
(`work` / `observe` / `oversight`) is only complete when `allowedTypes` is set on
both `observe` (EVENT only) and `oversight` (QUERY,COMMAND only).
