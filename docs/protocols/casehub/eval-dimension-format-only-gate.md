---
id: PP-20260602-3ecfdb
title: "EvalDimension.applicableFor() is gated by format only — never by profile availability"
type: rule
scope: repo
applies_to: "casehub-eidos eval module; any code that adds a new EvalDimension or quality signal to the eval harness"
severity: important
refs:
  - ../../repos/casehub-eidos.md
violation_hint: "A new EvalDimension whose applicability depends on whether a source profile exists, or requires a second parameter beyond RenderFormat, violates this rule. Such a signal must instead be a separate @ApplicationScoped judge class with its own result type."
created: 2026-06-02
---

`EvalDimension.applicableFor(RenderFormat format)` determines which dimensions apply to an eval case based solely on the render format. This invariant must not be broken by adding a second parameter (e.g. `boolean hasSourceProfile`) or by adding a new dimension whose applicability depends on anything other than format. Any quality signal that depends on profile availability — semantic proximity to original prose, vocabulary expressiveness, trait expression, pairwise contrast — must be implemented as a separate `@ApplicationScoped` judge with its own result and report types. The invariant exists to keep `EvalResult.overall` scores comparable across synthetic and profile-backed cases: if profile cases carried an extra dimension, their `overall` denominator would differ from synthetic cases and cross-dataset comparisons would be meaningless.
