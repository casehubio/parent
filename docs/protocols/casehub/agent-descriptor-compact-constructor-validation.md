---
id: PP-20260530-2d6dbd
title: "AgentDescriptor required-field validation belongs in the compact constructor"
type: rule
scope: repo
applies_to: "AgentDescriptor record in casehub-eidos-api; any future descriptor-style record in casehub-eidos-api"
severity: important
refs:
  - ../../repos/casehub-eidos.md
violation_hint: "Validation moved to AgentRegistry.register() or other service boundaries — allows invalid AgentDescriptors (null agentId, blank slot, etc.) to be constructed in tests or intermediate contexts, removing the guarantee that every descriptor in the system is valid."
created: 2026-05-30
---

`AgentDescriptor` validates its four implicitly-required fields (`agentId`, `name`, `slot`, `tenancyId`) in the compact constructor via `AgentDescriptorValidator.validate()`. This guarantees that no invalid descriptor can exist anywhere in the system — not in tests, not in intermediate state, not in any registry implementation. Registry implementations (`JpaAgentRegistry`, `InMemoryAgentRegistry`) need no validation code: every descriptor reaching them is already guaranteed valid. Validation at service boundaries instead of type construction leaves a window where invalid descriptors can be constructed, passed around, and only fail at registration — misleading error location and allowing invalid state in tests. The compact constructor is the correct enforcement point. Tests that previously created descriptors with null required fields for convenience must use valid values or be deleted (the behavior is now covered by `AgentDescriptorValidatorTest`).
