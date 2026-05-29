---
id: PP-20260529-ab32a9
title: "Sanitize caller-controlled HTTP headers before including them in logs"
type: rule
scope: universal
applies_to: "Any Quarkus service that logs HTTP request context — especially security event logs"
severity: important
refs:
  - ../casehub/auth-retrofit-readiness.md
violation_hint: "LOG.warning(\"... sourceIp=\" + request.header(\"x-forwarded-for\"))  — raw header value injected directly into a log line without validation"
created: 2026-05-29
---

Headers such as `X-Forwarded-For`, `X-Real-IP`, and `X-Client-ID` are set by the HTTP caller and must not be trusted or reflected verbatim into logs. A malicious caller can forge these headers to produce log-injection entries (embedding newlines that create fake log lines), mislead incident triage (claiming a blocked request came from a legitimate internal IP), or inject control characters. Before logging any caller-supplied header: (1) validate the value against a strict allowlist pattern (e.g. `[\\w.,: \\[\\]/-]{1,200}` for IP addresses/lists), (2) reject or substitute `"unknown"` if validation fails, (3) for comma-separated forwarded headers, take only the first segment. This rule applies with heightened priority to `SECURITY:`-prefixed log lines, where forged values are most harmful to incident response.
