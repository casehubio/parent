---
id: PP-20260521-9d4988
title: "Update journal migration references if Flyway versions are renumbered before the journal is committed"
type: rule
scope: platform
applies_to: "All casehub repos — design/JOURNAL.md entries referencing Flyway V numbers"
severity: guidance
refs:
  - docs/protocols/casehub/flyway-version-range-allocation.md
violation_hint: "Journal entry says VN/VM but the branch migration files are at VP/VQ — numbers were renumbered after the journal was written but before it was committed."
created: 2026-05-21
---

When Flyway migrations are renumbered on an epic branch (typically to resolve a concurrent-epic version conflict), any journal entries that reference the old V numbers must be updated before the journal is committed. The journal is committed to git and becomes the permanent record merged into DESIGN.md at epic close — stale V numbers in a committed journal create permanently incorrect documentation that cannot be corrected without re-writing history. Check: after any renumber commit, grep design/JOURNAL.md for the old V numbers and update them to match the new filenames on disk.
