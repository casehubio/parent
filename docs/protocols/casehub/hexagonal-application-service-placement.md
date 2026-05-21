---
id: PP-20260512-9b8847
title: "Application-tier repos: use-case orchestration lives in app/, api/ stays pure domain"
type: principle
scope: application
applies_to: "Application-tier repos (aml, clinical, devtown) — the api/ and app/ module split"
severity: important
refs:
  - docs/PLATFORM.md
violation_hint: "api/ module depending on casehub-work-api, casehub-ledger-api, or any other foundation library; or a top-level orchestration interface in api/ that returns foundation types"
created: 2026-05-12
---

In hexagonal architecture the domain module (api/) is the innermost layer and carries
zero dependencies on external frameworks or foundation libraries. Use-case orchestration
— composing specialist domain services with foundation services such as WorkItemService,
LedgerEntryService, or QhorusChannel — belongs in the application layer (app/).
Define the orchestration as a CDI @ApplicationScoped bean in app/; use @DefaultBean on
the naive/fallback implementation so a richer implementation displaces it without
configuration switches. Result types that cross the domain/application boundary are pure
Java records in api/ and carry only primitive identifiers (String, UUID), never foundation
entity or SPI types.
