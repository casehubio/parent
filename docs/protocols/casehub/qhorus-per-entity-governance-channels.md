---
id: PP-20260521-f39085
title: "Per-entity governance channels — name oversight channel after the entity, not the actor"
type: rule
scope: application
applies_to: "any casehub harness issuing COMMANDs via qhorus for governance decisions (PI authorisation, IRB review, DSMB oversight)"
severity: important
refs:
  - casehubio/clinical#5
  - casehubio/qhorus#154
violation_hint: "Per-actor channel names (e.g. clinical/site/{siteId}/pi-oversight) cannot correlate a response to a specific entity when correlationId is null. Multiple concurrent governance requests from the same actor produce unresolvable responses."
created: 2026-05-21
---

`ChannelGateway.receiveHumanMessage()` passes `correlationId=null` to `MessageService` (qhorus#154). The channel name is the only reliable way to identify which entity a human response belongs to.

Name governance channels after the entity being governed, not the actor receiving the command:

```
# Wrong — per-actor channel
clinical/site/{siteId}/pi-oversight

# Correct — per-entity channel
clinical/deviation/{deviationId}/pi-oversight
```

The per-entity pattern makes the entity identity structural — the channel name IS the entity identifier. It also enables concurrent governance of multiple entities by the same actor: a PI can have multiple active deviations, each with its own channel and Commitment, with responses unambiguously routed.

**When to revisit:** When casehubio/qhorus#154 ships (`InboundHumanMessage.correlationId`), per-actor channels become viable again. The per-entity pattern remains valid regardless — prefer it unless actor-centric grouping is a specific product requirement.
