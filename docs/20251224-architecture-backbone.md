# Architecture Backbone

## Context

This document captures the architectural discussion on 2024-12-24, focused on establishing the backbone before diving into implementation artifacts (schemas, prototypes).

Previous work: [Pilot PoC Summary](./20251223-previous%20work-pilot%20poc%20summary.md) | [Concepts](./20251223-concepts-devlab.md) | [Critique](./20251223-previous%20work-valid%20critique.md)

---

## Clarifications Made

### Two Orchestrators (Terminology)

| Term | What | Who |
|------|------|-----|
| **Human Orchestrator** | Decides *what* runs, *when*, with *what context* | You |
| **Runtime Orchestrator** | Executes those decisions - spawns agents, provisions environment, monitors | Code (kernel) |

These are complementary layers, not conflicts. "Human-Led Orchestration" constraint means you make decisions; Runtime Orchestrator executes them.

### CLI vs SDK is Implementation, Not Architecture

Both wrap the same thing: Claude + computer environment. SDK is designed to be embedded in scripts. The architectural decision is about **contracts and boundaries**, not which interface to use.

If contracts are solid, swapping SDK ↔ CLI is a refactor, not a redesign.

---

## Core Architecture

### The Principle

**Environment over Model** - Runtime Orchestrator's job is provisioning the environment that makes agents effective.

### What Provisioning Means

```
Runtime Orchestrator
    ├── 1. Sandbox     → Isolated filesystem (git clone → fresh dir)
    ├── 2. Context     → Codebase awareness (summary file, relevant docs)
    ├── 3. Tools       → MCP servers + installed utilities + permissions
    ├── 4. Memory      → Learned conventions, past failures
    └── 5. Spawn agent → cwd = sandbox, config = above
```

Agent wakes up inside this environment. It doesn't know how it got there - it just operates.

### Lifecycle Differences

| Component | Lifecycle | Notes |
|-----------|-----------|-------|
| Sandbox | Per-task | Created fresh, destroyed after |
| Context | Per-repo or per-task | Could be pre-computed |
| Tools | Per-agent-type | Dev vs QA have different tools |
| Memory | Per-repo | Accumulates over time |

### Conflict Resolution

Multiple agents (QA, dev, 10 devs) each get isolated sandboxes. Conflicts are **not** handled at sandbox level - they're outsourced to Git/GitHub at merge time. This aligns with philosophy: agents work like humans, leverage existing ecosystem.

---

## Implementation Path

<!-- ### Phase 1: Local Directories (Start Here)

```bash
mkdir -p /sandboxes/task-123
git clone <repo> /sandboxes/task-123/repo
cp context.md memory.md /sandboxes/task-123/repo/
cd /sandboxes/task-123/repo && claude --config mcp.json
```

- Fast iteration, no infra overhead
- No true isolation (acceptable for human-supervised runs) -->
Phase 1 is skipped because the pilot poc already doing that.

### Phase 2: Docker (Current project focus)

```dockerfile
FROM python:3.11
RUN pip install claude-code
COPY context.md memory.md /workspace/
WORKDIR /workspace
```

- True isolation, reproducible environments
- Image management overhead

### Phase 3: K8s/Nomad (Defer)

Only needed when:
- Parallelization is required
- "Human-led" constraint is removed
- Multi-agent concurrency is real

---

## Architecture Considerations

Survey findings (2024-12-26):
- [MCP Ecosystem Survey](./20251226-architecture-mcp-ecosystem-survey.md)
- [Sandbox Solutions](./20251226-architecture-sandbox-solutions.md)

### 1. Task Hierarchy Source of Truth

See [Task Hierarchy Architecture](./20251224-architecture-task%20hierarchy.md) for exploration.

---

### 2. Browser/UI Interaction

**Problem:** How do agents interact with running applications?

See [MCP Ecosystem Survey](./20251226-architecture-mcp-ecosystem-survey.md) for options explored (Playwright MCP, VNC containers, Browserbase).

**To decide:** Final approach for each phase.

---

### 3. Tool Ecosystem Survey

**Problem:** What existing tools can we leverage before building custom?

**Finding:** [Docker MCP Catalog](https://hub.docker.com/mcp) has 270+ verified servers. Starting point identified.

See [MCP Ecosystem Survey](./20251226-architecture-mcp-ecosystem-survey.md) for initial findings.

**Still needed:** Evaluate specific tools for each Dev Lab need.

---

### 4. Runtime Orchestrator Implementation

**Problem:** How to implement the Runtime Orchestrator?

**Finding:** Existing tools available. See [Sandbox Solutions](./20251226-architecture-sandbox-solutions.md) for survey of:
- claude-code-sandbox
- AIO Sandbox
- E2B
- Claude-Flow

**To decide:** Which tool(s) to adopt, what thin wrapper to build.

---

## Open Questions

1. Should Runtime Orchestrator be repo-specific or a general-purpose tool?
2. How does human orchestrator communicate intent to runtime orchestrator? (CLI flags, config files, GUI?)
3. When does "human-led" constraint relax? What triggers the evolution to automated orchestration?

---

## Summary

The backbone is:

```
Human Orchestrator (you)
         ↓ intent
Runtime Orchestrator (kernel)
         ↓ provisions environment (sandbox + context + tools + memory)
Agent (black box)
         ↓ operates, produces output
Runtime Orchestrator
         ↓ post-checks, captures results
Human Orchestrator
         ↓ reviews, decides next
```

This is simple, aligns with philosophy, and allows incremental evolution.
