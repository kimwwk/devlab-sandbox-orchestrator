# Task Hierarchy Architecture

## The Problem

Where do tasks, stories, epics live? How do humans and agents both access them?

---

## Two Different Needs

| Who | Needs | Why |
|-----|-------|-----|
| Human Orchestrator | Hierarchy, visualization, planning tools | To think, prioritize, manage |
| Agent | Simple task access via tool, query history | To execute, get context |

These needs are different. One solution may not serve both well.

---

## Key Insight: Separate the Layers

```
Human's tool (Jira / Linear / Notion / folder)
    ├── Source of truth
    ├── Hierarchy: Epic → Story → Task
    ├── Visualization: boards, lists, dashboards
    └── Planning: estimation, assignment, prioritization
              ↓
         Adapter (sync on-demand)
              ↓
Agent-facing format (portable schema)
              ↓
         MCP server
              ↓
Agent queries via tool:
    ├── get_current_task()
    ├── list_completed_tasks()
    ├── get_parent_story()
    └── update_status()
```

---

## Why Agent Uses Tool, Not Prompt Injection

**Not this:**
```
Runtime Orchestrator injects task into prompt → Agent executes blindly
```

**But this:**
```
Agent has task MCP → Agent queries what it needs → Agent navigates context
```

Reasons:
- Agent is a decision engine - it decides what context it needs
- Can explore mid-task if stuck
- Can check completed tasks for patterns
- Can read parent story for bigger picture
- Dynamic, not static

This already works in PoC (task-master MCP).

---

## Agent as Decision Engine vs Hierarchy

**Tension:** If agent only gets atomic tasks, does it become a mere executor?

**Resolution:** Atomic task ≠ micro-instruction.

| Violates decision engine | Respects decision engine |
|-------------------------|-------------------------|
| "Add line 42 to file X" | "Implement JWT auth" |
| Tells agent WHAT to type | Tells agent GOAL to achieve |
| No decisions needed | Agent decides HOW |

**Key insight:** Agent doesn't need to MANAGE hierarchy. But agent benefits from READING it.

```
Task: "Implement login"
Context:
  - Parent: "User management system"
  - Related: "Registration complete", "Password reset pending"
Acceptance: ...
```

Agent gets hierarchy as **context**, not as **responsibility**.

---

## Scope Boundary

| In Scope (DevLab) | Out of Scope (External Peripheral) |
|-------------------|-----------------------------------|
| Agent executes assigned task | AI creates/analyzes epics/stories |
| Agent queries task system | AI does planning/estimation |
| Agent updates status | AI breaks down work |

DevLab = execution layer. Planning/analysis can use AI, but that's a separate concern.

---

## Tool Evaluation (Hands-on)

### task-master

| Aspect | Finding |
|--------|---------|
| Focus | Execution management |
| Storage | JSON (`tasks.json`) |
| Hierarchy | Subtasks via dot notation (1.1, 1.2) |
| Agent access | MCP server |
| Problem at scale | JSON gets huge, hard to visualize |

### spec-kit

| Aspect | Finding |
|--------|---------|
| Focus | Spec-driven planning |
| Storage | Markdown files |
| Hierarchy | User stories → Phases → Tasks |
| Agent access | Slash commands |
| Problem at scale | Markdown gets huge, agents skip steps |

### Assessment

Both tools try to do planning + task management. Neither does both well at scale.

**For this project:**
- Planning = human orchestrator's job (not AI)
- Task management = needed, but existing tools have scale problems
- Decision: evaluate value of solving this vs working around it

---

## The Adapter Pattern (Still Valuable)

Core principles support this:
- "Tooling Is a Portfolio, Not a Lock-in"
- "It Is an Ecosystem"

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│    Jira     │     │   Folder    │     │   Notion    │
│   Adapter   │     │   Adapter   │     │   Adapter   │
└──────┬──────┘     └──────┬──────┘     └──────┬──────┘
       │                   │                   │
       └───────────────────┴───────────────────┘
                           ↓
              Portable Schema (standard)
                           ↓
                      MCP server
                           ↓
                        Agent
```

Human uses what they prefer. Adapter translates. Agent doesn't care about source.

---

## Existing Structure Analysis

Reviewed folder-based planning from previous project. See structure:

```
doc/
├── 20251217-Product-Intention.md      # Discovery → Why
├── 20251217-TDD-*.md                  # Analysis → Technical decisions
├── 20251218-Product-Vision.md         # Discovery → Strategy
├── 20251218-SAD-v1-*.md               # Specification → Architecture (9 sections)
├── 20251219-Feature-v1.md             # Specification → Implementation plan
├── 20251221-Feature-v1.1.md           # Iteration → Updated scope
├── 20251221-Future-Features.md        # Validation → Explicit "out of scope"
├── references/                         # Knowledge base (reusable concepts)
└── solutions/                          # Iteration → Lessons learned (agent memory)
```

**What's working:**
- Date prefixes provide temporal ordering
- Progressive refinement (Intent → Vision → SAD → Features)
- Explicit scoping (Future-Features = what's out)
- Version tracking (Feature-v1, v1.1)
- Memory system (solutions/ = avoid past mistakes)
- References for reusable knowledge
- Tasks include "Done When" + "Testing Approach" (acceptance)
- Dependencies declared between features
- SAD references linked from tasks

**What could be enhanced:**
- Status tracking (checkboxes are fragile to parse)
- Hierarchy links (implicit in sections, not explicit IDs)
- Acceptance criteria format (varies, not always Gherkin)
- Agent navigation conventions (not documented)

---

## Explorations Completed

See [Schema & Workflow Exploration](./20251224-architecture-task%20hierarchy-schema.md) for detailed analysis of:

1. **Jira Data Model** - hierarchy via parent field, workflow as state machine, custom fields
2. **User Story Format** - As a/I want/So that, INVEST criteria, MoSCoW priority
3. **Acceptance Criteria (Gherkin)** - Given/When/Then, testable scenarios
4. **spec-kit Templates** - phases, checkpoints, [P] markers, traceability
5. **Real-World BA Workflow** - discovery → analysis → specification → validation → handoff → iteration
6. **Portable Schema Proposal** - work item schema that maps to multiple tools

---

## Key Considerations

### Source of Truth Question

| Option | Description | Pro | Con |
|--------|-------------|-----|-----|
| A. Schema first | YAML/JSON source, generate markdown | Structured, parseable | Extra step, markdown stale |
| B. Markdown first | Markdown source, derive schema | Human-friendly authoring | Parsing fragile |
| C. Bidirectional | Either can be source | Flexibility | Complexity, conflicts |

**Current lean:** Option B with conventions. Markdown is natural for humans. Add structured frontmatter. Parse when needed.

### Minimal Viable Schema

| Priority | Fields |
|----------|--------|
| Must have | id, type, title, status, parent_id, done_when |
| Should have | priority, depends_on, references, description |
| Could have | acceptance_criteria (Gherkin), labels |
| Won't have (now) | story_points, time_estimates, assignee |

### Agent Status Update Options

| Approach | Mechanism | Pro | Con |
|----------|-----------|-----|-----|
| Edit checkbox | Search/replace in markdown | Simple | Fragile |
| Update frontmatter | YAML header in markdown | Structured | Less visible |
| Separate status file | status.json | Clean separation | Another file |
| MCP tool | API call | Clean interface | Needs build |
| task-master | Existing tool | Already works | Separate system |

---

## Open Questions

1. **What's the minimum schema that serves both human planning and agent execution?**

2. **Should we adopt Gherkin for all acceptance criteria, or is "Done When" sufficient?**

3. **How to handle Feature-vX.md → individual task tracking?**
   - Keep tasks in Feature-vX.md (current)?
   - Extract to separate task files?
   - Use task-master for execution, Feature-vX.md for planning?

4. **What conventions enable agents to navigate folder structure reliably?**

5. **Is the adapter pattern worth the implementation cost, or start simpler?**

---

## Next Steps

1. Define minimal schema for DevLab (based on exploration)
2. Document conventions for agent navigation (CLAUDE.md update)
3. Decide: adapter pattern now, or simpler approach first?
4. Prototype: parse existing Feature-v1.md into schema
5. Validate: does schema capture what agents need?
