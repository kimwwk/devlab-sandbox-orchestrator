# Task Hierarchy: spec-kit Fit Assessment

## Context

This document evaluates whether [spec-kit](https://github.com/spec-kit/spec-kit) can address the task hierarchy and planning challenges identified in [Task Hierarchy Architecture](./20251224-architecture-task%20hierarchy.md).

**Previous findings:**
- Human orchestrator needs hierarchy, visualization, planning tools
- Agent needs simple task access via tools
- Separate layers with adapter pattern is recommended
- Current tools (task-master, folder-based planning) have scale limitations

**Why spec-kit?**
spec-kit provides structured templates, slash commands, and workflows for specification-driven development. It could potentially solve:
- Consistent document structure (via templates)
- Agent guidance (via slash commands)
- Workflow enforcement (via constitution checks)

---

## spec-kit Overview

### Workflow

```
/speckit.constitution → Define project principles
        ↓
/speckit.specify → Create feature specification (user stories, requirements)
        ↓
/speckit.clarify → Resolve ambiguities
        ↓
/speckit.plan → Technical planning (research, data model, contracts)
        ↓
/speckit.tasks → Break down into tasks
        ↓
/speckit.implement → Execute implementation
```

### Structure

```
.specify/
├── memory/
│   └── constitution.md       # Project principles
├── templates/                 # Enforce consistent structure
│   ├── spec-template.md
│   ├── plan-template.md
│   └── tasks-template.md
└── scripts/                   # Automation

specs/
└── ###-feature-name/          # Per-feature folder
    ├── spec.md               # What to build (user stories, requirements)
    ├── plan.md               # How to build (technical plan)
    ├── research.md           # Research findings (TDD equivalent)
    ├── data-model.md
    ├── contracts/            # API contracts
    └── tasks.md              # Task list
```

---

## Comparison: spec-kit vs Your Existing Approach

### Your Current Structure

Based on the [previous project](./previous-project/our-pot/doc/):

```
doc/
├── Product-Intention.md      # Why (discovery)
├── Product-Vision.md         # Strategy
├── TDD-*.md                  # Technical decisions
├── SAD-v1-*.md               # Architecture (9 sections)
├── Feature-v1.md             # Implementation plan with tasks
├── Feature-v1.1.md           # Incremental version
├── Future-Features.md        # Explicit "out of scope"
├── references/               # Knowledge base
└── solutions/                # Lessons learned (agent memory)
```

### Direct Comparison

| Artifact           | spec-kit           | Your Approach                     | Notes                      |
|--------------------|--------------------|-----------------------------------|----------------------------|
| Principles         | constitution.md    | CLAUDE.md + Philosophy            | Similar purpose            |
| Requirements       | spec.md            | Product-Vision + Feature sections | Similar purpose            |
| Technical plan     | plan.md            | SAD sections                      | Similar purpose            |
| Research/decisions | research.md        | TDD-*.md                          | Similar purpose            |
| Data model         | data-model.md      | SAD Data Layer                    | Same                       |
| Tasks              | tasks.md           | Feature-vX.md checkboxes          | Different format           |
| Out of scope       | ❌ Missing         | Future-Features.md                | **You have, spec-kit doesn't** |
| Memory             | ❌ Missing         | solutions/                        | **You have, spec-kit doesn't** |
| Knowledge base     | ❌ Missing         | references/                       | **You have, spec-kit doesn't** |
| Version tracking   | Branch per feature | Date prefix + Feature-vX          | Different strategy         |

---

## Key Differences

### 1. Organization Philosophy

| spec-kit                             | Your Approach                  |
|--------------------------------------|--------------------------------|
| Feature-centric (specs/###-feature/) | Project-centric (doc/)         |
| One folder per feature               | One set of docs, versioned     |
| Branch per feature                   | Date prefix for temporal order |

### 2. What You Have That spec-kit Doesn't

| Pattern | Purpose | Value |
|---------|---------|-------|
| `solutions/` | Agent memory, lessons learned | Avoid repeating past mistakes |
| `references/` | Reusable knowledge | Build institutional knowledge |
| `Future-Features.md` | Explicit scope boundaries | Prevent scope creep |
| Version tracking (Feature-v1, v1.1) | Progressive refinement | Track evolution |

### 3. What spec-kit Has That You Don't

| Pattern | Purpose | Value |
|---------|---------|-------|
| Templates | Enforce consistent structure | Agents produce predictable output |
| Scripts | Automate file creation | Reduce manual overhead |
| Slash commands | Guide agent through workflow | Agent knows what to do next |
| Constitution checks | Gates in planning phase | Enforce principles early |

---

## Fit Assessment

### spec-kit Strengths for Dev Lab

- **Templates** align with "Environment over Model" - agent gets structure, not prompts
- **Slash commands** provide agent navigation (addresses open question from Task Hierarchy doc)
- **Constitution** aligns with project principles in CLAUDE.md

### spec-kit Gaps for Dev Lab

- **No memory system** - critical for agents to learn from past runs
- **No knowledge base** - agents need access to reusable references
- **No explicit scoping** - Future-Features pattern is valuable
- **Feature-centric organization** - doesn't match project-wide view
- **Missing your progressive flow** - Intent → Vision → SAD → Feature is BA workflow

---

## Related Documents

- [Task Hierarchy Architecture](./20251224-architecture-task%20hierarchy.md) - Problem definition
- [Task Hierarchy Schema](./20251224-architecture-task%20hierarchy-schema.md) - Schema exploration
- [Helpful Tools to Leverage](./20251224-helpful-tools-to-leverage.md) - Other tools analysis
- [Dev Lab Concepts](./20251223-concepts-devlab.md) - Core philosophy
