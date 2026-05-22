---
id: PP-20260522-3dca14
title: "Speech-act type validation is owned by MessageDispatch.Builder — enforce at build() time, not downstream"
type: rule
scope: repo
applies_to: "casehub-qhorus — any code dispatching messages via MessageService.dispatch()"
severity: important
refs:
  - docs/specs/2026-05-22-message-dispatch-builder-design.md
violation_hint: "Calling dispatch() without inReplyTo on DONE/DECLINE/FAILURE/RESPONSE/HANDOFF, or without correlationId on DONE/DECLINE/FAILURE/HANDOFF, or without target on HANDOFF"
created: 2026-05-22
---

`MessageDispatch.Builder.build()` is the single enforcement point for speech-act protocol invariants. The validation matrix is: DONE, DECLINE, FAILURE require both `inReplyTo` AND `correlationId`; RESPONSE requires `inReplyTo`; HANDOFF requires `inReplyTo`, `correlationId`, AND `target`; STATUS, COMMAND, QUERY, EVENT have no required reply fields. Violations throw `IllegalArgumentException` at `build()` invocation — never silently accept a malformed dispatch. Do not add try/catch to suppress builder exceptions; fix the protocol setup instead. Tests that previously sent DONE without `inReplyTo` were latent violations — the builder exposed them correctly.
