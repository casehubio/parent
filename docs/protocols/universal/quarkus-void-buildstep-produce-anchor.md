---
id: PP-20260521-636c9c
title: "Void @BuildStep must be anchored with @Produce(ArtifactResultBuildItem.class)"
type: rule
scope: universal
applies_to: "Any Quarkus extension @BuildStep method that returns void and has no BuildProducer parameters"
severity: important
refs: []
violation_hint: "A void @BuildStep with no producer dependencies is a graph orphan — Quarkus may elide it silently. The step appears to compile and deploy but never executes. ArtifactResultBuildItem is in io.quarkus.deployment.pkg.builditem, not io.quarkus.deployment.builditem."
garden_ref: "GE-20260521-977e3e"
created: 2026-05-21
---

A `@BuildStep` method that returns `void` and takes no `BuildProducer<?>` parameters has no outgoing edges in the Quarkus build graph and may be silently elided by the build framework. To guarantee execution, annotate the method with `@Produce(ArtifactResultBuildItem.class)` from `io.quarkus.deployment.annotations`. This declares the step as a contributor to artifact building — a phase Quarkus always runs — ensuring the step executes regardless of downstream consumers. The `@Produce` annotation is declarative only; the method does not need to return or produce the `ArtifactResultBuildItem` instance. Import `ArtifactResultBuildItem` from `io.quarkus.deployment.pkg.builditem` (not `io.quarkus.deployment.builditem` — the latter does not exist).
