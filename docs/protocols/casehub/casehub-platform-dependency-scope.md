---
id: PP-20260524-a8f597
title: "Use test scope for casehub-platform in library/extension modules; runtime scope in app modules"
type: rule
scope: platform
applies_to: "Any module declaring a dependency on io.casehub:casehub-platform"
severity: critical
refs:
  - ../../repos/casehub-work.md
  - ../../PLATFORM.md
violation_hint: "All @QuarkusTest tests pass, then the build fails ~20s later with UnsatisfiedResolutionException for PreferenceProvider during Quarkus augmentation"
created: 2026-05-24
---

Library and Quarkus extension modules (no `<goal>build</goal>` in quarkus-maven-plugin) must declare `casehub-platform` as `<scope>test</scope>` — production augmentation never runs for these modules, so test-scoped activation is sufficient and correct. Application modules that declare `<goal>build</goal>` must use `<scope>runtime</scope>` — the Quarkus production build validates CDI without the test classpath, making `MockPreferenceProvider @DefaultBean` invisible at augmentation time if scoped as test. The `casehub-platform` module must also be Jandex-indexed (`io.smallrye:jandex-maven-plugin:3.3.1`) so its beans are discoverable when consumed as a JAR.
