# CaseHub Platform Index

> Universal entry point for every LLM session. Start here — find your audience,
> then follow links to capability-specific documentation.

## Choose Your Path

| Audience | Start here | What you'll find |
|----------|-----------|-----------------|
| **App builder** — consuming platform capabilities | [Consumer Index](consumer-index.md) | Modules to depend on, APIs, SPIs to implement, configuration, quick start |
| **Platform builder** — modifying platform internals | [Contributor Index](contributor-index.md) | Architecture, internal SPIs, module structure, extension points |

Both indexes link to per-repo guides aggregated via git subtree at `repos/<name>/`.
Each repo owns its own `docs/guides/consumer-guide.md` and `docs/guides/contributor-guide.md`.

---

## Cross-Cutting (both audiences)

### Architecture & Conventions
- [Architecture](ARCHITECTURE.md) — tier patterns, dependency rule, selective event sourcing
- [DSL Style Guide](DSL-STYLE-GUIDE.md) — fluent API conventions
- [Lifecycle](LIFECYCLE.md) — state machines, terminal semantics
- [Boundary Rules](platform/boundary-rules.md) — all "do not" rules across the platform
- [Overlap Risks](platform/overlap-risks.md) — known semantic collisions
- [Protocols](platform/protocols.md) — implementation conventions (audience-mapped)
  - Full protocol indexes: [universal](../../garden/docs/protocols/universal/INDEX.md) · [foundation](../../garden/docs/protocols/casehub/FOUNDATION-INDEX.md) · [harness](../../garden/docs/protocols/casehub/HARNESS-INDEX.md)

### Platform Operations
- [Coherence Protocol](platform/coherence-protocol.md) — 6-step pre-implementation check
- [Capability Ownership](platform/capability-ownership.md) — "where does X live?" lookup
- [Dependency Map](platform/dependency-map.md) — cross-repo impact analysis
- [Overview](platform/overview.md) — tier structure, repo map, build order

### Topic Deep-Dives
- [Routing](platform/routing.md) — trust-weighted, semantic, CBR-evidence agent selection
- [CBR](platform/cbr.md) — case-based reasoning: retrieve, reuse, revise, retain
- [Agent Mesh](platform/agent-mesh.md) — 3-channel normative layout, mesh participation
- [Agent Identity](platform/agent-identity.md) — DID format, SCIM2, versioning
- [Auth](platform/auth.md) — gateway topology, roles, outbound credentials
- [Notifications](platform/notifications.md) — subscription engine, delivery, digest batching
- [Privacy](platform/privacy.md) — GDPR erasure, PII sanitisation
- [Persistence](platform/persistence.md) — Flyway conventions, datasource naming
- [Observability](platform/observability.md) — OTel tracing, audit entries, ledger correlation
- [Channels](CHANNELS.md) — purpose categories, discriminator dimensions
- [UI Architecture](platform/ui-architecture.md) — pages → blocks-ui → app UI layering

### Guides & Tools
- [API Reference](api/INDEX.md) — machine-generated type signatures, method contracts (per-repo + cross-repo SPI matrix)
- [Building Apps](guides/building-apps.md) — capability matrix, pattern catalogue, placement criteria
- [Building Platform](guides/building-platform.md) — adding capabilities, SPI design, boundary enforcement
- [Agentic Harness](AGENTIC-HARNESS-GUIDE.md) — session conventions for LLM work in app repos
- [arc42stories spec](arc42stories-spec.md) — standard architecture documentation format
- [Config Architecture](config-architecture.md) — topic ownership, what's authoritative where
- [New Repo Checklist](new-repo-checklist.md) — setup steps for adding a new repository
- [Applications](APPLICATIONS.md) — all domain applications with status

### Prompt Snippets
- [Prompt Snippets](prompt-snippets.md) — work-item opening sequences, doc-sync reminders
