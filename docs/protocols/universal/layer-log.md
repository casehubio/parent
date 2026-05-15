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

Every CaseHub agentic harness must maintain a `LAYER-LOG.md` at the project root.

**Two obligations, two triggers:**
- **Start the entry** — when any work on the layer begins
- **Fill the entry** — when the layer's code ships

Do not conflate these. Starting immediately means wiring decisions and gotchas are captured while the context exists. Filling at ship means the entry is complete before the layer is declared done. An entry that is started but not yet filled is correct; an entry that was never started is a violation.

Entries are written incrementally across sessions. Mark pending sections with `🔲` — see Placeholder guidance below.

**Epics and layers are different organizational schemes.** Epics organize work for build convenience. Layers organize knowledge for teaching. A single tutorial layer may span multiple epics. Do not wait for all epics covering a layer to close before starting its log entry.

**Do not write skeleton entries for layers that have not started.** The layer table in the repo deep-dive already tracks pending/in-progress/complete — that is sufficient for distant layers. The log entry adds value when there is implementation knowledge to capture. Empty skeletons create drift risk without adding anything the layer table does not already provide.

## Purpose

`LAYER-LOG.md` is the raw material for tutorials, how-tos, and LLM-consumable building guides. It captures what was built at each layer in a structured, reusable form — more explicit than narrative blog entries, more durable than session notes.

An LLM reading `LAYER-LOG.md` alongside the code and git history has everything it needs to:
- Build the equivalent layer in a different domain harness
- Generate human-readable tutorials in any format
- Answer "how do I wire X in a CaseHub app?" without asking questions

## Format

Each layer entry must contain all five sections. Sections that cannot yet be filled are marked `🔲` — include the expected content or a pointer to where it will come from. A `🔲` with context is far more useful to a future session than a blank section or a skipped one.

```markdown
## Layer N — [What it adds]

**Completed:** YYYY-MM-DD (or: 🔲 in progress — Epic M done YYYY-MM-DD, naive service pending)
**Issue:** owner/repo#N (list all contributing epics/issues)
**Key files:**
- `path/to/file.java` — one-line description of what it does
- 🔲 `path/to/future.java` — not yet built; see §What it shows

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

A layer whose code is merged but has no `LAYER-LOG.md` entry at all is a violation. An entry with `🔲` placeholders is not — placeholders are expected and useful. The distinction: missing entry means the knowledge is lost; placeholder entry means a future session knows exactly what to fill in.

## Placeholder guidance

A `🔲` placeholder **must** include a cross-reference to where the answer will come from, or the expected content if known. A bare `🔲` with no context is nearly useless — it tells the next session that something is missing but not what, where to find it, or what to expect.

Required in every placeholder: why it's pending AND either the expected content or the pointer to where it will come from.

```markdown
### Key wiring
🔲 To fill in when built. Expected: same Hibernate scan packages issue as AML Layer 2
   (`io.casehub.work.runtime.model,io.casehub.work.runtime.filter`).
   See ../aml/LAYER-LOG.md §Key wiring.
```

Not acceptable:

```markdown
### Key wiring
🔲 To fill in when built.
```

## Reference implementations

- **casehub-aml `LAYER-LOG.md`** — Layers 1 and 2 complete. Reference for fully-filled entries.
- **casehub-devtown `LAYER-LOG.md`** — Layer 1 in progress. Reference for in-progress entries with `🔲` placeholders.

Read both before writing your own.

## Retroactive entries

When adopting this protocol mid-project, write entries for all layers that have any work done — completed and in-progress — before starting the next one. Use git history, specs, blog entries, and forage garden to reconstruct the content. In-progress layers get entries with `🔲` sections. Layers with no work done are left out — the layer table already tracks them as pending.

**Note on the epics vs layers confusion:** if epics are closed but the tutorial layer table shows all layers as "pending", the layer table is wrong — not the epics. Epics do not map 1:1 to layers. Update the layer table to reflect actual status (pending / in progress / complete) and write the layer entry for what has been built so far.
