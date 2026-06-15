# casehub-ops — Platform Deep Dive

**GitHub:** [casehubio/casehub-ops](https://github.com/casehubio/casehub-ops)
**Tier:** Integration (Research project + reference architecture)
**Status:** Active — `infra` module PoC complete (casehub-ops#1); `deployment`, `compliance`, `iot` modules planned

---

## Purpose

Domain implementations of `casehub-desiredstate` SPIs for CaseHub-specific deployment concerns. Bridges the generic desired-state runtime (`casehub-desiredstate`) to concrete CaseHub operational goals — agent deployment, stream topology, channel configuration, IoT desired state, compliance posture, and infrastructure provisioning.

`casehub-desiredstate` stays domain-agnostic; `casehub-ops` is the CaseHub domain layer above it. Research project and reference architecture.

---

## Module Structure

| Module | Purpose |
|--------|---------|
| `api` | SPIs for CaseHub-specific desired state: `GoalCompiler`, `NodeProvisioner`, `ActualStateAdapter`, `FaultPolicy`, `EventSource` implementations keyed to CaseHub domain concepts |
| `infra` | Terraform/Ansible augmentation PoC — `InfraNodeSpec` sealed hierarchy, `InfraBackend` SPI, `StandaloneBackend`, `InfraGoalCompiler`, `InMemoryResourceProvisioner`. Three operating modes: standalone, Terraform augmentation, Ansible augmentation |
| `deployment` | `DeploymentGoalCompiler` — processes `casehub-deployment.yaml` goal declaration into a `DesiredStateGraph`; sub-compilers for agents, streams, channels, detection, trust |
| `compliance` | SOC2/GDPR/EU-AI-Act/DORA posture compliance desired-state |
| `iot` | IoT desired state (coordinates with `casehub-iot`) |

---

## Infra Module PoC (casehub-ops#1)

`InfraNodeSpec` sealed hierarchy: `StandaloneNodeSpec`, `TerraformNodeSpec`, `AnsibleNodeSpec` — each representing one operating mode.

`InfraBackend` SPI — provision/deprovision infrastructure nodes. Implementations: `StandaloneBackend` (in-memory, test-friendly), `TerraformBackend` (planned), `AnsibleBackend` (planned).

`InfraGoalCompiler` — translates `casehub-desiredstate` `GoalSpec` into an `InfraNodeSpec` hierarchy.

`InMemoryResourceProvisioner` — test-scope in-memory `NodeProvisioner` implementation. 96 tests green.

---

## Depends On

| Artifact | Module | Nature |
|---|---|---|
| `casehub-desiredstate-api` | `api`, `infra` | `GoalCompiler`, `NodeProvisioner`, `ActualStateAdapter`, `FaultPolicy`, `EventSource` SPIs |
| `casehub-desiredstate` (runtime) | `infra` | `DefaultDesiredStateGraphFactory` (test scope) |
| `casehub-platform-api` | `api` | `Path`, `Preferences`, `CurrentPrincipal` |
| `casehub-work-api` | `infra` | `WorkItem` generation for human nodes |

---

## Design Documents

- Spec: `docs/superpowers/specs/2026-06-12-infra-terraform-ansible-adapter-design.md` (in casehub-ops repo)
