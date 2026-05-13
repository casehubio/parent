---
id: PP-20260513-2ce9e1
title: "Verify SPI default method contracts with an anonymous implementation test"
type: rule
scope: platform
applies_to: "All SPI interfaces in devtown-domain/spi/ that use default methods"
severity: important
refs:
  - domain/src/test/java/io/casehub/devtown/domain/spi/CapabilityRegistrySpiTest.java
violation_hint: "Testing only the concrete class (e.g. DevtownCapabilityRegistry) passes whether isKnown() is abstract or default — the SPI contract is not proven"
created: 2026-05-13
---

When a method on an SPI interface is promoted to `default`, verify the contract with a test that uses an anonymous implementation providing only the genuinely abstract methods — deliberately omitting the default method. The compiler error ("does not override abstract method X") is the RED state; it proves the method is still abstract. After the change, the anonymous class compiles and the test passes GREEN. This proves the contract lives on the interface itself, not on any concrete implementation. Testing on the concrete class alone is insufficient — a concrete override satisfies the test whether or not the default exists.
