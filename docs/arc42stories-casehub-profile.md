# Arc42Stories — CaseHub Profile

**Spec:** [Arc42Stories v0.1](arc42stories-spec.md)  
**Applies to:** All components in the CaseHub ecosystem — application-tier harness apps and foundation-tier modules.

This profile instantiates [Arc42Stories](arc42stories-spec.md) for the CaseHub ecosystem. It defines default values for artifact schema, crosscutting conventions, and platform references that all CaseHub components inherit. Component-type-specific guidance is marked per section.

---

## Preamble Templates

Copy the appropriate preamble for your component type. Add only what is project-specific.

### Application tier (harness apps — devtown, aml, clinical, life, drafthouse)

```markdown
# [App name] — ARC42STORIES.MD

**Spec:** Arc42Stories v0.1
**Profile:** CaseHub — Application tier
**Profile ref:** `../parent/docs/arc42stories-casehub-profile.md` · fallback: `https://raw.githubusercontent.com/casehubio/parent/main/docs/arc42stories-casehub-profile.md`
**Prefix:** [DT / AML / CLI / LIF / DH / QM]
```

### Foundation tier (platform modules — connectors, qhorus, ledger, work, engine, platform, eidos)

```markdown
# [Module name] — ARC42STORIES.MD

**Spec:** Arc42Stories v0.1
**Profile:** CaseHub — Foundation tier
**Profile ref:** `../parent/docs/arc42stories-casehub-profile.md` · fallback: `https://raw.githubusercontent.com/casehubio/parent/main/docs/arc42stories-casehub-profile.md`
**Build position:** [e.g. "Foundation — no casehubio dependencies" or "After casehub-ledger; before casehub-engine"]
**Consumed by:** [repos that depend on this module]
**Depends on:** [casehubio deps, or "none"]
```

### Extension tier

Deferred — no extension-tier components exist yet. A preamble template will be defined when the first extension component is built.

---

## Default Artifact Schema

*Applies to: both tiers.*

All CaseHub components inherit this schema. Declare only the **Prefix** in the preamble — the rest is inherited.

| Artifact type | Format | Example | Where it lives |
|---|---|---|---|
| Improvement log entry | `[PREFIX]-NNN` | `DT-042` | `docs/PROGRESS.md` |
| Issue | `#NNN` or `casehubio/[repo]#NNN` | `#52`, `casehubio/devtown#52` | GitHub Issues |
| Garden entry | `GE-YYYYMMDD-XXXXXX` | `GE-20260521-e39ad1` | `~/.hortora/garden/` |
| Protocol | `PP-YYYYMMDD-XXXXXX` | `PP-20260522-f08b62` | `casehub/garden: docs/protocols/` |
| ADR | `ADR-NNNN` | `ADR-0007` | `docs/adr/` |
| Blog entry | `YYYY-MM-DD-[initials]NN-title` | `2026-05-19-mdp01-layer-5-lands` | workspace `blog/` |
| Design spec | `YYYY-MM-DD-topic-design` | `2026-05-15-epic3-design` | `docs/specs/` |

**Prefix by app (Application tier):**

| App | PREFIX |
|---|---|
| casehub-devtown | `DT` |
| casehub-aml | `AML` |
| casehub-clinical | `CLI` |
| casehub-life | `LIF` |
| casehub-drafthouse | `DH` |
| QuarkMind | `QM` |

Foundation-tier modules do not use an improvement log prefix — use issue refs directly.

---

## Default Layer Taxonomy

### Application tier only

Replace the generic Arc42Stories layer model with the CaseHub harness integration sequence:

| Layer | Foundation module | What it adds |
|---|---|---|
| Domain baseline | *(none — pure Java)* | Domain vocabulary, port interfaces, `@DefaultBean` baseline service |
| casehub-work | `casehub-work` | Human task lifecycle — WorkItem, SLA, escalation, breach policy |
| casehub-qhorus | `casehub-qhorus` | Agent communication mesh — COMMAND/DONE/DECLINE, commitment lifecycle |
| casehub-ledger | `casehub-ledger` | Tamper-evident audit — Merkle chain, trust scoring, GDPR |
| casehub-engine | `casehub-engine` | Adaptive orchestration — CasePlanModel, content-driven routing, WAITING state |
| Trust routing | `casehub-ledger` (trust APIs) | Trust-weighted agent selection from outcome attestations |

This is the natural integration sequence. Justification for a different order belongs in §4 Solution Strategy.

### Foundation tier

Foundation modules define their own layer taxonomy in §4/§5. Layers represent internal architectural concerns — SPI tiers, transport implementations, optional bridge modules, etc. There is no prescribed taxonomy. A module with a single coherent architecture may have one layer.

---

## Default Conventions (§8 Crosscutting Concepts)

*Applies to: both tiers.*

Reference these protocols in §8 rather than duplicating their content:

| Concern | Protocol |
|---|---|
| Module structure | `casehub/garden: docs/protocols/universal/module-tier-structure.md` |
| Flyway migrations | `casehub/garden: docs/protocols/casehub/flyway-version-range-allocation.md` |
| Named datasources | `docs/PLATFORM.md` §Persistence |
| CDI displacement (`@DefaultBean`) | `casehub/garden: docs/protocols/casehub/alternative-extension-patterns.md` |
| SPI placement | `docs/PLATFORM.md` §Step 4 |
| Architectural patterns | `docs/ARCHITECTURE.md` |
| Capability ownership | `docs/PLATFORM.md` Capability Ownership table |

**Anti-patterns must be present inline in §8** — do not merely reference AGENTIC-HARNESS-GUIDE.md. A reader with only ARC42STORIES.MD in context will not follow the reference. Include the 2–3 most dangerous failure modes for this specific component in Symptom → Cause → Fix format.

---

## Default Platform References (§3 Context and Scope)

*Applies to: both tiers — with different content.*

### Application tier

Every harness app's §3 should reference:

- `docs/PLATFORM.md` — capability ownership table and boundary rules
- `docs/repos/{this-app}.md` — what this application owns
- Comparison baseline if one exists (e.g. `docs/gastown-casehub-analysis-v2.md` for devtown)

### Foundation tier

A foundation module's §3 Context and Scope should:

- Include a C4 System Context diagram showing consumers and dependencies
- Reference `docs/PLATFORM.md` Cross-Repo Dependency Map for the authoritative consumer list
- Reference `docs/repos/{this-module}.md` for the platform deep-dive

The preamble's **Build position**, **Consumed by**, and **Depends on** fields give a compact machine-readable summary; §3 provides the full context with diagrams.

---

## Production-First Constraint

*Applies to: both tiers.*

Before writing any class, apply the production-first test:

> "Would this class exist in a production system built to this layer and no further?"

If no — do not build it. Document the architecture in the Arc42Stories document instead. The most common violations and their fixes are in ARC42STORIES.MD §8 Anti-patterns (must be present in every CaseHub ARC42STORIES.MD) and in `docs/AGENTIC-HARNESS-GUIDE.md §Anti-patterns` for the full platform-wide list.

---

## Document Artifact Mapping

*Applies to: Application tier primarily. Foundation modules adapt as appropriate.*

| Artifact | Role | Location |
|---|---|---|
| `ARC42STORIES.MD` | Permanent architecture record — §1–§13 | workspace root |
| `design/JOURNAL.md` | Per-epic working doc — feeds ARC42STORIES.MD at close | workspace `design/` |
| `HANDOFF.md` | Per-session continuity — immediate next action | workspace root |
| `blog/` | Session narrative | workspace `blog/` |
| `docs/specs/` | Pre-implementation brainstorm output | project repo |

`ARC42STORIES.MD` absorbs what were previously separate artifacts: `LAYER-LOG.md` (layer entries → §9.4), the Vertical Slice Index (Chapter Index → §9.2), and `DESIGN.md` (cross-cutting decisions → §10). Those files are retired when the migration to `ARC42STORIES.MD` is complete.

---

## Reference Implementations

**Application tier:** casehub-devtown `ARC42STORIES.MD`  
`../devtown/ARC42STORIES.MD` · `https://github.com/casehubio/devtown/blob/main/ARC42STORIES.MD`

**Foundation tier:** *(deferred — will be listed here when the first foundation-tier ARC42STORIES.MD is complete)*

---

## References

- [Arc42Stories Specification](arc42stories-spec.md)
- `docs/AGENTIC-HARNESS-GUIDE.md` — production-first rules, anti-patterns, session conventions
- `docs/ARCHITECTURE.md` — CaseHub architectural patterns
- `docs/PLATFORM.md` — capability ownership and boundary rules
- `casehub/garden: docs/protocols/universal/` — cross-cutting conventions applicable across all casehub modules (module structure, Maven naming, persistence patterns)
