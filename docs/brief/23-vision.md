# Vision — Where the Platform Is Heading

*Not a roadmap — the trajectory. What becomes possible when
current work lands.*

---

## The Shape of What's Coming

CaseHub today covers the full lifecycle from declaration to
operations. The platform already works — 28 product repos, 500+
modules, proven domain applications in AML, clinical trials, security
operations, and financial trading. What follows is not a feature
wishlist. It is the convergence of work already in progress, visible
in open issues and active branches across the ecosystem.

Three horizons structure the trajectory:

1. **Infrastructure completion** — Spring parity, YAML tooling
   maturation, simulation depth. This is work that fills gaps in an
   already-shipping platform.
2. **Emergent coordination** — Hive Mind self-organisation, Qhorus
   Mesh agent-to-agent relay, physical world convergence. This is
   work that unlocks new coordination patterns from existing
   primitives.
3. **Cognitive architecture** — structured identity, goal formation,
   emotional models, emergent behaviour synthesis. This is work in
   active development that represents where the learning loop
   ultimately leads.

Each horizon builds on the previous one. Cognitive agents need the
coordination infrastructure. Coordination needs the platform
completeness. The sequence is not arbitrary.

---

## Horizon 1 — Infrastructure Completion

### Spring Boot Parity

The platform's CDI-first (Contexts and Dependency Injection)
architecture runs on Quarkus. Spring Boot support is being extracted
systematically — engine (11 CDI modules,
18 leaked imports to resolve), ledger (53 CDI beans to extract),
work, and platform modules are all in active extraction. When
complete, every foundation module will run natively on either
framework. The customer chooses their runtime; the platform adapts.

### YAML Tooling Maturation

Three capabilities are converging to make YAML authoring
production-grade:

- **Auto-bootstrap from classpath YAML** — a CaseHub application
  starts from YAML case definitions found on the classpath. Zero
  code, zero configuration. Drop YAML files into a project, start
  the application.
- **LSP import resolution** — step definition playbooks gain
  language-server-protocol support for cross-file references,
  completions, and diagnostics in any editor.
- **IDE JSON Schema generation** — the step catalogue generates
  JSON Schema automatically, enabling validation and autocompletion
  in VS Code, IntelliJ, and any schema-aware editor.

Together, these make YAML a first-class development surface with
the same tooling depth that Java developers expect.

### Simulation Depth

The simulation framework already generates CDI decorators and runs
temporal simulations. Two extensions deepen its value:

- **SPI (Service Provider Interface) simulation strategies** —
  pluggable response resolution for scenario testing. Each SPI can
  declare how it behaves under
  simulation — deterministic, probabilistic, corpus-based, or
  custom.
- **Simulation data catalogue** — curated exemplar storage with
  pattern-based synthesis. Instead of hand-crafting test data,
  simulations draw from typed corpora that capture real-world
  distributions.

---

## Horizon 2 — Emergent Coordination

### Hive Mind — Self-Organising Agent Systems

The platform's orchestration patterns today are explicit — a
supervisor delegates, a debate structure argues, a voting protocol
converges. Hive Mind introduces implicit coordination: agents
organise themselves without central control.

Three execution models are in development:

- **Stigmergy** — indirect coordination through shared environment
  modification. Agents leave signals in the blackboard; other agents
  respond to those signals. No direct communication, no supervisor.
  The coordination pattern emerges from the environment.
- **Swarm** — self-organising agents with dynamic role emergence.
  Agents observe local conditions and adopt roles based on need.
  Leadership is fluid. Specialisation emerges from interaction, not
  from configuration.
- **Continuous evolution** — agents introspect on their own
  performance, propose improvements, implement changes through the
  DevTown code review pipeline, and deploy them through
  quality-gated CI. The platform improves itself.

The enabling infrastructure already exists — the blackboard
architecture, CBR (Case-Based Reasoning) experience matching,
composable signal routing,
and evolution conductor are all deployed. Hive Mind composes them
into emergent patterns.

### Qhorus Mesh — Agent-to-Agent Communication

Today, agent communication goes through the Qhorus communications
mesh via REST endpoints with full governance. The Mesh extension
adds local relay: LLM-to-LLM communication within a single JVM,
bypassing network serialisation while preserving every governance
guarantee — speech-act protocols, normative accountability,
watchdog monitoring.

Key extensions:

- **YAML-declared channels** — communication topology configured in
  app.yaml alongside case definitions. Channel membership, message
  routing, and governance policies declared, not coded.
- **Indirect loop detection** — cross-bridge invocation-context
  propagation prevents circular agent-to-agent calls across
  communication boundaries.
- **Message-scoped content erasure** — granular GDPR compliance at
  the individual message level, not just the conversation level.

### Physical World Convergence

Desired-state reconciliation today works on infrastructure and
software topology. Three extensions bring reconciliation to the
physical world and to the platform itself:

- **IoT desired-state** — NodeProvisioner implementations for
  physical devices. A sensor's firmware version, calibration state,
  and operational mode are declared in YAML and reconciled
  continuously. The gap between digital twins and physical reality
  closes.
- **Crossplane NodeProvisioner** — multi-cloud infrastructure
  reconciliation through Crossplane providers. One YAML graph
  targets AWS, GCP, and Azure simultaneously.
- **CaseHub-application NodeSpec** — the platform deploys instances
  of itself. A desired-state graph declares a CaseHub application
  (version, configuration, case definitions), and the platform
  provisions, configures, and health-checks it automatically.

The self-managing ops console already demonstrates this pattern:
the operations application runs the engine's case model against its
own infrastructure. Physical world convergence generalises it.

### Avatar and Voice Performance

Local inference eliminates cloud dependency for latency-sensitive
agent interactions:

- **Local LLM via MTPLX + Qwen3 32B** — on-device language model
  inference for real-time agent responses without cloud round-trips.
- **Kokoro CoreML TTS** — Apple Neural Engine text-to-speech at
  12–79x realtime. Parallel sentence synthesis with engine pooling
  for continuous speech output.
- **Embodied agent interfaces** — structured identity and voice
  profiles rendered through avatar performance systems. The agent's
  personality, as declared in YAML, drives its vocal characteristics.

---

## Horizon 3 — Cognitive Architecture

This is where the learning loop leads. When CBR experience
matching, structured identity, goal cognition, and social cognition
converge, agents move from executing instructions to exhibiting
coherent behaviour.

### Emergent Behavioural Synthesis

Crystallised behaviours emerge from the intersection of memory,
disposition, and experience:

- **Behavioural attractors** — recurring patterns in agent decision
  histories form stable behavioural modes that the agent gravitates
  toward in similar contexts.
- **Cause-effect decision graphs** — structured causal models that
  agents build from their experience, enabling predictive reasoning
  about the consequences of actions.
- **Gut-feeling probes** — fast, intuition-like assessments derived
  from compressed experience, providing rapid initial judgements
  before deliberative reasoning engages.

### Multi-Agent Inside Out Model

Sub-LLMs per cognitive domain — one for emotional appraisal, one
for memory retrieval, one for goal evaluation, one for social
reasoning — coordinated by a metacognitive executive. This is not
multi-agent orchestration (that's Horizon 2). This is internal
cognitive architecture within a single agent identity.

Key enablers:

- **Adaptive cognitive brief** — the agent's context window is
  managed by metacognitive feedback, prioritising relevant memories
  and suppressing noise.
- **Cognitive simulation scenarios** — time-collapsed multi-week
  simulation runs that develop agent personality and memory
  structure before deployment.
- **Memory seeding** — fabricated backstory ingestion and emotional
  conditioning that gives agents coherent histories consistent with
  their declared identity.

### Goal Formation

Agents that form their own goals from situational knowledge and
personality. Not goal execution (already deployed) — goal
*origination*. An agent observes a situation, evaluates it against
its values and capabilities, and proposes new goals that the
oversight system can approve, modify, or reject.

The accountability infrastructure ensures this is safe: every
proposed goal is a ledger entry, every approval is M-of-N quorum,
every execution leaves a tamper-evident trail. Autonomous goal
formation without autonomous action.

---

## What Becomes Possible

When these horizons converge, the platform enables patterns that
don't exist today:

**Self-improving domain applications.** An AML investigation system
that analyses its own false-positive rate, proposes routing signal
adjustments, tests them in simulation, and deploys the improvements
through CI — with full accountability at every step.

**Emergent specialist teams.** A clinical trial coordination system
where monitoring agents self-organise around detected safety
signals, forming ad-hoc investigation teams without supervisor
intervention, coordinated through stigmergic signals in the shared
case blackboard.

**Physically-aware enterprise automation.** An IoT deployment where
desired-state reconciliation manages software versions, device
firmware, and physical sensor calibration in one graph. Drift
detection triggers corrective cases. The digital and physical
converge.

**Cognitively coherent agent personas.** A financial trading system
where regulatory monitoring agents develop stable analytical
personalities from experience, maintain emotional models that
modulate risk assessment, and communicate through governed speech
acts with trust-weighted credibility — all declared in YAML, all
accountable.

---

## The Trajectory

![Vision Evolution](images/vision-evolution.svg)

The vision is not speculative. Every capability described here is
either in active development (open issues, active branches) or is a
direct composition of capabilities that already ship. The
platform's architecture — composable modules, shared CDI context,
structural accountability — makes each horizon a natural extension
rather than a rebuild.

The sequence matters: infrastructure completion enables emergent
coordination, which enables cognitive architecture. Each layer
inherits the accountability guarantees of the layers below. An
agent that forms its own goals does so within the same oversight,
audit, and governance framework as an agent that executes
hand-written YAML. The harness holds.
