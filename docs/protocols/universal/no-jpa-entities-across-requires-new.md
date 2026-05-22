---
id: PP-20260522-056cc2
title: "No JPA entities cross a REQUIRES_NEW boundary — extract primitives before the call"
type: rule
scope: universal
applies_to: "Any Quarkus service calling a @Transactional(REQUIRES_NEW) method from within an outer @Transactional context"
severity: critical
refs: []
violation_hint: "Passing a Channel, Message, or any JPA entity as a parameter to a REQUIRES_NEW method; accessing lazy associations inside REQUIRES_NEW and getting LazyInitializationException"
created: 2026-05-22
---

When a `@Transactional(REQUIRES_NEW)` method is called from within an outer `@Transactional` context, JPA entities from the outer context become detached in the REQUIRES_NEW context. Accessing any lazy association on them throws `LazyInitializationException`. The fix is architectural: callers must extract all needed values as primitives (Long, UUID, String, Instant) or plain records before calling the REQUIRES_NEW method. No JPA entity references cross the boundary. This also improves readability — a signature accepting only value types signals to readers that the method may run in a different transaction context. The garden entry GE-20260522-259812 covers the technique.
