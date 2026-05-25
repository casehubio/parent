---
id: PP-20260525-8c361f
title: "Keep CLAUDE.md under 25 KB — extract triggered content to referenced files"
type: rule
scope: platform
applies_to: "All casehubio repos with a CLAUDE.md"
severity: important
refs:
  - casehubio/parent#66
violation_hint: "`wc -c CLAUDE.md` exceeds 25 000 bytes, or a gotchas/Flyway/build-detail section is inline rather than extracted"
created: 2026-05-25
---

Claude Code checks CLAUDE.md size at session start; files over 40 KB degrade session quality by loading content irrelevant to the current task. Every casehubio repo must keep CLAUDE.md under 25 KB by extracting triggered content — gotchas, Flyway version conventions, and build script detail — to `docs/GOTCHAS.md`, `docs/FLYWAY.md`, and `scripts/README.md` respectively, and replacing each with a one-line trigger in CLAUDE.md (e.g. "Before writing any Java code: read `docs/GOTCHAS.md`"). Content that cannot pass the test "is this needed before the agent knows what task it's doing?" must be extracted. See casehubio/parent#66 for the cross-repo review checklist and casehub-work as the reference implementation.
