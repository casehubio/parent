---
id: PP-20260523-e7b577
title: "casehub-ledger signing and verification code must be algorithm-transparent"
type: rule
scope: repo
applies_to: "io.casehub.ledger.runtime.service — any class that signs, verifies, or loads cryptographic keys"
severity: important
refs:
  - https://github.com/casehubio/ledger/blob/main/adr/0013-post-quantum-signing-migration.md
violation_hint: "Hardcoded string 'Ed25519' (or any algorithm name) in Signature.getInstance(), KeyFactory.getInstance(), or similar JCA calls"
created: 2026-05-23
---

No signing, verification, or key-loading code in casehub-ledger may hardcode a cryptographic
algorithm string. Signing derives the algorithm from the private key's `getAlgorithm()` method.
Verification detects the algorithm from stored X.509/PKCS8 key bytes via trial-load through the
supported-algorithm list in `AgentCryptographicVerifier`. New algorithms are added to that list as
JVM or BouncyCastle support ships — no other code changes required. This rule enables the
post-quantum migration path described in ADR 0013 without schema changes or SPI breaks.
