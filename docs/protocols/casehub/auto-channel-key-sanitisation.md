---
id: PP-20260605-8013d4
title: "AutoChannelPolicy implementations must sanitise external keys via sanitiseSegment(); connector IDs via slugifyConnectorId()"
type: rule
scope: repo
applies_to: "casehub-qhorus connector-backend — any AutoChannelPolicy implementation that embeds external identifiers into auto-created channel names"
severity: important
refs:
  - docs/specs/2026-06-04-channel-slug-enforcement-design.md
  - docs/protocols/casehub/qhorus-channel-dual-identity.md
violation_hint: "An AutoChannelPolicy returns an AutoChannelSpec with a raw lookupKey (e.g. '+14155552671') directly in channelName. ChannelCreateRequest construction will throw IllegalArgumentException on first contact, silently discarding inbound messages."
created: 2026-06-05
---

The `AutoChannelPolicy` SPI leaves channel naming to the implementor, but all channel names must conform to the slug invariant (PP-20260604-dualid). External user-provided keys (phone numbers, email addresses, arbitrary connector keys) contain characters invalid in slugs (`+`, `@`, `.`, etc.) and must be sanitised before embedding in a channel name. Use `ConfiguredAutoChannelPolicy.sanitiseSegment(rawKey)` — it lowercases, replaces non-alphanumeric runs with `-`, prepends `id-` if the result starts with a digit, and appends an 8-hex-char SHA-256 hash of the lowercased input to guarantee uniqueness even when two distinct raw keys normalise to the same prefix. Developer-defined connector IDs are expected to be valid slugs already; use `slugifyConnectorId(connectorId)` for defensive normalisation without a hash (two non-conformant IDs that slugify identically are indistinguishable — make them unique at source). If a custom policy produces a non-conformant name, `ChannelCreateRequest`'s compact constructor will throw at first-contact time rather than at startup.
