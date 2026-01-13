# Operating Model: Ownership & Work Decomposition

## Context

This document defines how work flows from problem definition to executable tasks, clarifying ownership boundaries between Product/BA and Engineering.

**This is an Operating Model document** — it describes how we organize work, not how the software system is designed.

**Related Documents:**
- [Operating Model: Truth Layers](./20251230-operating-model-truth-layers.md)
- [Task Hierarchy Architecture](./20251224-architecture-task%20hierarchy.md)
- [Agent Context Requirements](./20251226-architecture-task%20hierarchy-agent%20context%20requirements.md)

---

## The Core Tension

Architecture exists before tasks — but architecture changes as we build. How does it cascade into execution without infecting the architecture with status tracking?

**The Wrong Mental Model:**
```
Design → Tasks → Coding (linear waterfall)
```

**The Correct Mental Model:**
```
Architecture is NOT a phase. It is a constraint system.
Tasks are operational slices of those constraints.
```

---

## Ownership Model

| Role | Owns | Does NOT Own |
|------|------|--------------|
| **Product/BA** | Problem, value, outcomes | Solutions, implementation, sequencing |
| **Engineering** | System transformation, architecture, tasks | Business priority, user value definition |

**Key Principle:**
- Product owns **intent** (what problem, what value)
- Engineering owns **transformation** (how system changes)

These are different disciplines with different responsibilities.

---

## What Architecture Produces

Architecture defines constraints, NOT work:

| Architecture Outputs | NOT Architecture |
|---------------------|------------------|
| Domain model | Tasks |
| Contracts | Tickets |
| Boundaries | Execution sequencing |
| Invariants | Units of work |
| Interfaces | Progress tracking |
| Data flows | |
| Risks | |
| Non-functional requirements | |

**Rule:** Architecture defines what must be true in the system — not how we'll get there.

If your architecture doc contains tasks, it's already contaminated.

---

## The Real Workflow

### Step 1: Product/BA Defines Problem & Value

**Output belongs in Product space:**
- Problem statement
- User goal / business value
- Outcome criteria
- Scope boundaries
- Assumptions and constraints
- High-level workflow

**This is NOT:**
- UI instructions
- Implementation ideas
- Database fields
- Engineering sequencing

> When BA writes solution-shaped stories, Engineering becomes a pair of hands instead of a design partner — and the system deteriorates over time.

---

### Step 2: Engineering Clarifies Feasibility & Architecture

**Before tasks exist**, Engineering performs:
- Architectural impact analysis
- Risk identification
- Dependency mapping
- Interface + boundary implications
- Spikes where uncertainty exists

**Output:** Architecture-level decisions, not tasks yet.

> If you create tasks before this step, you're committing to work you don't understand.

---

### Step 3: Tasks Created After Architecture Stabilizes

Only after architecture stabilizes → break into execution units.

Tasks must reflect:
- Constraints from architecture
- Sequencing realities
- Rollback safety
- Integration risk
- Testability

Each task references the constraint or ADR it satisfies.

---

### Step 4: Engineering Owns Re-tasking When Architecture Shifts

When architecture changes mid-build:
1. Tasks are invalidated
2. Work is paused
3. ADR is revised
4. New tasks are generated

**Product does NOT rewrite tasks.**
**BA does NOT reshuffle execution.**

Engineering owns change because engineering owns reality.

---

## The Negotiation Loop

The flow is not linear — it's a negotiation between reality and constraints:

```
┌─────────────────────────────────────────────────────────────┐
│                                                              │
│   Problem → Constraints → Architecture → Tasks               │
│      ▲                                      │                │
│      │                                      ▼                │
│      └──── Updated Constraints ◄─── Feedback                │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

When reality contradicts architecture:

| Weak System | Disciplined System |
|-------------|-------------------|
| Edits docs silently | Execution discovers constraint failure |
| Allows ad-hoc mutation | Task is paused or re-scoped |
| Lets code lead truth | New ADR proposal is created |
| | Humans review and approve |
| | Linear tasks rewritten accordingly |

---

## Task Taxonomy

Stop treating all tasks as equal. They are not.

### Type 1: Exploratory / Spike

**Purpose:** Reduce architectural uncertainty

- Validate assumptions
- Test latency / scaling
- Simulate integration behavior
- Measure failure modes

**Output:**
- Decision evidence
- Risk clarification
- Potential ADR update proposal

**No PR guaranteed. No feature promised.**

---

### Type 2: Structural Implementation

**Purpose:** Implement architectural constraints

Examples:
- Create boundary module / adapter layer
- Implement schema or contract rule
- Enforce invariant in codepath

**Definition of Done:** "Constraint X now holds true in this subsystem."

This is where architecture becomes real.

---

### Type 3: Behavioral Feature Work

**Purpose:** User-visible or capability-visible outcome

**Prerequisite:** Only happens AFTER Type 2 scaffolding exists.

> If you do feature tasks before structural tasks, you're building on sand — and rewriting later.

---

## Task Creation Rules

For every task created in Linear:

| Requirement | Purpose |
|-------------|---------|
| Declares which ADR / constraint it supports | Traceability |
| States whether Spike / Structural / Behavioral | Expectation setting |
| Includes risk / rollback plan | Safety |
| Does not restate architecture in its own words | No drift |
| If work contradicts architecture → blocks + ADR proposal | Integrity |

**A good task is NOT:** "Do thing X"

**A good task IS:** "Implement behavior X in Module Y, satisfying Constraint Z from ADR-001"

---

## ADR Linkage Requirement

Every Structural or Behavioral task **MUST** link to at least one ADR.

### Enforcement

| Task Type | ADR Linkage | Allowed Without ADR? |
|-----------|-------------|---------------------|
| Spike | Optional (exploring uncertainty) | Yes |
| Structural | **Required** | No |
| Behavioral | **Required** | No |

### Task Template (Linear)

```markdown
## Task: [Title]

### Required Fields
- **Task Type:** [Spike | Structural | Behavioral]
- **ADR References:** [MANDATORY for Structural/Behavioral]
  - ADR-001: Auth Strategy
  - ADR-005: API Design
- **Constraint Satisfied:** [Which invariant does this implement?]

### Description
[What this task accomplishes]

### Acceptance Criteria
[How we know it's done]

### Risk / Rollback
[What could go wrong, how to undo]
```

### If No ADR Applies

If a task cannot reference an existing ADR:
1. The task requires architectural review before starting
2. Create ADR proposal first
3. Get ADR approved
4. Then create task

**No ADR = No task** (for Structural/Behavioral work)

---

## Architecture Interrupt Protocol

When execution contradicts architecture, work must stop. This is not optional.

### When to Trigger

- Execution discovers constraint violation
- Reality contradicts ADR assumption
- Task cannot complete without breaking invariant
- Spike reveals architectural assumption was wrong

### The Protocol

```
┌─────────────────────────────────────────────────────────────┐
│                 ARCHITECTURE INTERRUPT                       │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  1. STOP     Do not proceed with workaround                 │
│              Do not "just make it work"                     │
│                                                              │
│  2. FLAG     Mark task: "Blocked: Architecture Conflict"    │
│              Add comment describing the conflict            │
│                                                              │
│  3. DOCUMENT Create issue describing:                       │
│              - What constraint is violated                  │
│              - What reality was discovered                  │
│              - Why current ADR doesn't work                 │
│                                                              │
│  4. PROPOSE  Draft new ADR or ADR revision                  │
│              Link to blocking issue                         │
│                                                              │
│  5. WAIT     Human must approve architecture change         │
│              No autonomous agent authorization              │
│                                                              │
│  6. RE-TASK  Generate new tasks from updated constraints    │
│              Close/invalidate old tasks                     │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### What Is NOT Allowed

| Forbidden Action | Why |
|------------------|-----|
| Silently working around constraint | Creates hidden debt |
| Editing existing ADR in place | Destroys history |
| Proceeding without resolution | Accumulates drift |
| Agent authorizing its own architecture change | No self-approval |
| "We'll fix it later" | Later never comes |

### Agent-Specific Rules

Agents (AI or automation) encountering architecture conflicts:

1. **Must halt** the current task
2. **Must report** the conflict in Linear
3. **Must not** attempt creative workarounds
4. **Must not** modify ADRs
5. **Must wait** for human decision

### Escalation

If blocked for extended period:
- Escalate to architecture owner
- Document in daily standup / async update
- Consider whether the ADR needs urgent revision

---

## The Decomposition Hierarchy

### Feature (Architecture-Level Intent) — Repo

- Describes behavior, constraints, tradeoffs
- Defines what must be true system-wide
- Includes risks, failure scenarios, boundary rules
- Durable, version-controlled
- **No acceptance checklists. No progress markers.**

### Epic / Capability — Linear

- Represents execution scope for cohesive behavior
- Links to architectural source doc
- Time-bound and team-owned
- **This is the bridge layer**

### User Story — Linear

- Describes externally meaningful outcome
- Expressed in terms of behavior, not implementation
- Acceptance criteria aligned to constraints
- **Stories reference architecture, they don't restate it**

### Task — Linear

- Smallest atomic unit of work
- Describes implementation step
- Explicitly states which architectural rule it satisfies
- **Tasks are execution-atomized reality**

---

## Where Business Analysis Fits

BA workflow is upstream, not task-level:

```
BA → clarifies value, users, workflows, outcomes
        ↓
Architecture → turns that into system constraints
        ↓
Execution → turns constraints into change steps
```

| Layer | Responsibility |
|-------|---------------|
| BA | WHY we build (value, users) |
| Architecture | HOW system must behave (constraints) |
| Tasks | WHAT we change right now (execution) |

**Stop letting these layers bleed together.**

---

## Common Failure Modes

### Failure 1: "Feature → Stories → Tasks" Pipeline

This is a project-management fantasy. Real systems are not tidy.

### Failure 2: BA Creates Solution-Shaped Stories

When BA writes solutions, Engineering becomes hands, not partners.

### Failure 3: Tasks Created Before Architecture Stabilizes

Committing to work you don't understand = project blowup.

### Failure 4: Architecture Docs Contain Tasks

The doc is now a project board. Drift is inevitable.

### Failure 5: No Re-tasking Protocol

When architecture changes, old tasks become lies.

---

## The Discipline Checklist

### Before Creating Any Task:

- [ ] Problem/value defined by Product/BA (not solutions)
- [ ] Engineering performed architectural analysis
- [ ] Architecture constraints documented in ADRs
- [ ] Uncertainty reduced via spikes if needed
- [ ] Task maps to specific constraint or ADR

### When Architecture Changes Mid-Build:

- [ ] Affected tasks identified and paused
- [ ] ADR revision proposed
- [ ] Humans review and approve change
- [ ] New tasks generated from updated constraints
- [ ] Old tasks closed/invalidated

---

## Summary

| Question | Answer |
|----------|--------|
| Who defines what to build? | Product/BA (problem & value) |
| Who defines how to build? | Engineering (architecture & tasks) |
| When are tasks created? | After architecture stabilizes |
| What do tasks reference? | Constraints/ADRs, not feature text |
| Who owns re-tasking? | Engineering |
| Can architecture change? | Yes, through explicit ADR revision |

---

*Last updated: 2025-12-30*
