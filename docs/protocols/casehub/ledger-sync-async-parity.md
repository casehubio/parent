---
id: PP-20260517-15bf75
title: "New ledger service methods must ship both blocking and reactive variants"
type: principle
scope: platform
applies_to: "LedgerVerificationService, LedgerEntryRepository, KeyRotationService, and any future ledger service SPI"
severity: important
refs:
  - docs/repos/casehub-ledger.md
violation_hint: "A new method added to a ledger service with no Uni<T> counterpart, or a new reactive method with no blocking counterpart"
created: 2026-05-17
---

casehub-ledger deliberately supports two API stacks — blocking (`LedgerEntryRepository`) and reactive (`ReactiveLedgerEntryRepository`). Any new capability added to only one stack creates an inconsistency that downstream consumers discover at integration time, not design time. When adding a method to any ledger service or SPI, provide both a blocking variant and a `Uni<T>` reactive variant unless one stack is demonstrably unsuitable (e.g. pure in-memory computation with no I/O has no async benefit; a true streaming operation may have no blocking equivalent). Discovered during #83 when `verifyAgentSignature()` was found to have no reactive counterpart.
