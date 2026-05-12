# Prompt Snippets — casehubio

Project-specific snippets for casehubio sessions. The general snippet lives at `~/.claude/prompt-snippets.md` — start there for any non-casehubio project.

---

## casehubio — session start

Paste once at the start of a new session (handles platform doc, issue check,
IntelliJ MCPs, tool preferences):

```
session start
```

---

## casehubio — starting an issue or feature

Paste this with every new piece of work to enforce the discipline chain.
One line of rules, then describe the work:

```
Read PLATFORM.md and run the Platform Coherence Protocol. Check docs/protocols/ for relevant rules. superpowers:brainstorming before designing. superpowers:test-driven-development before implementing. java-dev for all Java (loads testing-principles + ide-tooling). superpowers:requesting-code-review before committing. implementation-doc-sync after.

[describe the issue or feature here]
```

---

## Notes

- `session-start` skill: handles PLATFORM.md, issue check, IntelliJ MCPs, tool preferences
- Work-item line: enforces the skill chain explicitly for each piece of work
- Tracked in: casehubio/parent#13
