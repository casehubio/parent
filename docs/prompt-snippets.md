# Prompt Snippets — casehubio

Project-specific snippets for casehubio sessions. The general snippet lives at `~/.claude/prompt-snippets.md` — start there for any non-casehubio project.

---

## casehubio — design and implementation sessions

Paste this at the start of every session. One phrase — the `session-start`
skill handles everything.

```
session start
```

The skill reads PLATFORM.md, runs the Platform Coherence Protocol, confirms
an issue exists, verifies both IntelliJ MCPs, establishes IntelliJ tool
preferences, and activates the full skill chain:
brainstorming → TDD → java-dev (+ testing-principles) → code-review → doc-sync.

---

## Notes

- `session-start` skill source: `cc-praxis/session-start/`
- The platform doc path for casehubio is resolved automatically by the skill
- To extend to other projects: add `platform-doc: path/to/PLATFORM.md` to
  that project's CLAUDE.md — the skill will pick it up
- Tracked in: casehubio/parent#13
