# Protocol: Vertical Slice Planning and Documentation

**Applies to:** Any CaseHub application. Also general best practice for any
layered Quarkus application.

---

## The Principle

A **vertical slice** is the thinnest working path through all relevant layers of an
application that produces a testable, demonstrable capability. Build slices end-to-end
before completing any single layer to full production depth.

This applies to development planning, not just tutorial structure. The slice index is
the primary planning and documentation artifact for a layered application — it answers
what the system can DO at each milestone, not merely which modules were integrated.

---

## Planning

**Before starting implementation, identify vertical slices for the application.**

A slice is defined by its user-visible capability — what a caller can do after the
slice is delivered. Each slice touches one or more horizontal layers (foundation modules,
domain components, infrastructure concerns).

**Ordering slices:**

Apply two criteria in order:

1. **Sequential dependencies first.** Some slices can only be built after another is
   complete — the earlier slice provides something the later one requires at runtime
   (a datasource, a CDI bean, a persisted record). These dependencies establish hard
   ordering constraints. Identify them before sequencing.

2. **Minimal layer delta next.** Among slices with no hard dependency ordering, prefer
   the slice that reuses the most of what is already built. A slice that adds one new
   foundation module is preferable to one that adds three, even if both are technically
   unblocked. This keeps each slice small, reviewable, and well-bounded.

**Caveats:**

- Some layers that appear orthogonal have soft ordering: qhorus messaging before
  ledger is not a hard dependency, but qhorus generates the entries that make the
  ledger audit trail meaningful. Document soft orderings as rationale in the slice
  index, not as blocking constraints.
- A layer may participate in multiple slices. Deliver the minimum version needed for
  the first slice that uses it; deepen in later slices that require more from it.
- Not every slice needs to touch every layer. A slice that adds engine routing without
  yet touching the ledger is valid if ledger coverage comes in the next slice.

---

## LAYER-LOG.md Structure

Every CaseHub application maintains a `LAYER-LOG.md` at the project root.
The file has two sections:

### Section 1 — Vertical Slice Index (at the top)

```markdown
## Vertical Slices

| Slice | Capability delivered | Layers | Arch patterns | Status |
|---|---|---|---|---|
| S1 | [user-visible capability, one sentence] | L1, L5 | Hexagonal, Clean | ✅ complete |
| S2 | [next capability] | + L2 | + Event-Driven | ✅ complete |
| S3 | [next capability] | + L3 | + Observer | 🔲 pending |
```

The **Arch patterns** column references the patterns from `docs/ARCHITECTURE.md` that
this slice demonstrates. Use the pattern names as defined there: `Hexagonal`,
`Clean` (dependency rule), `DDD`, `Event-Driven`, `CQRS-lite`, `Strategy`, `Registry`,
`Observer`, `Factory`, `Interceptor`. This makes the slice index a navigational hub:
a reader can enter from the capability and find both the delivery record and the
architectural rationale.

For each slice in progress or complete, add a brief rationale row explaining why it
was sequenced here (sequential dependency or minimal delta), and a reference to the
design docs that informed the approach:

```markdown
**Ordering rationale:**
- S1 before S2: S1 establishes the engine runtime; S2's WorkItem adapter depends on it
- S2 before S3: S2 wires casehub-work; S3 reads WorkItem state from qhorus commitment
- S3 and S4 independent: either could come first; S3 chosen for minimal delta (adds qhorus,
  which is already a runtime dep; S4 would add ledger subclass + Flyway migration)

**Architectural references for this application:**
- `docs/ARCHITECTURE.md` — pattern definitions and invariants (Hexagonal, Clean, DDD, etc.)
- `docs/PLATFORM.md` — capability ownership table; boundary rules
- `docs/protocols/universal/` — universal Quarkus conventions
- `docs/protocols/casehub/` — CaseHub-specific conventions
- `docs/repos/{this-app}.md` in casehub-parent — deep-dive: what this app owns
- `[app-specific analysis doc]` — e.g. gastown-casehub-analysis-v2.md for devtown
```

### Section 2 — Layer Entries

One entry per foundation layer integrated. Each entry opens with a cross-reference to
the slices it participates in and the architectural pattern it implements:

```markdown
## Layer N — [Foundation module]

**Participates in:** S2, S3, S4, S5
**Architectural pattern:** Hexagonal (ports and adapters) — `docs/ARCHITECTURE.md §Foundation`
**Key protocols:** `flyway-migration-rules.md`, `module-tier-structure.md`
**Design refs:** `docs/specs/YYYY-MM-DD-[topic]-design.md`
**Completed:** YYYY-MM-DD
...
[existing LAYER-LOG.md entry format: what was built, accountability gaps closed,
key wiring, gotchas, pattern to replicate]
```

The entry format is unchanged — it captures what was built, accountability gaps closed,
key wiring, gotchas, and pattern to replicate. The slice cross-reference, architectural
pattern, and design refs are additive headers that make the entry navigable from the
slice index and from the architectural docs.

---

## Retrospective Application

When a LAYER-LOG.md exists for an application that was built without slice planning:

1. Identify the vertical slices by reading the existing layer entries, git history, and
   issue list. Map each slice to what the application could DO at that point.
2. Write the Vertical Slice Index as if it had been planned from the start — present
   the intended approach, not the accidental sequence. Git history captures chronology;
   the slice index captures the planning structure.
3. Add the "Participates in" cross-reference to each existing layer entry.
4. The existing entry content does not need to be rewritten.

---

## Relationship to Tutorial Structure

For harness applications (devtown, AML, clinical), the vertical slice index doubles as
the tutorial progression map — each slice is a demonstrable milestone a tutorial reader
can run. The slice index at the top of LAYER-LOG.md is what a developer reads to
understand the application's capability progression; the layer entries below are what
they read to understand how each capability was built.

Spot and technique tutorials (see `tutorial-strategy.md §5`) are extracted from layer
entries — a pattern discovered while implementing a slice becomes a reusable spot
tutorial. They are not the same artifact.

---

**Refs:** casehubio/parent#N (tutorial-strategy.md restructure 2026-05-27)
