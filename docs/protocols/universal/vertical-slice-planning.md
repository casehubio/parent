# Protocol: Slice-Indexed Architecture Log (SIAL)

**Applies to:** Any CaseHub application. Also general best practice for any layered
Quarkus application.

---

## What this is

A **Slice-Indexed Architecture Log (SIAL)** is the primary planning and documentation
artifact for a layered application.

`LAYER-LOG.md` is the SIAL artifact for CaseHub harness applications. It is part of a
three-document design system:

| Document | Role |
|---|---|
| `LAYER-LOG.md` (SIAL) | Slice index + layer entries — planning, delivery, and replication record |
| `DESIGN.md` | Cross-cutting architectural decisions; the *why*; distilled from JOURNAL at epic close |
| `design/JOURNAL.md` | Per-epic working doc; feeds LAYER-LOG and DESIGN.md at epic close |

See `AGENTIC-HARNESS-GUIDE.md §Three-Document Design System` for the full flow.

---

## Slices and layers

**Slices are the planning and delivery unit. Layers are the implementation unit.**

A **vertical slice** is a user-visible capability — what a caller can do after it is
delivered. Each slice requires some set of horizontal layers (foundation modules, domain
components, infrastructure concerns) to implement it.

To deliver a slice: identify which layers it requires, then implement each of those
layers in turn — doing only what the slice needs from each layer — until the slice works
end-to-end. Move to the next slice. Deepen a layer further only when a later slice
requires more from it.

The layer ordering in LAYER-LOG.md is for *reading* — the sequence in which a
developer encounters the layers to understand the system. It is not the build sequence.
Build sequence is governed by the slice plan.

---

## Planning

Before starting implementation, identify the vertical slices for the application and
sequence them.

**Define each slice** by its user-visible capability — one sentence stating what a
caller can do after the slice ships.

**Sequence slices** using two criteria in order:

1. **Sequential dependencies first.** Some slices can only follow another because the
   earlier slice provides something the later one needs at runtime (a datasource, a CDI
   bean, a persisted record). Identify these hard constraints before sequencing.

2. **Minimal layer delta next.** Among unblocked slices, prefer the one that implements
   the fewest new layers. Smaller deltas mean smaller, more reviewable delivery steps.

**Soft ordering** — document but do not block on it. Some layers appear orthogonal but
produce artefacts the next layer consumes (e.g. qhorus messaging produces
`MessageLedgerEntry` records that make ledger audit meaningful). Call this out in
ordering rationale, not as a hard constraint.

---

## LAYER-LOG.md structure

Every CaseHub application maintains a `LAYER-LOG.md` at the project root with two
sections.

### Purpose of each section

**Section 1 — Vertical Slice Index** answers: what can this system DO, and what does it
take to deliver each capability? This serves planning, architectural navigation, and
readers who want to understand the capability arc before going deep.

**Section 2 — Layer entries** answers: how was each layer implemented, what are the
non-obvious decisions, what went wrong, and how do I replicate this in another domain?
An LLM reading a layer entry should be able to reproduce that layer in a different
domain harness without asking questions. This is the primary replication and teaching
record.

Neither section subordinates the other. A reader enters from the capability (slice
index) to find implementation depth, or enters from a layer entry to find architectural
context and slice membership.

### Section 1 — Vertical Slice Index

Place this at the top of LAYER-LOG.md, before any layer entries.

```markdown
## Vertical Slices

| Slice | Capability delivered | Layers | Arch patterns | Status |
|---|---|---|---|---|
| S1 | [user-visible capability, one sentence] | L1, L5 | Hexagonal, Clean | ✅ complete |
| S2 | [next capability] | + L2 | + Event-Driven | ✅ complete |
| S3 | [next capability] | + L3 | + Observer | 🔲 pending |

**Ordering rationale:**
- S1 before S2: [hard dependency or minimal-delta reason]
- S2 before S3: [reason]

**Architectural references:**
- `docs/ARCHITECTURE.md` — pattern definitions (Hexagonal, Clean, DDD, Event-Driven, CQRS-lite, ...)
- `docs/PLATFORM.md` — capability ownership; boundary rules
- `docs/protocols/universal/` and `docs/protocols/casehub/` — conventions
- `docs/repos/{this-app}.md` in casehub-parent — what this app owns
- [app-specific analysis doc, e.g. gastown-casehub-analysis-v2.md]
```

The **Arch patterns** column uses names from `docs/ARCHITECTURE.md`: `Hexagonal`,
`Clean`, `DDD`, `Event-Driven`, `CQRS-lite`, `Strategy`, `Registry`, `Observer`,
`Factory`, `Interceptor`, `Vertical Slices`. `Vertical Slices` applies at the
application tier — use it when a slice demonstrates capability-driven delivery
cutting through horizontal foundation layers.

### Section 2 — Layer entries

One entry per layer implemented. Each entry opens with navigation headers:

```markdown
## Layer N — [Foundation module name]

**Participates in:** S2, S3, S4
**Architectural pattern:** [Pattern name] — `docs/ARCHITECTURE.md §[Section]`
**Key protocols:** [protocol filenames]
**Design refs:** [paths to specs, DESIGN.md sections, analysis docs]
**Completed:** YYYY-MM-DD (or 🔲 pending)
**Issues:** [issue refs]
**Navigation:** `git log --grep="#N" --oneline`

### What it shows
[Teaching narrative — what this layer adds, what gap it closes, contrast with previous]

### Accountability gaps closed
| Gap | What breaks without it | Closed by |
|-----|----------------------|-----------|

### Key wiring
[Non-obvious configuration — not visible in code, not in official docs]

### Gotchas
[What went wrong; what would go wrong without prior knowledge]

### Pattern to replicate
[Domain-agnostic numbered steps an LLM follows to build this layer in a new domain]
```

When a layer entry is started but not yet complete, mark pending sections with 🔲 and
include a pointer to what will fill them (e.g. "🔲 at layer close — blocked on
engine#326").

---

## Retrospective application

When restructuring an existing LAYER-LOG.md that was written without slice planning:

1. Read the existing layer entries, git history, and issue list. Identify the vertical
   slices — what the application could DO at each meaningful milestone.
2. Write the Vertical Slice Index as if it had been planned from the start. Git history
   captures what actually happened; the slice index captures the correct planning
   structure.
3. Add `**Participates in:**` and the other navigation headers to each existing layer
   entry. The entry content does not need to be rewritten.

---

## Relationship to tutorial structure

LAYER-LOG.md is a development and replication record first. For harness applications
(devtown, AML, clinical) it also serves as tutorial source material — but the tutorial
emerges from building correctly, not the other way around.

The slice index doubles as the tutorial progression map. The layer entries are the
primary tutorial material — each "Pattern to replicate" section is what an LLM or
developer follows to reproduce that layer in a new domain.

Spot and technique tutorials (`tutorial-strategy.md §5`) are extracted from layer
entries. They are separate artifacts — not embedded in the layer entry itself.
