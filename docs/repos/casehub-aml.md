# casehub-aml

**GitHub:** [casehubio/aml](https://github.com/casehubio/aml)
**Tier:** Application
**Status:** In progress — Layers 1, 2, and 3 complete; Layers 4–7 pending

## What It Is

An AML investigation application built on the CaseHub agentic harness. Coordinates specialist agents (entity resolution, pattern analysis, OSINT screening), compliance officer human task gates, and adaptive investigation paths — producing a FinCEN-compliant, independently verifiable audit trail. Field showcase and tutorial for Java developers in financial services.

Scored 44/50 in the use-case analysis (22 market + 22 community) — the only use case strong on both dimensions simultaneously. Java dominates banking infrastructure; enterprise developers have built these systems and know what fails in practice.

See `docs/use-case-analysis.md` §8.2 and `docs/tutorial-strategy.md` §6 in this repo.

## Tutorial Layers

The tutorial structure emerges from the natural adoption sequence — each layer adds one foundation module and makes its value tangible. The code at every layer is production-grade. See `docs/tutorial-strategy.md §6` for teaching objectives per layer.

| Layer | Adds | Gap it closes | Status |
|-------|------|---------------|--------|
| 1 | Naive Java — no CaseHub | Baseline anti-pattern | ✅ complete |
| 2 | casehub-work | No formal SLA or human task lifecycle for compliance officer review | ✅ complete |
| 3 | casehub-qhorus | No formal obligation per specialist agent interaction | ✅ complete (2026-05-17) |
| 4 | casehub-ledger | No tamper-evident FinCEN audit trail | pending |
| 5 | casehub-engine | Fixed investigation pipeline; no adaptive paths | pending (blocked: engine P1.3) |
| 6 | Trust routing | No trust model; random agent selection | pending (blocked: engine P1.3) |
| 7 | Comparison vs IBM AMLSim | — | pending |

## What It Owns

- AML domain model: `SuspiciousTransaction`, `AmlInvestigationCase`, `SuspiciousActivityReport`
- Capability tags: `entity-resolution`, `pattern-analysis`, `osint-screening`, `sar-drafting`, `compliance-review`, `senior-escalation`, `investigation-triage`
- Trust dimensions: `investigation-accuracy`, `pep-clearance`, `scope-awareness`
- Investigation `CasePlanModel` — adaptive paths based on entity type, risk score, PEP detection
- Compliance officer WorkItem with 30-day FinCEN SLA and head-of-compliance escalation
- 7-layer tutorial from naive Java through full adaptive case management
- Comparison baseline vs IBM AMLSim and industry whitepapers

## The Compliance Gap It Closes

Current agentic AML systems cannot provide:
- Auditable evidence chains (FinCEN requirement) — `causedByEntryId` chain per agent finding
- Formal obligation per investigation task — COMMAND creates Commitment, DECLINE ≠ FAILED
- GDPR Art.17 erasure on transaction PII — `LedgerErasureService`
- Tamper-evident investigation record — Merkle inclusion proofs, independently verifiable
- Trust-weighted routing — experienced analysts on complex cases, auto-updated from SAR outcomes

## Dependencies

```
casehub-aml
  → casehub-engine   (investigation CasePlanModel, adaptive paths)
  → casehub-ledger   (Merkle audit, FinCEN evidence chain, GDPR erasure, trust scoring)
  → casehub-work     (compliance officer WorkItem, 30-day SLA, escalation)
  → casehub-qhorus   (COMMAND/RESPONSE per specialist agent, commitment lifecycle)
  → casehub-connectors (Slack/Teams for SAR assignment notifications)
```

## Key Epics

1. Project scaffold
2. Domain model — AML entities and capability tags
3. Investigation CasePlanModel — adaptive paths
4. Compliance officer WorkItem — 30-day FinCEN SLA
5. Failure handling — DECLINED vs FAILED routing
6. Trust-weighted routing and post-investigation feedback
7. GDPR and regulatory audit
8. LLM supervisor mode — investigation triage
9. Tutorial layers 1–7 (comparison showcase)
10. Operational tooling — MCP tools and observability

Issues: https://github.com/casehubio/aml/issues?label=epic
