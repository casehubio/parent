# YAML Walkthrough — From Agent Identity to Situation Awareness

CaseHub is an enterprise Java platform with 500+ modules. Domain experts
never see that Java. They declare intent in YAML — cases, agents,
routing, reconciliation, monitoring — and the platform handles execution,
accountability, and learning.

This walkthrough uses real YAML from the CaseHub codebase. Each section
shows a different lifecycle stage.

---

## 1. Agent Identity — Who the Agents Are

Before agents can act, they need structured identity. CaseHub uses
vocabulary-grounded descriptors — not ad-hoc prompt strings — so the
platform can reason about agent capabilities, match them to tasks, and
enforce behavioural compliance.

```yaml
# eidos agent descriptor — clinical-researcher.yaml
name: clinical-researcher
role: Clinical Researcher — Trial Protocol Specialist
domain: clinical-trials
descriptor:
  agentId: clinical-researcher-01
  provider: anthropic
  modelFamily: claude
  modelVersion: claude-opus-4-7
  slot: specialist
  jurisdiction: ICH-E6R2, EMA-GCP, FDA-21CFR-312
  capabilities:
    - name: protocol-review
      qualityHint: 0.93
      latencyHintP50Ms: 90000
      costHint: high
      inputTypes:
        - trial-protocol
        - statistical-analysis-plan
      outputTypes:
        - protocol-assessment
        - compliance-report
      epistemicDomains:
        clinical-trial-design: 0.95
        biostatistics: 0.85
        regulatory-affairs: 0.88
    - name: adverse-event-assessment
      qualityHint: 0.90
      costHint: medium
      epistemicDomains:
        pharmacovigilance: 0.92
  disposition:
    ruleFollowing:
      - term: strict
        weight: 1.0
    riskAppetite:
      - term: conservative
        weight: 1.0
    autonomy:
      - term: directed
        weight: 1.0
  briefing: >
    Every protocol deviation must be escalated immediately to the
    principal investigator. Source data verification is non-negotiable.
```

**What the platform does with this:** The descriptor feeds into trust
scoring, capability-based routing, and behavioural compliance checking.
When a task needs `protocol-review`, the platform matches agents by
epistemic domain scores, not by name. Disposition terms (`strict`,
`conservative`, `directed`) constrain how the agent operates — a
`strict` rule-following agent cannot be overridden by peer pressure in
a voting pattern.

---

## 2. Case Declaration — The Lifecycle in YAML

A case definition declares what should happen, not how. Capabilities
define the work. Bindings define when work triggers. Goals define
success. The engine handles execution, concurrency, and state.

```yaml
# case definition — care-coordination.yaml
dsl: "0.1"
version: "1.0.0"
name: care-coordination
namespace: casehub-life
title: Care coordination — assess, plan, assign, episode, review

spec:
  capabilities:
    - name: needs-assessment
      description: "Assess care needs based on the care request"
      inputSchema: "{ careRequest: .careRequest }"
      outputSchema: "{ assessment: . }"
    - name: care-plan
      description: "Produce a care schedule based on the assessment"
      inputSchema: "{ assessment: .assessment }"
      outputSchema: "{ carePlan: . }"
    - name: health-check
      description: "Analyse care notes and flag health concerns"
      inputSchema: "{ episodeResult: .episodeResult }"
      outputSchema: "{ healthCheck: . }"

  milestones:
    - name: assessment-complete
      condition: ".assessment != null"
    - name: carer-assigned
      condition: ".carerAssignment != null"

  goals:
    - name: review-complete
      kind: success
      condition: ".careReview != null"

  completion:
    success:
      allOf:
        - review-complete
```

**What the platform does with this:** The engine creates a blackboard
for case state, evaluates binding conditions on every context change,
dispatches workers to matched capabilities, tracks milestone
progression, and completes the case when all goals are satisfied.
JQ expressions evaluate against the working context layer.

---

## 3. Bindings — When Things Happen

Bindings connect events to actions. They can trigger AI capabilities,
human tasks, or sub-cases. Conditional logic is expressed in JQ — the
platform evaluates it on every state change.

```yaml
  bindings:
    # AI capability — fires when care request arrives
    - name: needs-assessment
      on: { contextChange: {} }
      when: ".careRequest != null and .assessment == null"
      capability: needs-assessment

    # Human task — household member accepts delegation
    - name: assign-carer
      on: { contextChange: {} }
      when: ".carePlan != null and .carerAssignment == null"
      humanTask:
        title: "Accept care delegation"
        expiresIn: PT24H
        candidateGroups: [household-member]
        inputMapping: "{ careRequest: .careRequest, carePlan: .carePlan }"
        outputMapping: "{ carerAssignment: . }"

    # Sub-case — spawns a child case
    - name: care-episode
      on: { contextChange: {} }
      when: ".carerAssignment != null and .episodeResult == null"
      subCase:
        namespace: casehub-life
        name: care-episode
        version: "1.0.0"
        waitForCompletion: true
        inputMapping: "{ careRequest: .careRequest, carePlan: .carePlan }"
        outputMapping: "{ episodeResult: . }"

    # Conditional escalation — only when health concern detected
    - name: escalate-concern
      on: { contextChange: {} }
      when: ".healthCheck.healthConcern == true and .escalation == null"
      humanTask:
        title: "Review health concern escalation"
        expiresIn: PT12H
        candidateGroups: [household-admin]
```

**What the platform does with this:** Three binding types in one case —
AI capability, human task, and sub-case — all using the same trigger
model. The engine evaluates `when` conditions on every context change,
dispatches the right type of work, and merges results back into the
case context. The escalation binding only fires when a health concern
is detected — adaptive behaviour declared in YAML.

---

## 4. Agentic Patterns — How Agents Collaborate

When a capability needs multiple agents, agentic patterns define the
collaboration structure. Supervisor, voting, HTN decomposition, debate
— all declared in YAML, executed on the platform.

```yaml
# agentic pattern — supervisor.yaml
type: supervisor
routing:
  type: first-match
  guard: "priority > 5"
termination:
  - type: max-iterations
    iterations: 20
aggregation:
  type: collect-all
agents:
  - type: worker
    name: analyst
    description: "Analyses input data"
    capabilities:
      - data-analysis
  - type: worker
    name: reviewer
```

```yaml
# agentic pattern — htn.yaml (hierarchical task network)
type: htn
rootTask:
  type: compound
  name: main-task
  subtasks:
    - type: primitive
      name: gather-data
      executor: data-agent
    - type: compound
      name: process
      subtasks:
        - type: primitive
          name: clean
          executor: cleaner-agent
        - type: primitive
          name: analyse
          executor: analyst-agent
```

**What the platform does with this:** The blocks module instantiates
the pattern, manages agent lifecycles, enforces termination conditions,
and aggregates results. HTN patterns decompose compound tasks into
primitives — the platform handles parallel execution on virtual threads,
dependency ordering, and failure propagation. Routing guards use the
same JQ expression language as case bindings.

---

## 5. Trust-Weighted Routing — Learning from Outcomes

Case-based reasoning (CBR) makes the platform learn. Features define
what matters. Weights control importance. Past outcomes feed future
routing decisions — which agent, which strategy, which plan.

```yaml
# CBR configuration — within a case definition
spec:
  cbr:
    features:
      careType: ".careRequest.careType"
      patientRiskLevel: ".careRequest.patientRiskLevel"
      hoursPerWeek: ".carePlan.hoursPerWeek"
    weights:
      careType: 3.0
      patientRiskLevel: 2.0
      hoursPerWeek: 1.0
    topK: 5
    minSimilarity: 0.3
    domain: casehubio/life/eldercare
    caseType: care-coordination
    timing: case-lifetime
```

**What the platform does with this:** When a new case arrives, the CBR
engine retrieves the top-K most similar past cases by weighted feature
similarity. Past outcomes — which strategies worked, which agents
performed well, which plans needed adjustment — inform the current
case. This is a proven learning loop, deployed and running, not
theoretical.

---

## 6. Deployment Topology — Infrastructure as YAML

Operations declares the deployment target. Lifecycle phases order
infrastructure provisioning. Dependencies ensure resources are created
in the right sequence. The same desired-state reconciliation engine
manages both application resources and infrastructure.

```yaml
# deployment topology — ha-multi-az-healthcare.yaml
desiredState:
  namespace: topology
  name: hospital-records

variables:
  namespace: "hospital"
  region: "us-east-1"
  replicas: "3"

imports:
  - module: ha-multi-az
    as: ha
    parameters:
      namespace: ${var.namespace}
      region: ${var.region}
      zones: "us-east-1a,us-east-1b,us-east-1c"

lifecycle:
  phases:
    - id: infrastructure
      completionCondition: allPresent
      nodes:
        hospital-ns:
          type: k8s_namespace
          spec:
            name: ${var.namespace}

    - id: data
      completionCondition: allPresent
      nodes:
        patient-db:
          type: k8s_deployment
          dependsOn: [hospital-ns]
          spec:
            namespace: ${var.namespace}
            name: patient-db
            image: postgres:16
            replicas: ${var.replicas}

    - id: application
      completionCondition: allPresent
      nodes:
        records-api:
          type: k8s_deployment
          dependsOn: [patient-db]
          spec:
            name: records-api
            image: hospital-records-api:2.1
            replicas: ${var.replicas}
```

**What the platform does with this:** The desired-state reconciliation
engine resolves variables, orders lifecycle phases by dependency,
provisions resources in parallel within each phase, and continuously
reconciles actual state against the declared target. Drift is detected
and corrected automatically. The same engine that manages cloud
resources also manages application-level desired state.

---

## 7. Desired-State Reconciliation — Declare, Detect, Correct

A desired-state plugin defines a resource type end-to-end: what the
resource looks like (spec), how to check if it exists (actual-state),
how to create or remove it (provisioner), what to do when things fail
(fault-policy), how to learn from outcomes (CBR), and when to escalate
(RAS situation awareness).

```yaml
# desired-state plugin — resource definition
plugin:
  type: cloud-resource
  version: 1
  resyncInterval: 30s

spec:
  fields:
    name:
      type: string
      required: true
    count:
      type: integer
      default: 1

actual-state:
  steps:
    - rest-call:
        method: GET
        url: "https://${auth.api.endpoint}/resources/${spec.name}"
        auth: api
        result: response
    - compare-state:
        present-when: "${result.response.status} == 200"
        drifted-when: "${result.response.body.count} < ${spec.count}"
        absent-when: "${result.response.status} == 404"

provisioner:
  provision:
    steps:
      - rest-call:
          method: PUT
          url: "https://${auth.api.endpoint}/resources/${spec.name}"
          body:
            name: "${spec.name}"
            count: ${spec.count}
  deprovision:
    steps:
      - rest-call:
          method: DELETE
          url: "https://${auth.api.endpoint}/resources/${spec.name}"

fault-policy:
  - faultTypes: [PROVISION_FAILED]
    tiers:
      - threshold: 3
        reviewNode:
          type: human-review
          humanGating: ALL

cbr:
  features:
    - name: count
      source: spec.count
      similarity: numeric
  outcome-signals:
    success: "${result.response.body.count} >= ${spec.count}"

ras:
  situations:
    - name: repeated-failures
      events: [NODE_FAULTED, NODE_RECOVERED]
      correlation-window: 10m
      chain-mode:
        streak: 3
      trigger: create-case
      trigger-mode: fire-once
```

**What the platform does with this:** One YAML file, six lifecycle
concerns. The reconciliation engine checks actual state every 30
seconds, provisions when absent, corrects when drifted, deprovisions
when removed from the declaration. After 3 consecutive failures, the
fault-policy escalates to human review. CBR learns which resource
configurations succeed. RAS detects patterns of repeated failures and
creates a case for investigation. All of this from a single declaration.

---

## 8. Agent Configuration — Model Providers

Agent configuration defines which AI providers are available, how to
authenticate, and what aliases map to which model capabilities.

```yaml
# agent config manifest — base.yaml
providers:
  - vendor: anthropic
    credential: env:ANTHROPIC_API_KEY
aliases:
  reasoning-heavy:
    tier: FLAGSHIP
    capabilities: [reasoning, code]
    min-context: 128000
defaults:
  backend: claude
```

**What the platform does with this:** Provider configuration is
separate from agent identity and case definitions. Agents reference
capability tiers (`FLAGSHIP`, `STANDARD`), not specific models. The
platform resolves the best available model at runtime based on the
alias, available providers, and cost constraints. Switching providers
is a configuration change, not a code change.

---

## The Pattern

Every section above follows the same pattern: **declare what you want
in YAML, the platform handles how**. The YAML is the contract between
domain expert and platform. Underneath:

- **500+ Java modules** handle execution, concurrency, and state
- **Merkle MMR ledger** captures every decision with tamper-evident audit
- **Bayesian trust scoring** weights agent reliability over time
- **CDI dependency injection** wires capabilities at runtime
- **Virtual threads** execute work in parallel without thread management
- **JQ expressions** evaluate conditions against case context

The domain expert writes YAML. The platform provides enterprise-grade
execution with full accountability. That is the CaseHub proposition.
