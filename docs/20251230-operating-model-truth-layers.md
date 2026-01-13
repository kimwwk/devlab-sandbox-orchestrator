# Operating Model: Truth Layers

## Context

This document defines the separation between Git Repo (System of Record) and Linear (System of Engagement) for agent-assisted development workflows.

**This is an Operating Model document** — it describes how we organize work, not how the software system is designed.

**Related Documents:**
- [Operating Model: Work Decomposition](./20251230-operating-model-work-decomposition.md)
- [Task Hierarchy Architecture](./20251224-architecture-task%20hierarchy.md)
- [Tracking Integration](./20251226-architecture-task%20hierarchy-tracking%20integration.md)
- [Agent Context Requirements](./20251226-architecture-task%20hierarchy-agent%20context%20requirements.md)
- [Dev Lab Concepts](./20251223-concepts-devlab.md)

---

## The Core Split

| System | Role | Mutability | Agent Access |
|--------|------|------------|--------------|
| **Git Repo** | System of Record (Truth) | Immutable (INSERT, not UPDATE) | Read before coding |
| **Linear** | System of Engagement (Motion) | High volatility | Read tasks, update status |

**Key Insight:** Any documentation that requires manual synchronization will eventually become a lie. The solution is clear boundaries with no overlap.

---

## The Truth Hierarchy

```
┌─────────────────────────────────────────────────────────┐
│                    TRUTH HIERARCHY                       │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  1. CODE          "How does it actually work?"           │
│     └── The ultimate truth. If code != docs, code wins   │
│                                                          │
│  2. ADRs          "Why did we decide this?"              │
│     └── Permanent rationale. Immutable ledger            │
│                                                          │
│  3. INTENT        "What problem are we solving?"         │
│     └── Static reference. Problem framing only           │
│                                                          │
│  4. LINEAR        "What's the current status?"           │
│     └── Volatile. Execution state only                   │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

---

## What Lives Where

### Git Repo (Knowledge Layer)

```
/docs
├── ARCHITECTURE_INDEX.md   # CONSTITUTION - Read first before any work
│
├── /intent          # WHY - Problem framing only, no solutions
│   ├── product-vision.md
│   ├── problem-statements/
│   └── revisions/           # Append-only intent changes
│       ├── 001-scope-reduction.md
│       └── 002-market-pivot.md
│
├── /adr             # HOW (decided) - Immutable ledger, supersession only
│   ├── 001-auth-strategy.md
│   ├── 002-database-choice.md
│   └── ...
│
├── /specs           # WHAT to build - Frozen after sync to Linear
│   └── feature-v1/
│       └── overview.md      # Goals, scope - NO tasks
│
├── /glossary        # Domain terms, shared language
│
└── /system-maps     # Architecture diagrams
```

**Rules:**
- **No status** (no checkboxes, no "Phase 1 complete")
- **No future tense** (no "we will do X")
- **Immutable** - Never edit, only supersede with new ADR
- **Agent reads, never writes** to ADRs

### Linear (Execution Layer)

| Content | Example |
|---------|---------|
| Task status | Todo → In Progress → Done |
| Assignment | Who owns this task |
| Discussion | "Should we use OAuth or JWT?" |
| Blockers | "Waiting on API spec" |
| Progress comments | "Completed auth endpoint" |
| Acceptance criteria | Checklist for "done" |

**Rules:**
- **All status lives here**
- **Agent updates status and comments**
- **Ephemeral** - Discussions may be lost after project ends

### Code Repo

| Content | Notes |
|---------|-------|
| Source code | The actual implementation |
| Tests | Executable truth |
| Local configs | .env.example, tsconfig |
| ARCHITECTURE_INDEX.md | Link to global truth |

---

## Summary Table

| Content Type | Where | Mutability | Agent Role |
|--------------|-------|------------|------------|
| Problem/Vision | Repo `/intent` | Append-only revisions | Read |
| Decisions (ADR) | Repo `/adr` | Append-only | Read |
| Feature specs | Repo `/specs` | Frozen after sync | Read |
| Architecture diagrams | Repo `/system-maps` | Versioned | Read |
| Task status | Linear | Volatile | Read + Write |
| Discussion | Linear | Ephemeral | Read + Write |
| Code | Code repo | Evolving | Write |
| Tests | Code repo | Evolving | Write |

---

## Agent Workflow

### The Critical Rule

```
┌─────────┐     ┌──────────────┐     ┌─────────────┐     ┌──────┐
│ Linear  │ ──► │ Global Truth │ ──► │ Local Truth │ ──► │ Code │
│ (Task)  │     │ (ADRs)       │     │ (Repo docs) │     │      │
└─────────┘     └──────────────┘     └─────────────┘     └──────┘
     │                                                        │
     └────────────────────────────────────────────────────────┘
                        Update status
```

**Agent MUST:**
1. Read task from Linear
2. Read constraints from ADRs (global truth)
3. Read context from repo docs
4. Write code
5. Update Linear status

**Agent MUST NOT:**
- Skip reading truth layer
- Edit ADRs
- Put status in markdown

---

## The Promotion Rule

When does Linear discussion become a permanent ADR?

| Trigger | Action |
|---------|--------|
| Decision affects >1 Linear issue | Promote to ADR |
| Changes public interface (API, schema) | Promote to ADR |
| Cross-repo impact | Promote to Global ADR |
| Single-issue scope | Stays in Linear |

**The Distillation Loop:** Upon task completion, significant decisions from Linear discussions must be distilled into Git-based ADRs. If it's not committed to the repo, the learning is lost to the ephemeral Linear log.

---

## Multi-Repo Architecture

For projects with multiple repositories, global truth must be centralized.

```
┌─────────────────────────────────────────────┐
│           architecture-repo (Global)         │
│  /docs/intent/                               │
│  /docs/adr/                                  │
│  /docs/system-maps/                          │
└─────────────────────────────────────────────┘
              ▲           ▲           ▲
              │           │           │
         references   references  references
              │           │           │
┌─────────────┴───┐ ┌─────┴─────┐ ┌───┴─────────────┐
│  frontend-repo  │ │ backend   │ │  infra-repo     │
│                 │ │           │ │                 │
│ ARCHITECTURE_   │ │ ARCHI...  │ │ ARCHI...        │
│ INDEX.md ───────┼─┼───────────┼─┼──► links to     │
│                 │ │           │ │    global truth │
└─────────────────┘ └───────────┘ └─────────────────┘
```

### ARCHITECTURE_INDEX.md Template

Each code repository should contain this entry point:

```markdown
# Architecture Index

## Global Truth
- [Architecture Repo](link-to-architecture-repo)
- [ADRs](link-to-architecture-repo/docs/adr/)
- [System Maps](link-to-architecture-repo/docs/system-maps/)

## Local Context
- [README](./README.md)
- [API Contracts](./docs/api/)

## Relevant ADRs
- [ADR-001: Auth Strategy](link) - Affects this repo
- [ADR-005: API Design](link) - Defines our contracts
```

---

## ADR Format

ADRs follow an immutable, append-only ledger pattern.

### Template

```markdown
# ADR-NNN: [Title]

## Status
[Proposed | Accepted | Superseded by ADR-XXX]

## Context
What is the issue that we're seeing that is motivating this decision?

## Decision
What is the change that we're proposing and/or doing?

## Consequences
What becomes easier or more difficult because of this decision?

## Supersession Rules
This ADR is valid as long as [condition].
If [trigger], this ADR should be superseded.
```

### Key Principles

- **Never edit** - Write new ADR that supersedes
- **Past tense** - Documents decisions made, not hopes
- **Agent-readable** - Clear, parseable structure
- **Linked** - References related ADRs and issues

---

## Intent Revisions

Intent is not truly "frozen" — reality shifts. But we don't edit intent documents. We append revisions.

### Why Revisions, Not Edits

- Preserves history of how understanding evolved
- Agents can trace why scope changed
- No silent rewrites that confuse future readers

### Revision Format

```markdown
# Intent Revision 001: [Title]

## Date
2025-01-15

## Supersedes
[Which part of which document this affects]

## Context
[What changed in reality that motivates this revision]

## Change
- Removed: [What's no longer in scope]
- Added: [What's now in scope]
- Modified: [What changed]

## Impact
- ADRs affected: [List]
- Linear tasks invalidated: [List]
```

### Folder Structure

```
/docs/intent
├── product-vision.md           # Original vision
├── problem-statements/
│   └── core-problem.md
└── revisions/                  # Append-only changes
    ├── 001-2025-01-scope-reduction.md
    ├── 002-2025-02-market-pivot.md
    └── ...
```

**Rule:** Intent is not frozen. History is.

---

## The Checkbox Problem (Resolved)

Feature docs with `- [x]` checkboxes create drift between repo and Linear.

**Resolution:**
- For existing docs: Accept checkboxes as historical (planning artifact)
- For new docs: **No checkboxes** - Linear tracks all status
- Status belongs in Linear, not in markdown

---

## Validation Checklist

### System Works If:

- [ ] Global truth lives in one architecture repo (or designated location)
- [ ] Every code repo links back via `ARCHITECTURE_INDEX.md`
- [ ] Agent is forced to read truth before coding
- [ ] Global truth overrides local truth
- [ ] New cross-repo decisions get promoted to global ADR
- [ ] No status tracking in markdown files

### System Fails If:

- [ ] Truth scattered across repos
- [ ] ADRs duplicated locally with divergent content
- [ ] Agent skips straight to code without reading constraints
- [ ] Decisions stay trapped in Linear forever
- [ ] Markdown files contain status checkboxes

---

## Mapping to Our Workflow

### Human Workflow
1. **Plan** in repo (write Intent docs, ADRs)
2. **Create tasks** in Linear (from planning docs)
3. **Monitor** in Linear (boards, status)
4. **Review** in repo (PRs, code)
5. **Promote** significant decisions to ADRs

### Agent Workflow
1. **Query** Linear (get next task via MCP)
2. **Read** ARCHITECTURE_INDEX.md (find global truth)
3. **Read** relevant ADRs (understand constraints)
4. **Read** repo context (existing code, local docs)
5. **Write** code (implementation)
6. **Update** Linear (status, comments via MCP)

---

## Key Terminology

| Term | Definition |
|------|------------|
| **System of Record** | Git repo - permanent truth layer |
| **System of Engagement** | Linear - volatile execution layer |
| **ADR** | Architecture Decision Record - immutable decision log |
| **Intent** | Problem framing documents - no solutions |
| **Global Truth** | Cross-repo architectural constraints |
| **Local Truth** | Repo-specific context and docs |
| **Promotion** | Moving Linear discussion to permanent ADR |
| **Supersession** | New ADR replacing old (never edit) |

---

*Last updated: 2025-12-30*
