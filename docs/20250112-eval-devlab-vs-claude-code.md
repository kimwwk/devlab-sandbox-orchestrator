# Evaluation: Dev Lab vs Claude Code Built-in Capabilities

**Date:** 2025-01-12
**Purpose:** Compare Dev Lab's sandbox orchestrator against Claude Code's native agent capabilities to identify unique value and potential overlap.

---

## Executive Summary

Claude Code provides approximately **70% of basic agent isolation capabilities** out of the box. Dev Lab's unique value lies in **full container isolation, visual observability, and multi-project orchestration**.

---

## Feature Comparison Matrix

| Feature | Dev Lab | Claude Code Built-in | Notes |
|---------|---------|---------------------|-------|
| **Container Isolation** | Docker containers | OS-level sandbox (bubblewrap/Seatbelt) | Dev Lab provides stronger isolation |
| **Agent Roles** | developer, qa, reviewer | Explore, Plan, general-purpose | Both customizable |
| **Custom Agent Creation** | YAML config files | `.claude/agents/` directory | Similar approach |
| **MCP Integration** | Building custom | Already integrated | Claude Code ahead |
| **Permission System** | Building custom | Built-in with hooks | Claude Code ahead |
| **VNC/IDE Access** | Via container web UI | Not included | Dev Lab unique |
| **Multi-Repo Orchestration** | YAML-driven batch runs | Single workspace focus | Dev Lab unique |
| **Task Queuing** | Planned | Not built-in | Dev Lab unique |
| **Toolchain Images** | Pre-built node/python | Host environment | Dev Lab unique |

---

## Claude Code Native Capabilities

### Slash Commands (43+ built-in)

| Command | Purpose |
|---------|---------|
| `/sandbox` | Enable OS-level filesystem + network isolation |
| `/agents` | Manage custom AI subagents |
| `/plan` | Safe read-only code analysis mode |
| `/review` | Code review |
| `/mcp` | Manage MCP server connections |
| Custom | Create in `.claude/commands/` or `~/.claude/commands/` |

### Built-in Subagent Types

| Agent | Model | Tools | Purpose |
|-------|-------|-------|---------|
| `Explore` | Haiku (fast) | Read-only | Codebase exploration, search |
| `Plan` | Inherited | Read-only | Planning before action |
| `general-purpose` | Inherited | All | Complex multi-step tasks |
| `Bash` | - | Bash only | Terminal commands |

### Native Sandboxing (`/sandbox`)

- **Filesystem isolation** - Restricts read/write to current directory
- **Network isolation** - Domain-based proxy with permission prompts
- **OS-level enforcement** - Linux uses `bubblewrap`, macOS uses Seatbelt
- **Subprocess inheritance** - All child processes inherit restrictions

### Custom Agent Configuration

Claude Code supports custom agents via `.claude/agents/` with:

```yaml
# Example: read-only reviewer agent
name: reviewer
description: Code reviewer with read-only access
model: haiku
tools:
  - Read
  - Grep
  - Glob
permissionMode: plan  # read-only mode
```

**Available Permission Modes:**
- `default` - Standard permission checking
- `acceptEdits` - Auto-accept file edits
- `dontAsk` - Auto-deny permission prompts
- `bypassPermissions` - Skip all permission checks
- `plan` - Read-only exploration mode

---

## Dev Lab Unique Value Propositions

### 1. Full Docker Isolation

| Aspect | Claude Code Sandbox | Dev Lab Docker |
|--------|--------------------| ---------------|
| Isolation level | Process-level (bubblewrap) | Container-level |
| Escape difficulty | Moderate | High |
| Resource limits | Limited | Full cgroups control |
| Network isolation | Domain filtering | Full network namespace |

### 2. Visual Observability

Dev Lab provides web-accessible observation:

| Service | URL | Purpose |
|---------|-----|---------|
| VNC | `localhost:8888/vnc/` | Watch agent work visually |
| VSCode | `localhost:8888/code-server/` | Interactive code access |

This enables **human-in-the-loop supervision** not available in Claude Code.

### 3. Multi-Project Orchestration

```yaml
# Dev Lab: One YAML per project
name: my-project
repo: https://github.com/owner/repo.git
toolchain: node
agent: developer
task: |
  Your task description here.
```

Claude Code operates on a single workspace; Dev Lab can orchestrate across multiple repositories.

### 4. 3-Layer Provisioning Architecture

| Layer | Mechanism | What | Reusability |
|-------|-----------|------|-------------|
| 1. Build | `docker build` | Toolchain image | Cached, shared |
| 2. Start | `docker run` | Container + credentials | Per-session |
| 3. Exec | `docker exec` | Clone, setup, invoke | Per-task |

This separation enables efficient resource utilization across many tasks.

---

## Overlap Analysis

### What Dev Lab Doesn't Need to Build

These are already mature in Claude Code:

1. **Basic permission system** - Use Claude Code's built-in hooks
2. **MCP integration** - Already works, just configure servers
3. **Agent role definitions** - Use `.claude/agents/` for simple cases
4. **Code exploration** - Built-in Explore agent handles this

### What Dev Lab Should Focus On

1. **Container orchestration** - The 3-layer provisioning is unique
2. **Visual observation** - VNC/VSCode access is a differentiator
3. **Multi-repo batch processing** - Task queue management
4. **Linear integration** - Workflow tracking (per [tracking integration](./20251226-architecture-task%20hierarchy-tracking%20integration.md))

---

## Recommendations

### Short-term Strategy

1. **Leverage Claude Code's `/sandbox`** for single-workspace tasks
2. **Use Dev Lab** when you need:
   - Stronger isolation (untrusted code)
   - Visual observation
   - Multi-project orchestration
   - Custom toolchain images

### Long-term Strategy

1. **Don't rebuild what Claude Code provides** - Focus on orchestration layer
2. **Dev Lab as orchestrator** - Manage Claude Code instances in containers
3. **Integrate with Linear** - Per existing architecture decisions

---

## Decision Matrix

| Use Case | Recommended Solution |
|----------|---------------------|
| Quick code review | Claude Code `/review` |
| Exploratory analysis | Claude Code Explore agent |
| Untrusted repo analysis | Dev Lab (full isolation) |
| Batch task processing | Dev Lab (orchestration) |
| Human observation needed | Dev Lab (VNC) |
| Single workspace dev | Claude Code native |
| Multi-repo operations | Dev Lab |

---

## References

- [sandbox-solution-decisions.md](./20251229-architecture-sandbox-solution-decisions.md)
- [tracking integration.md](./20251226-architecture-task%20hierarchy-tracking%20integration.md)
- [Claude Code Sandboxing Docs](https://docs.anthropic.com/en/docs/claude-code/sandboxing)
- [Claude Code Subagents Docs](https://docs.anthropic.com/en/docs/claude-code/sub-agents)

---

*Last updated: 2025-01-12*
