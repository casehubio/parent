---
id: PP-20260514-layer-log
title: Maintain LAYER-LOG.md as definition of done per harness layer
type: convention
scope: universal
applies_to: All CaseHub agentic harnesses (casehub-aml, casehub-clinical, casehub-devtown, QuarkMind)
severity: required
refs:
  - docs/tutorial-strategy.md §2.1b
  - docs/repos/casehub-aml.md
created: 2026-05-14
---

## Rule

Every CaseHub agentic harness must maintain a `LAYER-LOG.md` at the project root. A layer is not complete until its log entry is written.

## Purpose

`LAYER-LOG.md` is the raw material for tutorials, how-tos, and LLM-consumable building guides. It captures what was built at each layer in a structured, reusable form — more explicit than narrative blog entries, more durable than session notes.

An LLM reading `LAYER-LOG.md` alongside the code and git history has everything it needs to:
- Build the equivalent layer in a different domain harness
- Generate human-readable tutorials in any format
- Answer "how do I wire X in a CaseHub app?" without asking questions

## Format

Each layer entry must contain all five sections. Omitting a section is a violation — leave it empty rather than skip it, so the gap is visible.

```markdown
## Layer N — [What it adds]

**Completed:** YYYY-MM-DD
**Issue:** owner/repo#N
**Key files:**
- `path/to/file.java` — one-line description of what it does
- `path/to/other.java` — one-line description

### What it shows

One paragraph: what capability this layer adds and what compliance or coordination gap it closes. Written for an LLM that has no prior context.

### The gap comments

Paste the `// LAYER N GAP: ...` comments from the naive layer that this layer addresses. These are the explicit teaching mechanism.

```java
// LAYER N GAP: no deadline tracking — compliance officer review can sit indefinitely
```

### Key wiring

The non-obvious configuration and wiring that is not derivable from the code alone. Anything that required trial and error, reading source code of a dependency, or a workaround.

```java
// Example: the wiring pattern that surprised us
```

- Any configuration properties that must be set
- Any scan packages, Hibernate mappings, or CDI qualifiers that are easy to miss

### Gotchas

- Bullet list of things that went wrong or would go wrong without prior knowledge
- Link to forage garden entries (GE-XXXXXXXX-XXXXXX) where relevant

### Pattern to replicate (in another domain)

Numbered steps an LLM would follow to implement this layer in a different domain harness. Domain-agnostic — replace AML-specific names with the equivalent concept.

1. Add `[dependency]` to `[module]` — reason
2. Configure `[property]` — what it does and why it's needed
3. Implement `[interface]` — what it must do
4. Wire `[component]` to `[component]` — how
5. Test with: `[what to verify]`
```

## Violation hint

A layer whose code is merged but has no `LAYER-LOG.md` entry is incomplete. The log entry is as much a deliverable as the code. Block the next layer until the current layer's entry exists.

## Retroactive entries

When adopting this protocol mid-project, write retroactive entries for all completed layers before starting the next one. Use git history, specs, blog entries, and forage garden to reconstruct the content. Incomplete recollection is acceptable — leave sections partially filled rather than skipping them.
