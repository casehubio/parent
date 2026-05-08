---
id: PP-20260508-29db19
title: "@Scheduled interval must use MicroProfile Config ${property} syntax"
type: rule
scope: platform
applies_to: "All modules with @Scheduled beans"
severity: important
refs: []
violation_hint: "Wrong syntax silently uses the literal string as the interval expression, typically firing at unintended frequency"
created: 2026-05-08
---

# Convention: @Scheduled Interval Must Use MicroProfile Config ${property}s Syntax

**Applies to:** All modules with @Scheduled beans  
**Severity:** Important — wrong syntax silently uses the literal string as the interval expression

## Problem

Using bare `{property}s` (without `$`) in a `@Scheduled` `every` or `delay` attribute does not throw an error — Quarkus treats it as a literal cron expression or duration string and either fails silently or uses a wrong default.

## Rule

Always prefix config property references with `$`: use `${casehub.work.expiry-cleanup.interval}s`, never `{casehub.work.expiry-cleanup.interval}s`.

## Example

```java
// Wrong — silently uses literal string
@Scheduled(every = "{casehub.work.expiry.interval}s")

// Right
@Scheduled(every = "${casehub.work.expiry.interval}s")
```
