---
id: PP-20260602-64fde8
title: "Eval variant pairs must differ on exactly one AgentDisposition axis"
type: rule
scope: repo
applies_to: "casehub-eidos eval module; any AgentProfile variant pair declared in profiles/index.yaml"
severity: important
refs:
  - ../../repos/casehub-eidos.md
violation_hint: "A variant pair where more than one disposition axis differs produces uninterpretable Stage 3 effect sizes — you cannot attribute a high effect size to a specific axis if multiple axes changed simultaneously."
created: 2026-06-02
---

Variant pairs in the eidos eval profile library (`profiles/index.yaml`, `variants:` block) must differ on exactly one `AgentDisposition` field (the declared `primaryAxis`) while holding all other disposition fields — `socialOrient`, `ruleFollowing`, `riskAppetite`, `autonomy`, and the boolean `delegation` — identical between the two profiles. `AgentProfileLoader.load()` enforces this at Stage 0: if the constraint is violated it throws `IllegalStateException` with the pair slugs and differing axis before any LLM call is made. This constraint exists because Stage 3 (`PairContrastJudge`) measures effect size on a single named axis; multi-axis pairs make the result uninterpretable — a high effect size cannot be attributed to the declared axis if other axes also differ.
