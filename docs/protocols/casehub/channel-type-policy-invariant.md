---
id: PP-20260604-a7ad99
title: "allowedTypes and deniedTypes are architectural invariants — only set when a hard constraint must be enforced across all scenarios"
type: rule
scope: platform
applies_to: "Any CaseChannelLayout implementation or any code creating Qhorus channels"
severity: important
refs:
  - claudony#142
created: 2026-06-04
---

`allowedTypes` and `deniedTypes` on Qhorus channels are hard enforcement gates, not documentation labels. Only set them when a hard architectural constraint must be enforced:

- `observe` enforces `allowedTypes = EVENT`: no obligations may ever be created on the telemetry channel.
- `oversight` enforces `deniedTypes = EVENT`: no telemetry may ever appear on the governance channel. EVENT is excluded because it has no commitment effect, is not delivered to agent context, and is excluded from default `pollAfter` results — invisible to governance participants.
- `work` has no constraint (both null): it is the open coordination space.

Channels participating in the full commitment lifecycle must have `allowedTypes = null`. If a new `MessageType` is added to Qhorus with no commitment effect (like `EVENT`), update `deniedTypes` on all governance channels and the `NormativeChannelLayout` comment that anchors this obligation.

`allowedTypes` and `deniedTypes` must not overlap. Overlapping sets are rejected at channel creation time with `IllegalArgumentException`. Denial wins at runtime.
