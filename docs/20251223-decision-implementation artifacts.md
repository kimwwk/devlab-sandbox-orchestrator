# Implementation Artifacts

## Context

This document captures implementation decisions to be built after the backbone architecture is complete.

**Related:** [Architecture Backbone](./20251224-architecture-backbone.md) | [Valid Critique](./20251223-previous%20work-valid%20critique.md) | [Pilot PoC Summary](./20251223-previous%20work-pilot%20poc%20summary.md)

---

## Summary of Discussion

### Decided

1. **Orchestrator as Kernel, Not Boss Agent**
The Orchestrator allocates resources, provisions environments, and handles I/O—it does not perform tasks or make domain decisions.

2. **Standardized Task Object as Input Contract**
All triggers (CLI, webhooks, schedules) normalize into a single JSON/YAML schema before reaching the Orchestrator.

3. **Agents Are Stateless Regarding Workflow**
Agents do not call other agents. They exit with a status. The Orchestrator handles all routing and transitions.

4. **Flight Plans for Workflow Logic**
Multi-step workflows are defined as declarative YAML configs, not hardcoded in the Orchestrator. The Orchestrator executes them as a state machine.

5. **Output Manifest as Handoff Contract**
Every agent produces a structured output (status, artifacts, context for next step) that the Orchestrator uses to hydrate subsequent agents.

6. **Two-Layer Architecture (For Now)**
Start with Trigger → Runner. Defer the Event Bus layer until multiple concurrent triggers create a real need.

7. **Copy-on-Write Snapshot for Environment Provisioning**
Maintain a "golden" local clone; create lightweight copies for each sandbox. Discard on corruption.

---

### Near Targets

1. **Design the Output Manifest Schema**
Define the exact JSON structure agents must produce upon completion.

2. **Design a Minimal Task Object Schema**
Start with only essential fields (task_id, repo, instruction, agent). Extend on demand.

3. **Prototype a Flight Plan Executor**
Build a simple loop that reads a YAML flight plan and advances through steps based on agent exit status.

4. **Define the "Peripheral Observation" Utility**
A non-agent step type that polls external systems (e.g., GitHub check status) and returns pass/fail.

---

### Deferred

1. **Event Bus / Router Layer**
Only add when multiple triggers compete for resources or when async coordination becomes complex.

2. **Context/RAG System Design**
How to determine relevance, when to load context, embedding strategies—requires dedicated session.

3. **Agent Manifest (Declarative Agent Configs)**
Useful for pluggable agents but not needed until agent count grows beyond 2-3.

4. **Embassy Adapters for External Systems**
Two-way translators for external platforms. Not needed while "Peripheral Observation" (read-only polling) suffices.

5. **Black Box Agent Interface**
Standard for integrating third-party or teammate agents. Defer until collaboration scenarios arise.

6. **State Persistence Strategy (SQLite vs. File)**
Current file-based session manager is sufficient. Revisit when multi-agent concurrency demands querying task states.