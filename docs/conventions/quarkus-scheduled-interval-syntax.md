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
