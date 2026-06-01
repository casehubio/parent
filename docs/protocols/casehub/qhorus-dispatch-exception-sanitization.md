---
id: PP-20260601-403c5f
title: "Exception messages must never reach MessageService.dispatch() content on error paths"
type: rule
scope: application
applies_to: "Any application-tier ChannelBackend or service that catches exceptions and dispatches DECLINE or FAILURE to a Qhorus channel"
severity: critical
refs:
  - https://github.com/casehubio/qhorus/blob/main/docs/messaging-architecture.md
violation_hint: "Passing e.getMessage() or e.toString() as the content argument to MessageDispatch.builder().content() inside a catch block — leaks API keys, endpoint URLs, stack traces, or internal paths into the tamper-evident ledger"
created: 2026-06-01
---

The Qhorus ledger is tamper-evident and immutable. Any content dispatched via `MessageService.dispatch()` is committed to a Merkle-chained audit record that cannot be retracted. Exception messages frequently contain credentials (API keys, bearer tokens), internal hostnames, stack traces with class paths, or user-identifiable data — none of which should ever appear in the ledger. On error paths, always dispatch a fixed, sanitized string rather than the exception's message or cause. The fixed string should describe the failure category without referencing any runtime detail: `"Reviewer encountered an error."` not `e.getMessage()`. This applies equally to DECLINE and FAILURE message types dispatched from catch blocks.
