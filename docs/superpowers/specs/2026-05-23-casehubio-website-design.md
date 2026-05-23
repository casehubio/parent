# casehubio.github.io — Landing Page Design

**Date:** 2026-05-23
**Status:** Approved

---

## Overview

Single-page org website for the casehubio GitHub organisation at `https://casehubio.github.io`. Communicates the "CaseHub — An AI Fusion Harness" positioning, lists all platform repos as hero cards separated by tier, and includes an SVG architecture layer diagram.

**Not included at this stage:** docs link, blog link. GitHub link only.

---

## Tech Stack

Plain HTML + CSS (no Jekyll, no build step). Migration to Jekyll is planned later — file paths are structured to make that migration trivial:

- `index.html` at repo root
- `assets/css/main.css` — matches Jekyll's default asset path convention

CSS is copied from `casehub-poc/docs/assets/css/main.css` and extended with new card and diagram styles.

---

## Repository Location

Local path: `/Users/mdproctor/claude/casehub/casehubio.github.io/`
GitHub: `https://github.com/casehubio/casehubio.github.io`
Serves at: `https://casehubio.github.io`

---

## Page Sections

### 1. Nav

- Left: CaseHub 4-square SVG logo + wordmark "CaseHub"
- Right: single link — "GitHub ↗" → `https://github.com/casehubio`
- No docs, no blog links

### 2. Hero

- Eyebrow (accent, uppercase, small): `Coming Soon`
- h1: `CaseHub`
- h2 (accent colour): `An AI Fusion Harness`
- Subtitle: "Where Classical AI meets LLM AI — production-grade orchestration for regulated multi-agent systems, built on Quarkus."
- CTA button: "View on GitHub ↗" → `https://github.com/casehubio`
- Background: grid overlay + radial glow (same as poc hero)

### 3. What is AI Fusion

Short explainer block (2–3 sentences):

> Classical AI brings structure — rules engines, formal process models (CMMN), Blackboard Architecture, and deterministic reasoning. LLM AI brings adaptability — autonomous agents, natural language understanding, and emergent problem-solving. CaseHub fuses both: a harness where each kind of intelligence does what it does best, coordinated by a compliance-first orchestration layer.

### 4. Architecture SVG Diagram

Inline SVG. Four horizontal bands stacked bottom-to-top, matching the site's dark theme (`--bg-deep`, `--bg-card`, `--border`, `--accent`).

Bands (bottom → top):

| Band | Label | Contents |
|------|-------|----------|
| 1 | Foundation | platform · ledger · work · qhorus · connectors · eidos |
| 2 | Orchestration | casehub-engine |
| 3 | Runtime | claudony |
| 4 | Applications | devtown · aml · clinical · quarkmind |

Right-side annotations:
- "Classical AI" bracket spanning Foundation + Orchestration bands (Blackboard, CMMN, rules)
- "LLM AI" bracket spanning Runtime + Foundation bands (agent mesh, identity, sessions)
- Where they overlap = AI Fusion zone (subtle highlight)

Upward arrows between bands indicate dependency direction (foundation depended on by all above).

### 5. Foundation Cards

Section heading: "Foundation" (with sub-label: "The platform beneath the harness")

8 cards in a responsive grid (3-col desktop, 2-col tablet, 1-col mobile):

| Repo | Headline |
|------|----------|
| `casehub-platform` | Zero-dependency SPI layer — Path, Preferences, Identity |
| `casehub-ledger` | Immutable, cryptographically tamper-evident audit ledger with trust scoring |
| `casehub-work` | Human task lifecycle — inbox, SLA, delegation, routing, and audit trail |
| `casehub-qhorus` | Agent communication mesh with formal speech-act accountability |
| `casehub-connectors` | Outbound message connectors — Slack, Teams, SMS, email |
| `casehub-eidos` | Structured agent identity, capability discovery, and system prompt generation |
| `casehub-engine` | Hybrid choreography + Blackboard orchestration engine (CMMN semantics) |
| `claudony` | Remote Claude CLI sessions and unified ecosystem dashboard |

Each card: repo name (monospace badge) · headline · 2-sentence description (from deep-dive docs) · "View on GitHub ↗" link → `https://github.com/casehubio/<repo>`.

claudony GitHub URL: `https://github.com/casehubio/claudony`

### 6. Application Cards

Section heading: "Applications" (with sub-label: "Domain-specific harnesses built on the platform")

4 cards in the same grid:

| Repo | Headline |
|------|----------|
| `casehub-devtown` | AI-assisted PR review with adaptive specialist routing and tamper-evident records |
| `casehub-aml` | AML investigation — FinCEN-compliant, adaptive investigation paths |
| `casehub-clinical` | Clinical trial coordination — GCP/FDA/GDPR-compliant multi-site case management |
| `quarkmind` | StarCraft II game AI — living lab proving the harness at millisecond granularity |

### 7. Footer

- Left: CaseHub logo wordmark
- Centre: "GitHub ↗" → `https://github.com/casehubio`
- Right: "Apache 2.0"

---

## Visual Design

Copied directly from `casehub-poc/docs/assets/css/main.css`:

```css
--bg-deep:    #080d12;
--bg-card:    #0e1820;
--border:     #1a2e38;
--accent:     #2aa8c4;
--text:       #b8d8e0;
--text-muted: #4a7a8a;
```

Logo: 4-square SVG (2×2 grid of rounded rectangles, accent colour, varying opacity: 0.9 / 0.6 / 0.6 / 0.3).

New styles needed (extend main.css):
- `.project-cards` — responsive grid for repo cards
- `.project-card` — individual card with hover border accent
- `.card-repo` — monospace repo name badge
- `.arch-diagram` — wrapper for SVG diagram section
- `.what-is-section` — AI Fusion explainer block

---

## Out of Scope

- Docs pages
- Blog
- Search
- Dark/light mode toggle
- Any Jekyll templating (deferred to B-phase migration)
