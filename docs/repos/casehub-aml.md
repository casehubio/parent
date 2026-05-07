# casehub-aml

**GitHub:** [casehubio/aml](https://github.com/casehubio/aml)
**Tier:** Application
**Status:** Greenfield — no code yet, epics defined

## What It Is

The Anti-Money Laundering investigation application built on the CaseHub foundation. Primary community tutorial for Java/Quarkus developers — demonstrates all platform capabilities in a domain every Java enterprise developer recognises.

Scored 44/50 in the use-case analysis (22 market + 22 community) — the only use case strong on both dimensions simultaneously. Java dominates banking infrastructure; enterprise developers have built these systems and know what fails in practice.

See `docs/use-case-analysis.md` §8.2 and `docs/tutorial-strategy.md` §6 in this repo.

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
