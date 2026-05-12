# Prompt Snippets — casehubio

Project-specific snippets for casehubio sessions. The general snippet lives at `~/.claude/prompt-snippets.md` — start there for any non-casehubio project.

---

## casehubio — starting an issue or feature

Paste this with every new piece of work:

```
Read PLATFORM.md and run the Platform Coherence Protocol. Check docs/protocols/ for relevant rules. Confirm an open issue exists — create one if not. For any rename use ide_refactor_rename, move use ide_move_file, find-usages use ide_find_references — if IntelliJ is unavailable stop and tell me, never fall back to bash. superpowers:brainstorming before designing. superpowers:test-driven-development before implementing. java-dev for all Java (loads testing-principles + ide-tooling). superpowers:requesting-code-review before committing. implementation-doc-sync after.

[describe the issue or feature here]
```

---

## Notes

- The `session-start` skill is available for blank sessions with no immediate work, but the above prompt is self-contained and sufficient on its own
- Tracked in: casehubio/parent#13
