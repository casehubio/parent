# Prompt Snippets

Ready-to-paste prompts for Claude sessions. Revisit and refine as the configuration system evolves.

---

## casehubio — design and implementation sessions

Paste this at the start of any session that involves designing or building something in a casehubio repo.

```
Before starting: read ~/claude/casehub/parent/docs/PLATFORM.md and run the
Platform Coherence Protocol. Confirm an open issue exists for this work —
create one if not. Check both IntelliJ MCPs are available and report if either
is missing; do not proceed with semantic operations (rename, move,
find-references) if they are absent. Before any rename use ide_refactor_rename
not sed/Edit. Before any move use ide_move_file not mv. Before any
find-usages use ide_find_references not grep. Use superpowers:brainstorming
before designing, superpowers:test-driven-development before implementing,
superpowers:requesting-code-review before committing.
```

---

## Notes

- The PLATFORM.md reference is casehubio-specific — omit for non-casehubio sessions
- The IntelliJ operation mappings (rename/move/find-usages) are the recognition step that skills alone cannot provide — they must stay in the prompt
- Tracked in: casehubio/parent#13
