# Sandbox & Runtime Orchestrator Solutions

## Context

This document captures findings from surveying existing sandbox and orchestration solutions for AI agents. The goal is to leverage existing tools rather than building from scratch, aligned with Dev Lab philosophy: "leverage, don't rebuild."

**Related:** [Architecture Backbone](./20251224-architecture-backbone.md) | [MCP Ecosystem Survey](./20251226-architecture-mcp-ecosystem-survey.md)

---

## Key Finding: Don't Build From Scratch

Multiple production-ready solutions already exist for running Claude Code in isolated environments. The "Runtime Orchestrator" concept from the architecture backbone can be implemented as a thin wrapper around these existing tools.

---

## Solution Comparison

| Solution | Sandbox Type | Display | MCP Ready | Self-Host |
|----------|--------------|---------|-----------|-----------|
| **claude-code-sandbox** | Docker | No | No | Yes |
| **AIO Sandbox** | Docker | VNC | Yes | Yes |
| **Docker Official Sandbox** | Docker | No | No | Yes |

---

## Recommended Solutions

### 1. [claude-code-sandbox](https://github.com/textcortex/claude-code-sandbox)

**What it does:** Runs Claude Code in Docker containers with web UI monitoring.

| Feature | Description |
|---------|-------------|
| Docker isolation per session | Sandbox per task |
| Auto-creates git branch | Conflict handling via Git |
| Web terminal at localhost:3456 | Human can watch agent |
| Auto-forwards credentials | GitHub, Claude API |
| Commit review + diff display | Review before push |
| Podman support | Alternative to Docker |

**Gap:** No display server for browser visual access.

---

### 2. [AIO Sandbox](https://github.com/agent-infra/sandbox)

**What it does:** All-in-one container with Browser + VNC + VSCode + MCP servers.

| Feature | Description |
|---------|-------------|
| VNC access | Display server for visual browser |
| VSCode Server | IDE in sandbox |
| Pre-configured MCP servers | Browser, file, shell MCPs |
| Chrome DevTools Protocol | Programmatic browser control |

**Tested:** See [Sandbox Testing](./20251228-architecture-sandbox-testing.md)

---

### 3. [Docker Official Sandbox](https://docs.docker.com/ai/sandboxes/claude-code/)

**What it does:** Docker's official Claude Code sandbox support.

| Feature | Description |
|---------|-------------|
| Pre-installed tools | Git, Node.js, Python, Docker CLI, GitHub CLI, ripgrep, jq |
| State persistence | Reuses container, maintains installed packages across sessions |
| Credential management | Automatic credential handling |
| Simple invocation | `docker sandbox run claude` |

**Usage:**
```bash
docker sandbox run claude
```

---

## Not Considering Alternatives

Cloud-based solutions deferred due to current constraints (no cloud sandbox/browser).

### [E2B](https://e2b.dev/)

Cloud sandboxes with Firecracker microVMs. 200ms cold start, 24-hour sessions, stronger isolation than Docker. Self-host option available.

**Future consideration:** When scaling to parallel agents or overnight runs.

### [Claude-Flow](https://github.com/ruvnet/claude-flow)

Multi-agent orchestration platform with swarm intelligence, 64 pre-built agents, memory system.

**Future consideration:** When moving beyond human-led orchestration to automated multi-agent workflows.

### [Cloudflare Sandbox](https://developers.cloudflare.com/sandbox/tutorials/claude-code/)

Run Claude Code on Cloudflare Workers. API-based task submission, serverless.

**Future consideration:** Quick experiments, serverless preference.

---

## Visual Access Solutions

### The Problem

Docker containers typically run headless. Agents can interact with DOM via Playwright but can't capture screenshots or understand visual layout without a display server.

### Agent UI Access Options

**Display server options** (enables screenshot capture):
- **Xvfb** - Virtual framebuffer, lightweight, no actual display
- **VNC server** - Virtual display + remote access protocol
- **X11** - Full display server, requires host X server

**Agent interaction options**:
- **Playwright MCP** - DOM/accessibility tree interaction
- **Screenshots + vision model** - Visual understanding via image analysis
- **Chrome DevTools Protocol (CDP)** - Programmatic browser control
- **Computer Use API** - Anthropic's vision-based browser control
- **Claude in Chrome** - Browser extension with direct page access

---

## Infrastructure Requirements

What Dev Lab sandbox needs to provide:

### Core Requirements

- **Isolation** - Agent runs in isolated environment (container or VM)
- **Display server** - For browser rendering and screenshot capture
- **Browser** - Chromium/Firefox for UI interaction
- **Terminal** - Shell access for agent commands
- **Git** - Version control for code changes
- **Network** - Access to external URLs, APIs, MCP servers

### Agent Tool Requirements

- **Playwright/CDP** - Browser automation and interaction
- **MCP servers** - Linear, GitHub, documentation tools
- **Claude Code** - The agent runtime itself

### Orchestrator Requirements

- **Provisioning** - Spin up sandbox on demand
- **Repo cloning** - Clone target repo into sandbox
- **Credential injection** - API keys, tokens securely passed
- **Cleanup** - Destroy sandbox after task completion

### Human Visibility (Nice to Have)

- **VNC/noVNC** - Watch agent's browser in real-time
- **Web terminal** - Observe agent's commands
- **Diff review** - See changes before push

---

## References

**Recommended Solutions:**
- [claude-code-sandbox](https://github.com/textcortex/claude-code-sandbox)
- [AIO Sandbox](https://github.com/agent-infra/sandbox)
- [Docker Official Sandbox](https://docs.docker.com/ai/sandboxes/claude-code/)

**Deferred Solutions:**
- [E2B](https://e2b.dev/)
- [Claude-Flow](https://github.com/ruvnet/claude-flow)
- [Cloudflare Sandbox](https://developers.cloudflare.com/sandbox/tutorials/claude-code/)

**Provisioning Approaches:**
- [Running Claude Code in DevContainers](https://www.solberg.is/claude-devcontainer) - DevContainer approach with Docker Compose
- [Container Use by Dagger](https://www.infoq.com/news/2025/08/container-use/) - Git worktree + container isolation for parallel agents

**Background:**
- [Anthropic: Claude Code Sandboxing](https://www.anthropic.com/engineering/claude-code-sandboxing)
- [E2B: Run Claude Code in Sandbox](https://e2b.dev/blog/python-guide-run-claude-code-in-an-e2b-sandbox)
