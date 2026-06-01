---
id: PP-20260529-d4bec0
title: "Use @ConfigProperty for static deploy-time credentials; use Preferences for runtime multi-tenant configuration"
type: rule
scope: platform
applies_to: "Any casehub module that requires external service credentials (IMAP, SMTP, API tokens, webhook secrets)"
severity: important
refs:
  - ../../repos/casehub-connectors.md
  - ../../PLATFORM.md
violation_hint: "A connector that injects Preferences/PreferenceKey to resolve IMAP host, SMTP password, or webhook secret — these are deploy-time constants, not runtime-mutable per-tenant values"
created: 2026-05-29
---

Static deploy-time credentials (IMAP host/port/username/password, SMTP settings, API tokens, webhook secrets) must be read via `@ConfigProperty` from MicroProfile Config — not via `casehub-platform-api` `Preferences`/`PreferenceKey`. `Preferences` is designed for runtime-mutable, path-scoped, potentially DB-backed configuration that varies by tenant or scope at runtime; injecting it for static credentials adds a `casehub-platform-api` dependency, requires a `PreferenceProvider` CDI bean at runtime, and misrepresents the configuration's mutability. `@ConfigProperty` is the correct mechanism for values that are set at deploy time and do not change per-tenant. The `EmailInboundAccountProvider` SPI provides the correct extension point for multi-account or runtime-configurable credential sources — the `@DefaultBean` default uses `@ConfigProperty`, and callers override with a custom provider backed by whatever source they need.
