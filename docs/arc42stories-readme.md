# ARC42STORIES

An extension of the arc42 architecture documentation standard. A repo containing
an `ARC42STORIES.MD` file is using this format.

---

## Beyond arc42

[arc42](https://arc42.org) answers three questions well:

- What is this system?
- How is it structured?
- Why were the key decisions made?

It was designed for a world where an architect writes documentation once and it stays largely stable.

Arc42Stories picks up where arc42 stops:

**How is the system being built, incrementally?**

Arc42 documents the system as-is. It has no mechanism for tracking which parts exist
yet, which are in progress, and what depends on what. Delivery planning lives elsewhere
— usually in a ticket tracker with no connection to the architecture.

**How does an LLM resume work across sessions?**

A session ends; context is lost. The next session starts cold. Arc42 can describe a
system but it doesn't record where the last session stopped, what was decided and why,
or what's blocked. Without that, every new session re-establishes context from scratch.

**How does a team in a different domain replicate the same architecture?**

Arc42 captures decisions, not replication steps. A team that wants to apply the same
layer integration in a new domain gets the rationale but not the numbered steps.

---

## Origins

Arc42Stories extends arc42, preserving all 12 original sections and adding a delivery
and replication layer on top. It was developed from practical experience building
LLM-assisted systems where documentation is shared memory across sessions.

The [full specification](arc42stories-spec.md) defines the format. Profiles adapt
it for specific stacks — for example, a multi-module Maven profile would define
conventions for module structure tables, Flyway version ranges, and Quarkus build
configuration; a multi-repo platform profile would define conventions for cross-repo
dependency tracking and cross-repo issue references.

---

## What it adds

**Journeys and Chapters (§9).** A Journey is a major user or business flow. A Chapter
is a vertical cut through the architecture that delivers one end-to-end capability.
Chapters are the planning and delivery unit — each has a status, a layer impact table,
and a linked issue. The Chapter sequence is the delivery roadmap.

**Layer tracking.** Each Chapter records which architectural layers it touches and
how much it changes them (`None` / `Low` / `Medium` / `High`). For a single-module
project the layers might be domain model, service, persistence, and API. For a
multi-module or multi-repo project they might be foundation SPIs, core runtime,
optional extensions, and integration adapters. The format is the same either way.

**Pattern to replicate.** Each Chapter includes domain-agnostic numbered steps for
implementing the same layer integration elsewhere. These are not descriptions of what
was built — they are instructions for replicating it. A team in a different domain
reading the Pattern to replicate should be able to apply the same integration approach
without reading the full design rationale.

**Session journal (§10).** A running log of architectural decisions, discoveries, and
blockers from each working session. This is what an LLM assistant or a developer
returning after a gap reads to understand where things stand without reconstructing
context from scratch.

**Diagrams.** Arc42Stories uses [C4 Model](https://c4model.com) diagrams rendered as [Mermaid](https://mermaid.js.org).

The C4 Model organises architecture diagrams into four levels of abstraction:

| Level | Shows | Audience |
|---|---|---|
| C1 — Context | The system and what it connects to | Anyone |
| C2 — Container | Major building blocks (services, databases, modules) | Developers, architects |
| C3 — Component | What's inside a container | Developers |
| C4 — Code | Class/implementation detail | Rarely needed in practice |

The value over alternatives is a shared vocabulary. Informal box-and-line diagrams
have no agreed meaning for shapes, arrows, or boundaries — every team invents their
own conventions and readers must decode them. UML has formal semantics but is complex
enough that most teams use it inconsistently. C4 sits in between: a small, fixed set
of element types (Person, System, Container, Component) with unambiguous meaning,
designed specifically for software architecture rather than general modelling.

Arc42Stories uses C2 and C3 views, rendered as Mermaid. Mermaid renders natively
in GitHub and most modern documentation tools with no external server or export
step — the diagram lives as text in the markdown file and renders on push. It defines
three diagram types arc42 doesn't:

- **Layer Architecture View** — the full stack, showing all layers and how they relate
- **Chapter View** — filtered to only what one Chapter introduces or modifies
- **Journey Map** — delivery status across Chapters, as a flowchart

---

## Core concepts

| Term | Definition |
|---|---|
| **Journey** | A major user or business flow — the overarching story the system tells |
| **Chapter** | A vertical cut through the layers delivering one capability end-to-end. The planning and delivery unit. |
| **Layer** | A horizontal architectural concern — a technical tier, module group, or infrastructure component. What layers exist depends on the system; they are defined in §4 of the document. |
| **Delta** | How much a Chapter changes a layer: `None` / `Low` / `Medium` / `High` |
| **Pattern to replicate** | Domain-agnostic numbered steps for implementing the same layer integration in a different project |
| **Profile** | A stack-specific adaptation of Arc42Stories defining naming conventions, diagram conventions, and artifact schema for a particular framework or architecture style |

---

## Mapping to epics

A Chapter is the architectural unit — it defines what capability is being delivered
and which layers it touches. How that maps to your issue tracker is left to the
author's discretion based on the scope and complexity of the work.

- A small Chapter in a single-module project may map to a single issue.
- A larger Chapter may map to an epic with child issues beneath it.
- A Chapter spanning multiple repos or modules may map to a parent epic, with child
  epics per layer or repo, mirroring the architectural hierarchy in the tracker.

The Chapter is always the architectural anchor. Whatever tracker structure sits beneath
it — one issue or a tree of epics — the Chapter reference is what ties the architecture
to the delivery.

Chapters are sequenced — a Chapter that depends on a previous one should not start
until that one completes. This reflects architectural dependencies between layers,
not arbitrary prioritisation. The layer taxonomy table in §4 maps each layer to its
owner and shows which Chapters deliver it.

---

## References

- [arc42stories-spec.md](arc42stories-spec.md) — full format specification
- [arc42.org](https://arc42.org) — the original arc42 standard by Gernot Starke & Peter Hruschka
