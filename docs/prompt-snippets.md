# Prompt Snippets — casehubio

Project-specific snippets for casehubio sessions. The general snippet lives at `~/.claude/prompt-snippets.md` — start there for any non-casehubio project.

---

## casehubio — starting an issue or feature

Paste this with every new piece of work:

```
MUST invoke work-start first — do not skip. Then: superpowers:brainstorming before designing. superpowers:test-driven-development before implementing. java-dev for all Java (loads testing-principles + ide-tooling). superpowers:requesting-code-review before committing. implementation-doc-sync after.

[describe the issue or feature here]
```

---

## Notes

- The `session-start` skill is available for blank sessions with no immediate work, but the above prompt is self-contained and sufficient on its own
- Tracked in: casehubio/parent#13
