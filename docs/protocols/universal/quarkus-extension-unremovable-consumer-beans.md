---
id: PP-20260531-2c9f00
title: "Quarkus extension CDI beans with no internal injection point must be annotated @Unremovable"
type: rule
scope: universal
applies_to: "Any Quarkus extension publishing a CDI bean (service, bridge, adapter) that consumers inject but the extension itself never injects internally"
severity: important
refs:
  - https://quarkus.io/guides/cdi-reference#remove-unused-beans
violation_hint: "Extension ships with a @DefaultBean service; consumer app gets UnsatisfiedResolutionException at augmentation time even though the extension appears on the classpath. ARC removed the bean silently during extension build because no injection point was visible."
created: 2026-05-31
---

When a Quarkus extension publishes a CDI bean that no code within the extension itself injects, ARC's dead-code elimination removes it at build time — it sees no injection point and concludes the bean is unreachable. Consumers who inject the bean at their own build time get `UnsatisfiedResolutionException` because the bean no longer exists in the CDI graph. The fix is `@Unremovable` on the bean class: this annotation instructs ARC to retain the bean regardless of whether it detects an injection point. Apply it to any extension-published bean that is designed for consumer injection but has no self-use within the extension (e.g. reactive bridges, utility services, SPI adapters).
