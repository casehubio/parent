---
id: PP-20260604-dualid
title: "Qhorus channels have dual identity: immutable UUID (machine) + immutable name (semantic slug)"
type: rule
scope: platform
applies_to: "casehub-qhorus — MCP tools, service layer, any consumer creating or referencing channels"
severity: important
refs:
  - docs/repos/casehub-qhorus.md
  - qhorus#237
  - qhorus#238
violation_hint: "A new MCP tool uses channel_name (name-only) instead of channel (UUID-or-name). Or tool output omits channelId or channelName from ChannelDetail. Or consumer code hard-codes a UUID as the only channel reference."
created: 2026-06-04
---

Every Qhorus channel has two complementary identities that are both immutable after creation:

**UUID** — machine identity. Assigned at creation, never changes, stable for cross-repo and machine-to-machine references. The `ChannelDetail` field is `channelId`.

**Name** — semantic slug. Human-readable, unique within a Qhorus instance, intended for LLM tool callers and operators. The `ChannelDetail` field is `channelName`. Format is constrained by qhorus#236 (enforcement pending); names must not be UUID-shaped (see sharp edge below).

## Rules

**Immutability.** Channel names cannot be changed once created. There is no `rename_channel` tool and none will be added without a Flyway migration strategy that preserves bindings, commitment references, and audit entries.

**Tool parameters.** MCP tools that accept a channel reference must use the parameter name `channel` (not `channel_name`) and delegate to `QhorusMcpToolsBase.resolveChannel()`. This accepts either form and returns the channel UUID. Existing tools using `channel_name` are a known inconsistency, migrated by qhorus#237.

**Tool responses.** All `ChannelDetail` responses include both `channelId` (UUID) and `channelName` (slug). Neither may be omitted.

**Reference preference.** UUID is the preferred reference for machine-to-machine and cross-repo use — it is guaranteed stable and is what ledger entries, commitment records, and binding keys store. Slug is preferred for human operators and LLM tool callers — it is contextual and readable.

## Sharp edge: UUID-shaped names

`resolveChannel()` tries UUID parse first. A channel named with a UUID-shaped string (e.g. `"550e8400-e29b-41d4-a716-446655440000"`) will resolve as UUID lookup, not name lookup. This distinction matters when a channel by that UUID does not exist but a channel by that name does — the call will fail with "channel not found". Channel names must not be UUID-shaped. This constraint is enforced informally today and formally by the slug pattern in qhorus#236.
