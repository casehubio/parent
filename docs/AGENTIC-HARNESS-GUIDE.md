# Agentic Harness Guide

This document applies to every CaseHub application repo:
**casehub-aml, casehub-clinical, casehub-devtown, QuarkMind**

Read this at session start alongside your CLAUDE.md.

---

## What You Are

You are an **agentic harness** — infrastructure that coordinates multiple agents (human
and AI), enforces formal accountability per interaction, adapts execution paths based on
accumulated context, and produces an independently verifiable audit trail. The domain
varies; the harness structure underneath is the same across all four apps.

See `docs/repos/{your-app}.md` in casehub-parent for your harness structure and tutorial
layers. See `docs/tutorial-strategy.md §2.0` for the full agentic harness concept.

---

## Your Two Goals

**Primary — Reference architecture and industry engagement**

Build a production-grade application that demonstrates what CaseHub makes possible in
your domain. This is the primary goal. Every architectural decision serves a deployed,
real system — not a teaching scenario.

Audiences: practitioners in your field evaluating CaseHub, potential adopters, industry
partners. They need to see that CaseHub solves real compliance and coordination problems
they recognise from their own work.

**Secondary — LLM and human tutorials**

The tutorial structure and how-to content emerge from building the application correctly.
An LLM reading your code, LAYER-LOG.md, blog entries, and git history should have
everything it needs to build a fifth harness in any domain without asking questions.
Human tutorials can be generated from that same material later.

**The constraint:** Do not design or architect for the tutorial. The tutorial documents
what you built. Code that exists only for the tutorial is wrong code.

---

## What to Produce and Maintain

### LAYER-LOG.md — the primary new artifact

One file at the project root. A structured record that grows with each completed layer.
This is the raw material for LLM and human tutorials. **A layer is not complete until
its LAYER-LOG.md entry is written.**

Each entry captures:
- What was built and what gap it closes
- The gap comments from the naive layer that this layer addresses
- Key wiring (the non-obvious configuration — not in the code, not in the docs)
- Gotchas (what went wrong, what would go wrong without prior knowledge)
- Pattern to replicate — domain-agnostic numbered steps an LLM can follow in a
  different domain

See `docs/protocols/universal/layer-log.md` in casehub-parent for the full format.
See `LAYER-LOG.md` in casehub-aml for a reference implementation (Layers 1 and 2).

### Existing habits to maintain

Nothing new beyond LAYER-LOG.md. Continue:

| Artifact | Purpose | Where |
|----------|---------|-------|
| Blog/diary entries | Narrative context per session | workspace `blog/` |
| CLAUDE.md | Session conventions, always current | project root |
| GitHub issues/epics | Layer-by-layer structure tracked | GitHub |
| ADRs | Significant architectural decisions | `docs/adr/` |

Blog entries correlate with LAYER-LOG.md but serve a different purpose — narrative for
humans; the log is structured for LLMs. Both are needed.

---

## Retroactive Work

When starting a new session in an app that has existing code but no LAYER-LOG.md:

### Step 1 — Establish what has been built

```bash
# Project repo git history
git log --oneline | head -40

# GitHub issues
gh issue list --state closed --repo casehubio/{app}
gh issue list --state open --repo casehubio/{app}
```

### Step 2 — Find blog and diary entries

Check in this order:
1. Workspace `blog/` directory — primary location
2. `~/claude/mdproctor.github.io/` — published notes (look for `notes-{app}.md`
   or dated entries referencing this app)
3. `~/mdproctor.github.io/` — secondary published location

**If entries are missing or you can't find enough to reconstruct a layer confidently —
stop and ask the user before writing the log.** Do not reconstruct from incomplete
information; gaps in the log are better than wrong entries.

### Step 3 — Map commits and entries to layers

For each completed layer (see your repo deep-dive in casehub-parent for the layer table):
- Which commits correspond to this layer?
- Is there a blog entry covering it?
- Is there a GitHub issue that was closed for it?

### Step 4 — Write LAYER-LOG.md entries retroactively

One entry per completed layer. Use git history, blog entries, and issues as source
material. If a section (e.g. "Gotchas") cannot be reconstructed, leave a note:
`*Not captured retroactively — check git log for {commit range}.*`

### Step 5 — Identify the current layer

From the layer table in your repo deep-dive: what is the next layer to build?
Create a GitHub issue for it if none exists (check Epic for tutorial layers first).

---

## Ongoing Maintenance (per layer)

When completing any layer:

1. Write the LAYER-LOG.md entry **before** marking the issue closed
2. The entry is part of the PR / commit, not a follow-up
3. Update your repo deep-dive in casehub-parent — change layer status from `pending`
   to `in progress` or `complete` (create issue on casehubio/parent if you cannot
   commit there directly)
4. Write a blog entry for the session
5. Check CLAUDE.md for drift

---

## Layer Structure Reference

Your layer structure is defined in two places:
- `docs/repos/{your-app}.md` in casehub-parent — Tutorial Layers table with status
- `docs/tutorial-strategy.md §{N}` in casehub-parent — teaching objectives and code
  sketches per layer

**Reference implementation:** casehub-aml — Layers 1 and 2 complete. Read
`LAYER-LOG.md` in casehub-aml before writing your own. The AML log is the pattern.

---

## Agentic Harness Protocols

Before implementing any layer, read:

1. `docs/protocols/universal/INDEX.md` in casehub-parent — universal Java/Quarkus conventions
2. `docs/protocols/casehub/HARNESS-INDEX.md` in casehub-parent — CaseHub app conventions

Key protocols that apply immediately:
- `layer-log.md` — LAYER-LOG.md as definition of done
- Hexagonal module placement (pending — follow AML's pattern: `api/` JPA-free, `app/` owns use-case orchestration)
- casehub-work Hibernate scan packages (pending — see AML LAYER-LOG.md Layer 2 §Key wiring)
