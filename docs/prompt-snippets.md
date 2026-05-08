# Prompt Snippets — casehubio

Project-specific snippets for casehubio sessions. The general snippet lives at `~/.claude/prompt-snippets.md` — start there for any non-casehubio project.

---

## casehubio — design and implementation sessions

General snippet plus casehubio additions: read PLATFORM.md and confirm an issue exists.

```
Before starting: read ~/claude/casehub/parent/docs/PLATFORM.md and run the
Platform Coherence Protocol. Confirm an open issue exists for this work —
create one if not. Check both IntelliJ MCPs are available and report if either
is missing; do not proceed with semantic operations if they are absent. Before
any rename use ide_refactor_rename not sed/Edit. Before any move use
ide_move_file not mv. Before any find-usages use ide_find_references not grep.
Use superpowers:brainstorming before designing,
superpowers:test-driven-development before implementing,
superpowers:requesting-code-review before committing.
```

---

## Notes

- General snippet (without PLATFORM.md and issue check): `~/.claude/prompt-snippets.md`
- Tracked in: casehubio/parent#13
