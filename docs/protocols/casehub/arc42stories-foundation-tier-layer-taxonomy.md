---
id: PP-20260604-1ff5b9
title: "Foundation-tier ARC42STORIES.MD defines its own layer taxonomy — do not apply the CaseHub Profile harness layer sequence"
type: rule
scope: platform
applies_to: "Any CaseHub foundation-tier module (casehub-ledger, casehub-work, casehub-qhorus, casehub-connectors, casehub-eidos) writing ARC42STORIES.MD"
severity: important
refs:
  - ../arc42stories-casehub-profile.md
  - ../arc42stories-spec.md
violation_hint: "Foundation module ARC42STORIES.MD §4/§5 uses the harness layer sequence (casehub-work=L2, casehub-qhorus=L3, casehub-ledger=L4, etc.) rather than a module-specific internal layer taxonomy"
created: 2026-06-04
---

Foundation modules must NOT use the CaseHub Profile's application-tier layer taxonomy (the integration sequence that harness apps follow: domain baseline → casehub-work → casehub-qhorus → casehub-ledger → etc.). That taxonomy describes how a harness app integrates layers of foundation modules. A foundation module's own ARC42STORIES.MD defines its internal architectural layers — the horizontal concerns specific to that module's own design (e.g. casehub-work uses L1 Domain Baseline / L2 REST API / L3 Lifecycle Engine / L4 Label System / L5 Ledger Integration / L6 Distribution / L7 Optional Modules). Use the base `arc42stories-spec.md` directly for foundation-tier documents; the CaseHub Profile's `### Foundation tier` preamble template applies, but its layer taxonomy table under `### Application tier only` does not.
