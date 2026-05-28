# Arc42Stories — CaseHub Profile

**Applies to:** casehub-aml, casehub-clinical, casehub-devtown, casehub-life, casehub-drafthouse, QuarkMind

This Profile instantiates [Arc42Stories](arc42stories-spec.md) for CaseHub agentic harness applications. It defines the CaseHub Foundation Layer taxonomy, CaseHub-specific conventions, and the relationship to existing CaseHub documentation artifacts.

---

## CaseHub Artifact Schema

Each CaseHub harness app uses this schema. Copy it into §1 of `ARC42STORIES.MD` and set the app-specific PREFIX.

| Artifact type | Format | Example | Where it lives |
|---|---|---|---|
| Improvement log entry | `[PREFIX]-NNN` | `DT-042` | `docs/PROGRESS.md` |
| Issue | `#NNN` or `casehubio/[repo]#NNN` | `#52`, `casehubio/devtown#52` | GitHub Issues |
| Garden entry | `GE-YYYYMMDD-XXXXXX` | `GE-20260521-e39ad1` | `~/.hortora/garden/` |
| Protocol | `PP-YYYYMMDD-XXXXXX` | `PP-20260522-f08b62` | `casehub-parent/docs/protocols/` |
| ADR | `ADR-NNNN` | `ADR-0007` | `docs/adr/` |
| Blog entry | `YYYY-MM-DD-[initials]NN-title` | `2026-05-19-mdp01-layer-5-lands` | workspace `blog/` |
| Design spec | `YYYY-MM-DD-topic-design` | `2026-05-15-epic3-design` | `docs/specs/` |

**PREFIX by app:**

| App | PREFIX |
|---|---|
| casehub-devtown | `DT` |
| casehub-aml | `AML` |
| casehub-clinical | `CLI` |
| casehub-life | `LIF` |
| casehub-drafthouse | `DH` |
| QuarkMind | `QM` |

---

## CaseHub Foundation Layer Taxonomy

Replace the generic Arc42Stories layer model with the CaseHub harness stack:

| Layer | Foundation module | What it adds |
|---|---|---|
| Domain baseline | *(none — pure Java)* | Domain vocabulary, port interfaces, `@DefaultBean` baseline service |
| casehub-work | `casehub-work` | Human task lifecycle — WorkItem, SLA, escalation, breach policy |
| casehub-qhorus | `casehub-qhorus` | Agent communication mesh — COMMAND/DONE/DECLINE, commitment lifecycle |
| casehub-ledger | `casehub-ledger` | Tamper-evident audit — Merkle chain, trust scoring, GDPR |
| casehub-engine | `casehub-engine` | Adaptive orchestration — CasePlanModel, content-driven routing, WAITING state |
| Trust routing | `casehub-ledger` (trust APIs) | Trust-weighted agent selection from outcome attestations |

This is the natural integration sequence. Justification for a different order belongs in §4 Solution Strategy.

---

## CaseHub Conventions (§8 Crosscutting Concepts)

Reference these protocols rather than duplicating their content:

| Concern | Protocol |
|---|---|
| Module structure | `docs/protocols/universal/module-tier-structure.md` |
| Flyway migrations | `docs/protocols/casehub/flyway-version-range-allocation.md` |
| Named datasources | `docs/PLATFORM.md` §Persistence |
| CDI displacement (`@DefaultBean`) | `docs/protocols/casehub/alternative-extension-patterns.md` |
| SPI placement | `docs/PLATFORM.md` §Step 4 |
| Architectural patterns | `docs/ARCHITECTURE.md` |
| Capability ownership | `docs/PLATFORM.md` Capability Ownership table |

---

## Platform References (§3 Context and Scope)

Every CaseHub harness app's §3 should reference:

- `docs/PLATFORM.md` — capability ownership table and boundary rules
- `docs/repos/{this-app}.md` — what this application owns
- `docs/gastown-casehub-analysis-v2.md` (devtown) or equivalent comparison baseline
- `docs/orchestration-advantages.md` (devtown) or equivalent

---

## Document Artifact Mapping

Arc42Stories for CaseHub produces one permanent document per application:

| Artifact | Role | Location |
|---|---|---|
| `ARC42STORIES.MD` | Permanent architecture record — §1–§13 | workspace root |
| `design/JOURNAL.md` | Per-epic working doc — feeds ARC42STORIES.MD at close | workspace `design/` |
| `HANDOFF.md` | Per-session continuity — immediate next action | workspace root |
| `blog/` | Session narrative | workspace `blog/` |
| `docs/specs/` | Pre-implementation brainstorm output | project repo |

`ARC42STORIES.MD` absorbs what were previously separate artifacts: `LAYER-LOG.md` (layer entries → §9.4), the Vertical Slice Index (Chapter Index → §9.2), and `DESIGN.md` (cross-cutting decisions → §10). Those files are retired when the migration to `ARC42STORIES.MD` is complete.

---

## Production-First Constraint

Before writing any class, apply the production-first test:

> "Would this class exist in a production system that does not include any other Chapters?"

If no — do not build it. Document the architecture in the Arc42Stories document instead. See `docs/AGENTIC-HARNESS-GUIDE.md §Anti-patterns` for concrete examples of what this rules out.

---

## Example: devtown Journey and Chapters

### Journey: PR Review Coordination

*A submitted pull request is reviewed by specialist agents with formal accountability, human oversight with SLA, and a tamper-evident audit trail that traces any production incident back to the review decision that allowed it.*

### Chapter Index

| # | Chapter | Layers | Delta | Status |
|---|---|---|---|---|
| 1 | Case opens and routes | Domain baseline, casehub-engine | Low, High | ✅ |
| 2 | Human review with SLA | + casehub-work | Medium | ✅ |
| 3 | Formal agent obligation | + casehub-qhorus | Low | 🔲 |
| 4 | Tamper-evident audit | + casehub-ledger | Medium | 🔲 |
| 5 | Trust-weighted selection | + Trust routing | Medium | 🔲 |

**Sequencing rationale:**
- C1 before C2: engine runtime established in C1; casehub-work-adapter depends on engine events
- C2 before C3: SLA gate in place before formal agent obligation tracking
- C3 before C4: qhorus messaging generates MessageLedgerEntry chain that makes audit meaningful
- C4 before C5: trust scoring reads attestation data written by ledger — hard dependency
- C1 built before C2 historically (engine was the architectural priority): correct Chapter practice, not a violation

---

## References

- [Arc42Stories Specification](arc42stories-spec.md)
- `docs/AGENTIC-HARNESS-GUIDE.md` — production-first rules, anti-patterns, session conventions
- `docs/ARCHITECTURE.md` — CaseHub architectural patterns
- `docs/PLATFORM.md` — capability ownership and boundary rules
- `docs/protocols/universal/` — universal Quarkus conventions
