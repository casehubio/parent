---
id: PP-20260519-39a9a5
title: "Reactive-tier service beans in casehub extensions are separate beans, build-time gated, with direct reactive SPI injection"
type: rule
scope: platform
applies_to: "Any casehub extension or module that exposes service beans with reactive variants (e.g. casehub-ledger, casehub-qhorus)"
severity: important
refs:
  - docs/protocols/universal/reactive-blocking-tier-separation.md
violation_hint: "A single @ApplicationScoped bean mixes blocking and reactive methods, or a reactive bean uses Instance<T> guards instead of build-time gating, or a reactive bean is not suffixed Reactive*Service"
created: 2026-05-19
---

Implements PP-20260519-f2e160 (reactive-blocking-tier-separation) for the Quarkus/casehub
platform. Every service capability ships in two separate @ApplicationScoped beans: a
blocking-tier bean (no reactive imports, no Instance<T> wrappers) and a reactive-tier bean
(Reactive*Service suffix, direct @Inject of reactive SPIs, all methods return Uni<T>).
Reactive-tier beans are annotated @IfBuildProperty(name = "casehub.<module>.reactive.enabled",
stringValue = "true") so they are absent from the CDI graph in JDBC-only consumers —
preventing build-time augmentation failures without Instance<T> or NoOp fallbacks.
Consuming deployments that need reactive set the property in application.properties at
build time. Test suites that exercise reactive paths set it in test application.properties
alongside @DefaultBean blocking shims that satisfy reactive SPI injection points.
Adding a method to the blocking tier requires adding the Uni<T> equivalent to the reactive
tier, and vice versa — parity is structural, not co-located.
