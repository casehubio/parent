# casehub-drafthouse — Deep Dive

## What It Is

DraftHouse is an MCP-driven document review tool. Any LLM (Claude Code, Claudony, or
any MCP client) can open a document, show before/after versions, create reviewer LLM
agents, and have grounded conversations about specific parts of the document.

Evolved from md-compare — a side-by-side markdown comparison tool. Promoted to CaseHub
application tier to leverage Qhorus for conversation channels and LangChain4j for
provider-agnostic LLM calls.

## What It Owns

- Document comparison UI (side-by-side rendered markdown with LCS diff)
- MCP tool surface for LLM-driven document review
- Reviewer agent lifecycle (personality library, conversation strategies)
- Document version history (git worktree-based)

## What It Does NOT Own

Everything in the CaseHub foundation: audit trail (casehub-ledger), channels and
messaging (casehub-qhorus), case orchestration (casehub-engine), human task inbox
(casehub-work), outbound notifications (casehub-connectors), agent identity
(casehub-eidos).

## Dependencies

```
casehub-qhorus    — channels, typed messages, instance registry
LangChain4j       — provider-agnostic LLM calls (Quarkus extension)
JGit              — version history via git worktrees
```

Future: casehub-engine (if case orchestration needed), casehub-eidos (agent identity).

## Module Structure

Currently flat (`server/` with Quarkus app). Will adopt `api/` + `app/` hexagonal
structure when the first CaseHub foundation dependency is wired in.

## Key Epics

1. Scaffold — infrastructure migration from md-compare (done)
2. MCP tool surface — start_review, push_revision, get_cursor_context, get_diff, end_review
3. Qhorus channels — conversation threading per review session
4. LangChain4j reviewer — single internal reviewer agent
5. Selection-scoped conversations — per-selection Qhorus channels with anchored UI
6. Multi-LLM reviewers — personality library, ReviewStrategy SPI

## Design Documents

- Research spec: `docs/superpowers/specs/2026-05-26-document-review-tool-research.md` (in drafthouse repo)
