---
id: PP-20260521-3e185a
title: "InboundNormaliser implementations must scope to relevant channel patterns"
type: rule
scope: application
applies_to: "any casehub harness that implements InboundNormaliser"
severity: important
refs:
  - casehubio/clinical#5
  - GE-20260517-f28d15
violation_hint: "Domain-specific normaliser applied to all channels. Messages on governance channels for other domains are misclassified as DONE/DECLINE, creating unintended Commitment state transitions."
created: 2026-05-21
---

`ChannelGateway` injects `InboundNormaliser` as a single CDI bean — there is no per-channel normaliser registration. The `ChannelRef` parameter in `normalise(ChannelRef, InboundHumanMessage)` exists precisely to enable scoping; implementations must use it.

Any `InboundNormaliser` must check the channel name before applying domain-specific message type detection. Without this check, domain-specific parsing applies globally and silently misclassifies messages on unrelated channels.

```java
@ApplicationScoped
public class ClinicalInboundNormaliser implements InboundNormaliser {

    @Override
    public NormalisedMessage normalise(ChannelRef channel, InboundHumanMessage raw) {
        // Scope check FIRST — SPI is application-wide
        MessageType type = isRelevantChannel(channel.name())
            ? detectDomainType(raw.content())
            : MessageType.QUERY;  // default for all other channels
        return new NormalisedMessage(type, raw.content(), "human:" + raw.externalSenderId());
    }

    private boolean isRelevantChannel(String name) {
        return name != null && name.contains("/pi-oversight");
    }
}
```

The default for unrecognised channels should be `MessageType.QUERY` — the least disruptive interpretation. Using `DONE` or `DECLINE` as a fallback silently fulfils or rejects Commitments on unrelated channels.
