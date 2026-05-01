# Convention: Qhorus EVENT Message Content Is Always Null

**Applies to:** All projects that read or display Qhorus `MessageLedgerEntry` records
**Severity:** Important — content renders as blank with no error; symptom misleads about cause

## The Problem

`LedgerWriteService` extracts telemetry fields from EVENT messages into dedicated columns
(`toolName`, `durationMs`, `tokenCount`, `contextRefs`, `sourceEntity`) and sets the
`content` field to null. Any code that reads `entry.content` for an EVENT entry gets null —
no exception, no warning, just silence.

This surfaces in feed renderers, dashboards, and any UI that displays message content
directly: the EVENT appears with no content, which looks like a missing message or a
rendering bug. It is neither — the data is in the telemetry fields.

## The Rule

**Never render `content` for EVENT entries.** For EVENT messages, display:
- `toolName` — the tool that was called
- `durationMs` — wall-clock duration
- `tokenCount` — tokens consumed
- `contextRefs` / `sourceEntity` — if present

For all other message types (QUERY, COMMAND, RESPONSE, STATUS, DONE, FAILURE, DECLINE,
HANDOFF), `content` is stored verbatim and safe to render directly.

```java
// Wrong — content is null for EVENT; renders as blank
String display = entry.content;

// Correct — branch on message type
String display = "EVENT".equals(entry.messageType)
    ? formatTelemetry(entry.toolName, entry.durationMs, entry.tokenCount)
    : entry.content;
```

## Where This Applies

Any Claudony feed renderer, dashboard panel, or test assertion that reads
`MessageLedgerEntry.content`. Also applies to any direct JPQL or repository query
that selects `content` from ledger entries without filtering by message type.
