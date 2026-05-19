# Audit 4 — repos/ Depth Check Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Trim all 9 `docs/repos/*.md` files to family-awareness level — no class names, method signatures, or implementation detail — and create DESIGN.md stubs for the 4 repos that lack one.

**Architecture:** Rubric-first sweep. The depth rubric is defined once and applied uniformly: keep domain concept names at abstract level, module structure, what the repo does NOT do, and dependency graph; remove specific class names, method signatures, field names, bean annotations, and MCP tool method lists. Each trimmed section gets a `See docs/DESIGN.md for [detail type].` pointer.

**Tech Stack:** Markdown, git. No code changes.

**Issue:** casehubio/parent#31
**Spec:** `docs/superpowers/specs/2026-05-19-audit-4-repos-depth-check.md`

---

## The Depth Rubric (apply to every sentence in every file)

**Keep:** domain concept names as abstractions (Channel, WorkItem, LedgerEntry), module names and tier (api/core/runtime), what the repo does NOT do, who consumes it and why, dependency graph, SPI names at abstract level.

**Remove:** specific class names (`ChannelGateway`, `LedgerWriteService`), method names and signatures (`verify(UUID subjectId)`), field names, bean annotations, internal state counts, MCP tool method lists, JPA implementation names, CDI event type names.

**Replace each removed block with:** `See docs/DESIGN.md for [what was removed — e.g. "service class structure", "SPI contracts and default implementations"].`

**Verification command** (run after each file, target is near-zero):
```bash
grep -oE '`[A-Z][a-zA-Z]+`' ~/claude/casehub/parent/docs/repos/<file>.md | wc -l
```

---

## File Map

| Task | File | Class-refs | DESIGN.md |
|------|------|-----------|-----------|
| 1 | Create stubs | — | connectors/devtown/aml/clinical: create |
| 2 | `casehub-qhorus.md` | 64 | ✅ `~/claude/casehub/qhorus/docs/DESIGN.md` |
| 3 | `casehub-engine.md` | 54 | ✅ `~/claude/casehub/engine/docs/DESIGN.md` |
| 4 | `casehub-ledger.md` | 44 | ✅ `~/claude/casehub/ledger/docs/DESIGN.md` |
| 5 | `casehub-work.md` | 42 | ✅ `~/claude/casehub/work/docs/DESIGN.md` |
| 6 | `claudony.md` | 36 | ✅ `~/claude/casehub/claudony/docs/DESIGN.md` |
| 7 | `casehub-clinical.md` | 10 | stub in Task 1 |
| 8 | `casehub-aml.md` | 5 | stub in Task 1 |
| 9 | `casehub-devtown.md` | 3 | stub in Task 1 |
| 10 | `casehub-connectors.md` | 2 | stub in Task 1 |
| 11 | Protocol/garden scan | — | — |

---

## Task 1: Create DESIGN.md stubs for the 4 repos without one

**Files:**
- Create: `~/claude/casehub/connectors/docs/DESIGN.md`
- Create: `~/claude/casehub/devtown/docs/DESIGN.md`
- Create: `~/claude/casehub/aml/docs/DESIGN.md`
- Create: `~/claude/casehub/clinical/docs/DESIGN.md`

- [ ] **Step 1: Create stub for casehub-connectors**

```bash
mkdir -p ~/claude/casehub/connectors/docs
cat > ~/claude/casehub/connectors/docs/DESIGN.md << 'EOF'
# casehub-connectors — Design

## Architecture

_To be documented._

## Module Structure

| Module | Type | Purpose |
|--------|------|---------|
| _(add modules)_ | | |

## Key Abstractions

_To be documented._

## SPI Contracts

_To be documented._

## Configuration

_To be documented._
EOF
git -C ~/claude/casehub/connectors add docs/DESIGN.md
git -C ~/claude/casehub/connectors commit -m "chore: add DESIGN.md stub — Refs casehubio/parent#31"
```

- [ ] **Step 2: Create stub for casehub-devtown**

```bash
mkdir -p ~/claude/casehub/devtown/docs
cat > ~/claude/casehub/devtown/docs/DESIGN.md << 'EOF'
# casehub-devtown — Design

## Architecture

_To be documented._

## Module Structure

| Module | Type | Purpose |
|--------|------|---------|
| _(add modules)_ | | |

## Key Abstractions

_To be documented._

## Data Model

_To be documented._

## Configuration

_To be documented._
EOF
git -C ~/claude/casehub/devtown add docs/DESIGN.md
git -C ~/claude/casehub/devtown commit -m "chore: add DESIGN.md stub — Refs casehubio/parent#31"
```

- [ ] **Step 3: Create stub for casehub-aml**

```bash
mkdir -p ~/claude/casehub/aml/docs
cat > ~/claude/casehub/aml/docs/DESIGN.md << 'EOF'
# casehub-aml — Design

## Architecture

_To be documented._

## Module Structure

| Module | Type | Purpose |
|--------|------|---------|
| _(add modules)_ | | |

## Key Abstractions

_To be documented._

## Data Model

_To be documented._

## Configuration

_To be documented._
EOF
git -C ~/claude/casehub/aml add docs/DESIGN.md
git -C ~/claude/casehub/aml commit -m "chore: add DESIGN.md stub — Refs casehubio/parent#31"
```

- [ ] **Step 4: Create stub for casehub-clinical**

```bash
mkdir -p ~/claude/casehub/clinical/docs
cat > ~/claude/casehub/clinical/docs/DESIGN.md << 'EOF'
# casehub-clinical — Design

## Architecture

_To be documented._

## Module Structure

| Module | Type | Purpose |
|--------|------|---------|
| _(add modules)_ | | |

## Key Abstractions

_To be documented._

## Data Model

_To be documented._

## Configuration

_To be documented._
EOF
git -C ~/claude/casehub/clinical add docs/DESIGN.md
git -C ~/claude/casehub/clinical commit -m "chore: add DESIGN.md stub — Refs casehubio/parent#31"
```

---

## Task 2: Trim `casehub-qhorus.md` (64 class-refs)

**Files:**
- Modify: `~/claude/casehub/parent/docs/repos/casehub-qhorus.md`

The main violations are in: **Key Abstractions** (Domain Model class names with internal state details), **Channel Gateway** (specific class table), **Ledger Integration** (class names + method lists), **MCP Tool Surface** (full tool method list).

- [ ] **Step 1: Read the full file**

```bash
cat ~/claude/casehub/parent/docs/repos/casehub-qhorus.md
```

- [ ] **Step 2: Apply rubric — Domain Model table**

The Domain Model table lists 7 entities with implementation detail. Keep the entity names and their abstract purpose; remove internal state counts, ACL field names, and class-level detail.

Replace the `### Domain Model` section's table content with:

```markdown
### Domain Model

| Concept | Purpose |
|---|---|
| Channel | Typed communication channel with pluggable backend semantics and access control |
| Message | Speech-act message — 9 types covering the full normative interaction vocabulary |
| Commitment | Obligation with a defined lifecycle from creation to terminal resolution |
| Instance | Agent registry entry with capability-based addressing |
| SharedData | Shared artefact store with claim/release lifecycle |
| PendingReply | Long-poll correlation for request/response patterns |
| Watchdog | Condition-based alert registration |

See `docs/DESIGN.md` for channel semantics, message type vocabulary, commitment state machine, and addressing modes.
```

- [ ] **Step 3: Apply rubric — Channel Gateway section**

Replace the `### Channel Gateway` class table and its inline implementation notes with:

```markdown
### Channel Gateway

Outbound messages route through pluggable channel backends. Inbound human messages
are normalised to a canonical form before processing. A default backend wraps the
core message service and is always registered.

See `docs/DESIGN.md` for the gateway class structure, backend SPI contracts, and
inbound normalisation pipeline.
```

- [ ] **Step 4: Apply rubric — Ledger Integration section**

Replace the `### Ledger Integration` class table with:

```markdown
### Ledger Integration

All 9 message types are recorded as tamper-evident ledger entries. Telemetry fields
(tool name, duration) are extracted from structured EVENT messages.

See `docs/DESIGN.md` for the ledger entry subclass structure and query capabilities.
```

- [ ] **Step 5: Apply rubric — MCP Tool Surface section**

Replace the `### MCP Tool Surface` tool method list with:

```markdown
### MCP Tool Surface

Claude Code agents interact with qhorus via MCP tools covering: instance management,
channel management, backend management, messaging, shared data, commitments, and
watchdog alerts. Both blocking and reactive variants are provided.

See `docs/DESIGN.md` for the full tool inventory.
```

- [ ] **Step 6: Apply rubric — remaining class references**

Scan the rest of the file for any remaining backtick class names:
```bash
grep -n '`[A-Z][a-zA-Z]\+`' ~/claude/casehub/parent/docs/repos/casehub-qhorus.md
```
For each hit: if it's a concept name used abstractly (e.g. `Channel`, `Message`) — keep it. If it's an implementation class (`InProcessMessageBus`, `ChannelBackend`) — remove and replace with prose description.

- [ ] **Step 7: Verify**

```bash
grep -oE '`[A-Z][a-zA-Z]+`' ~/claude/casehub/parent/docs/repos/casehub-qhorus.md | sort | uniq -c | sort -rn | head -20
```

Expected: only abstract concept names remain (Channel, Message, Commitment, etc.). No service class names, no method signatures.

- [ ] **Step 8: Commit**

```bash
git -C ~/claude/casehub/parent add docs/repos/casehub-qhorus.md
git -C ~/claude/casehub/parent commit -m "docs(audit-4): trim casehub-qhorus to family-awareness level — Refs #31"
```

---

## Task 3: Trim `casehub-engine.md` (54 class-refs)

**Files:**
- Modify: `~/claude/casehub/parent/docs/repos/casehub-engine.md`

Main violations: **Key Abstractions** (class tables for Core Model, Engine Handlers, Worker Provisioner SPIs), **Module Structure** (specific class names in module descriptions).

- [ ] **Step 1: Read the full file**

```bash
cat ~/claude/casehub/parent/docs/repos/casehub-engine.md
```

- [ ] **Step 2: Apply rubric — Core Model table**

The Core Model table lists specific classes with internal detail. Replace with:

```markdown
### Core Model

| Concept | Purpose |
|---|---|
| Case Definition | Declarative specification of capabilities, workers, bindings, goals, and milestones |
| Case Instance | Running case — tracks lifecycle status through active, waiting, completed, and faulted states |
| Event Log | Append-only decision audit trail for restart recovery |
| Case Lifecycle Event | CDI event fired on case status transitions |

See `docs/DESIGN.md` for the class structure, status enumeration, and event payload shapes.
```

- [ ] **Step 3: Apply rubric — Engine Handlers table**

Replace the Engine Handlers class table with:

```markdown
### Engine Handlers

The engine contains CDI handlers for the two execution paths: choreography (context-change
driven) and orchestration (suspend/resume). Worker scheduling runs via Quartz. A
restart-durable correlation registry bridges the orchestration path across restarts.

See `docs/DESIGN.md` for handler responsibilities and the choreography vs orchestration
decision boundary.
```

- [ ] **Step 4: Apply rubric — Worker Provisioner SPIs table**

Replace the detailed SPI table with:

```markdown
### Worker Provisioner SPIs

The engine defines SPIs for worker lifecycle (provision, terminate), worker status
(started, completed, stalled), context, and channel access. Both blocking and reactive
variants are provided. Deployment-specific implementations belong in the deploying app.

See `docs/DESIGN.md` for the full SPI inventory and implementation guidance.
```

- [ ] **Step 5: Scan and fix remaining class references**

```bash
grep -n '`[A-Z][a-zA-Z]\+`' ~/claude/casehub/parent/docs/repos/casehub-engine.md
```

Apply rubric to each hit. Keep `CaseInstance`, `EventLog` if used abstractly. Remove `WorkOrchestrator`, `PendingWorkRegistry`, `CaseContextChangedEventHandler`.

- [ ] **Step 6: Verify and commit**

```bash
grep -oE '`[A-Z][a-zA-Z]+`' ~/claude/casehub/parent/docs/repos/casehub-engine.md | wc -l
git -C ~/claude/casehub/parent add docs/repos/casehub-engine.md
git -C ~/claude/casehub/parent commit -m "docs(audit-4): trim casehub-engine to family-awareness level — Refs #31"
```

---

## Task 4: Trim `casehub-ledger.md` (44 class-refs)

**Files:**
- Modify: `~/claude/casehub/parent/docs/repos/casehub-ledger.md`

Main violations: **Services (CDI Beans)** table with bean names + method signatures, **SPIs** table with JPA class names, **Supplements** table.

- [ ] **Step 1: Read the full file**

```bash
cat ~/claude/casehub/parent/docs/repos/casehub-ledger.md
```

- [ ] **Step 2: Apply rubric — Services table**

Replace the `### Services (CDI Beans)` table with:

```markdown
### Services

The ledger provides services for: cryptographic verification and inclusion proofs,
Merkle tree operations, optional Ed25519 tlog-checkpoint publishing, W3C PROV-DM
lineage export, GDPR Art.17 token-severing erasure, nightly trust score recomputation,
trust score CDI routing events, and trust score read-model export.

See `docs/DESIGN.md` for service class structure and configuration properties.
```

- [ ] **Step 3: Apply rubric — SPIs table**

Replace the `### SPIs` table with:

```markdown
### SPIs

Consumer-implemented SPIs cover: ledger entry persistence, trust score persistence,
actor identity tokenisation/erasure, PII sanitisation, OTel trace ID extraction,
trust score import, and trust bootstrapping. Each SPI ships a no-op or stub default;
JPA implementations are provided as built-in alternatives.

See `docs/DESIGN.md` for the full SPI list, defaults, and implementation guidance.
```

- [ ] **Step 4: Apply rubric — Supplements table**

Replace the `### Supplements` table with:

```markdown
### Supplements

Optional attachments extend ledger entries with compliance fields (GDPR Art.22 / EU AI Act
Art.12 decision records) and data lineage (W3C PROV-DM source and workflow references).

See `docs/DESIGN.md` for supplement structure.
```

- [ ] **Step 5: Scan remaining, verify, commit**

```bash
grep -n '`[A-Z][a-zA-Z]\+`' ~/claude/casehub/parent/docs/repos/casehub-ledger.md
grep -oE '`[A-Z][a-zA-Z]+`' ~/claude/casehub/parent/docs/repos/casehub-ledger.md | wc -l
git -C ~/claude/casehub/parent add docs/repos/casehub-ledger.md
git -C ~/claude/casehub/parent commit -m "docs(audit-4): trim casehub-ledger to family-awareness level — Refs #31"
```

---

## Task 5: Trim `casehub-work.md` (42 class-refs)

**Files:**
- Modify: `~/claude/casehub/parent/docs/repos/casehub-work.md`

Main violations: **WorkItem Entity** section (field names, status enumerations as class-level), **Core Services** table (bean names + method signatures), **REST API** section (endpoint paths + request type names), **CDI Events** section (event class names).

- [ ] **Step 1: Read the full file**

```bash
cat ~/claude/casehub/parent/docs/repos/casehub-work.md
```

- [ ] **Step 2: Apply rubric — WorkItem Entity section**

Replace with:

```markdown
### WorkItem

The core human task entity. Tracks lifecycle status (10 statuses from creation through
terminal states), SLA deadlines, delegation, escalation, and spawn. Supports named outcome
classifications and conflict-of-interest user exclusion.

See `docs/DESIGN.md` for the WorkItem field model, status enumeration, and lifecycle rules.
```

- [ ] **Step 3: Apply rubric — Core Services table**

Replace the `### Core Services` bean/method table with:

```markdown
### Core Services

Services cover: task lifecycle management (create, claim, complete, delegate, expire),
M-of-N parallel group completion coordination, worker routing and selection, label-based
queue views (optional module), and semantic/embedding-based worker matching (optional module).

See `docs/DESIGN.md` for service class structure and the core/runtime split boundary.
```

- [ ] **Step 4: Apply rubric — REST API section**

Replace the REST API endpoint/request-type detail with:

```markdown
### REST API

REST endpoints cover task inbox management, lifecycle transitions, delegation, escalation,
and SLA queries. See `docs/DESIGN.md` for the full endpoint inventory and request/response shapes.
```

- [ ] **Step 5: Apply rubric — CDI Events section**

Replace CDI event class names with:

```markdown
### CDI Events

CDI events fire on WorkItem lifecycle transitions and on M-of-N group completion. Both
are consumed by casehub-engine for case coordination. See `docs/DESIGN.md` for event types and payload shapes.
```

- [ ] **Step 6: Scan remaining, verify, commit**

```bash
grep -n '`[A-Z][a-zA-Z]\+`' ~/claude/casehub/parent/docs/repos/casehub-work.md
grep -oE '`[A-Z][a-zA-Z]+`' ~/claude/casehub/parent/docs/repos/casehub-work.md | wc -l
git -C ~/claude/casehub/parent add docs/repos/casehub-work.md
git -C ~/claude/casehub/parent commit -m "docs(audit-4): trim casehub-work to family-awareness level — Refs #31"
```

---

## Task 6: Trim `claudony.md` (36 class-refs)

**Files:**
- Modify: `~/claude/casehub/parent/docs/repos/claudony.md`

Main violations: **Key Abstractions** subsections (class names in Core, CaseHub SPI Implementations, Application layers), **Persistence Model** (table names + JPA entity names), **Terminal Streaming**, **Authentication**, **MCP Transport** sections.

- [ ] **Step 1: Read the full file**

```bash
cat ~/claude/casehub/parent/docs/repos/claudony.md
```

- [ ] **Step 2: Apply rubric to all Key Abstractions subsections**

For each of `### Core`, `### CaseHub SPI Implementations`, `### Application`: replace class-name tables with prose describing what the module owns at concept level, with a `See docs/DESIGN.md` pointer.

Example for `### Core`:
```markdown
### Core (`claudony-core`)

Shared types and utilities used across claudony modules. No Quarkus or external
framework dependencies.

See `docs/DESIGN.md` for the type inventory.
```

Apply the same pattern to the other two subsections, keeping module names and their purpose without class names.

- [ ] **Step 3: Apply rubric — Persistence Model**

Replace table column names and entity class names with:

```markdown
## Persistence Model

Claudony uses separate persistence units for its own session data and for the Qhorus
message store (named `qhorus` datasource). No ledger tables are owned here — ledger
entries are written via the ledger SPI.

See `docs/DESIGN.md` for the entity model and datasource configuration.
```

- [ ] **Step 4: Apply rubric — Terminal Streaming, Authentication, MCP Transport**

Each section likely has implementation class names or internal type names. Apply the rubric: keep the conceptual description (what it does, what protocol it uses), remove class names and implementation detail, add `See docs/DESIGN.md`.

- [ ] **Step 5: Scan remaining, verify, commit**

```bash
grep -n '`[A-Z][a-zA-Z]\+`' ~/claude/casehub/parent/docs/repos/claudony.md
grep -oE '`[A-Z][a-zA-Z]+`' ~/claude/casehub/parent/docs/repos/claudony.md | wc -l
git -C ~/claude/casehub/parent add docs/repos/claudony.md
git -C ~/claude/casehub/parent commit -m "docs(audit-4): trim claudony to family-awareness level — Refs #31"
```

---

## Task 7: Trim `casehub-clinical.md` (10 class-refs)

**Files:**
- Modify: `~/claude/casehub/parent/docs/repos/casehub-clinical.md`

Low violation count — likely confined to What It Owns or Tutorial Layers sections.

- [ ] **Step 1: Read and scan**

```bash
cat ~/claude/casehub/parent/docs/repos/casehub-clinical.md
grep -n '`[A-Z][a-zA-Z]\+`' ~/claude/casehub/parent/docs/repos/casehub-clinical.md
```

- [ ] **Step 2: Apply rubric to each hit**

For each class-name reference: if it's a domain concept used abstractly — keep. If it's a specific class, SPI implementation, or entity name — replace with prose + `See docs/DESIGN.md`.

- [ ] **Step 3: Verify and commit**

```bash
grep -oE '`[A-Z][a-zA-Z]+`' ~/claude/casehub/parent/docs/repos/casehub-clinical.md | wc -l
git -C ~/claude/casehub/parent add docs/repos/casehub-clinical.md
git -C ~/claude/casehub/parent commit -m "docs(audit-4): trim casehub-clinical to family-awareness level — Refs #31"
```

---

## Task 8: Trim `casehub-aml.md` (5 class-refs)

**Files:**
- Modify: `~/claude/casehub/parent/docs/repos/casehub-aml.md`

- [ ] **Step 1: Read and scan**

```bash
cat ~/claude/casehub/parent/docs/repos/casehub-aml.md
grep -n '`[A-Z][a-zA-Z]\+`' ~/claude/casehub/parent/docs/repos/casehub-aml.md
```

- [ ] **Step 2: Apply rubric to each hit and commit**

Apply same process as Task 7. Then:

```bash
grep -oE '`[A-Z][a-zA-Z]+`' ~/claude/casehub/parent/docs/repos/casehub-aml.md | wc -l
git -C ~/claude/casehub/parent add docs/repos/casehub-aml.md
git -C ~/claude/casehub/parent commit -m "docs(audit-4): trim casehub-aml to family-awareness level — Refs #31"
```

---

## Task 9: Trim `casehub-devtown.md` (3 class-refs)

**Files:**
- Modify: `~/claude/casehub/parent/docs/repos/casehub-devtown.md`

- [ ] **Step 1: Read and scan**

```bash
cat ~/claude/casehub/parent/docs/repos/casehub-devtown.md
grep -n '`[A-Z][a-zA-Z]\+`' ~/claude/casehub/parent/docs/repos/casehub-devtown.md
```

- [ ] **Step 2: Apply rubric to each hit and commit**

```bash
grep -oE '`[A-Z][a-zA-Z]+`' ~/claude/casehub/parent/docs/repos/casehub-devtown.md | wc -l
git -C ~/claude/casehub/parent add docs/repos/casehub-devtown.md
git -C ~/claude/casehub/parent commit -m "docs(audit-4): trim casehub-devtown to family-awareness level — Refs #31"
```

---

## Task 10: Trim `casehub-connectors.md` (2 class-refs)

**Files:**
- Modify: `~/claude/casehub/parent/docs/repos/casehub-connectors.md`

- [ ] **Step 1: Read and scan**

```bash
cat ~/claude/casehub/parent/docs/repos/casehub-connectors.md
grep -n '`[A-Z][a-zA-Z]\+`' ~/claude/casehub/parent/docs/repos/casehub-connectors.md
```

- [ ] **Step 2: Apply rubric to each hit and commit**

```bash
grep -oE '`[A-Z][a-zA-Z]+`' ~/claude/casehub/parent/docs/repos/casehub-connectors.md | wc -l
git -C ~/claude/casehub/parent add docs/repos/casehub-connectors.md
git -C ~/claude/casehub/parent commit -m "docs(audit-4): trim casehub-connectors to family-awareness level — Refs #31"
```

---

## Task 11: Protocol/garden scan and issue close

**Files:** None modified — this is a review pass over removed content.

- [ ] **Step 1: Universal pattern check**

Review the content removed across Tasks 2–10. Ask for each trimmed block: does this encode a universal architectural pattern that any similar project would benefit from knowing?

Candidates to consider:
- The three-tier module structure (Tier 1 pure-Java SPI / Tier 2 CDI core / Tier 3 full runtime) — already in `protocols/universal/module-tier-structure.md`; check if the garden entry is richer
- The Store SPI pattern (domain model + pluggable persistence + in-memory test impl) — likely universal to any Quarkus multi-module project
- The dual blocking/reactive SPI variant rule — may be universal Quarkus guidance

For each genuine universal pattern: submit via forage CAPTURE to the `jvm/` garden domain.

- [ ] **Step 2: Reformulation candidates for Audit 5**

Review the protocols referenced in the trimmed files. Apply the reformulation test to any casehub-scoped protocols:
> Strip casehub-specific names. Is the result still true and useful for another project?

Flag any that pass the test with a comment on spec#14 for Audit 5 follow-up.

- [ ] **Step 3: Close issue**

```bash
gh issue close 31 --repo casehubio/parent --comment "Audit 4 complete. All 9 repos/ files trimmed to family-awareness level. DESIGN.md stubs created for connectors, devtown, aml, clinical. Protocol/garden scan done — candidates flagged for Audit 5 in Hortora/spec#14."
```

---

## Self-Review

**Spec coverage:**
- ✅ Depth rubric defined: File Map + rubric section
- ✅ DESIGN.md stubs: Task 1
- ✅ 9 files trimmed in violation order: Tasks 2–10
- ✅ Protocol/garden scan as separate final step: Task 11
- ✅ Acceptance criteria: issue close in Task 11

**Placeholder scan:** All tasks show specific grep commands, specific replacement prose, specific commit messages. Tasks 7–10 are intentionally brief because the violation count is low and the rubric is fully established by Task 6. No TBDs.

**Consistency:** All commit messages follow `docs(audit-4): trim <repo> to family-awareness level — Refs #31`. All verification commands use the same grep pattern. All DESIGN.md stubs use the same java template.
