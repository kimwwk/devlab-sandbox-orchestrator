# MCP Ecosystem Survey

## Context

This document captures findings from surveying the MCP (Model Context Protocol) ecosystem to address open architecture questions from [Architecture Backbone](./20251224-architecture-backbone.md).

**Questions addressed:**
1. Task Hierarchy Source of Truth - What tools have native MCP support?
2. Browser/UI Interaction - What's the right abstraction?
3. Tool Ecosystem Survey - What exists before building custom?

---

## Docker MCP Catalog Overview

**Source:** [Docker MCP Catalog](https://hub.docker.com/mcp)

The Docker MCP Catalog hosts **270+ verified MCP servers** from partners including New Relic, Stripe, Grafana, and more.

### Server Types

| Type | Description | Example |
|------|-------------|---------|
| **Local servers** | Docker-built, digitally signed, run on your machine | Playwright MCP |
| **Remote servers** | Hosted services connecting to external platforms | Linear MCP, GitHub MCP |

### Key Benefits

- **Dependency isolation** - Each tool runs containerized
- **Security & verification** - Signed releases, publisher verification
- **Simplified setup** - MCP Toolkit handles configuration
- **Cross-platform** - Consistent behavior across systems

---

## Task Hierarchy: Linear MCP vs Notion MCP

### Recommendation: Linear MCP

**Rationale:** Jira-like project management fits better than Notion's flexible database approach. Human populates tasks via orchestration, agents query via MCP.

### [Linear MCP](https://linear.app/docs/mcp) (Official)

| Aspect | Details |
|--------|---------|
| **Tools** | 21 specialized tools |
| **Operations** | Find, create, update issues/projects/comments |
| **Auth** | OAuth 2.1 with dynamic client registration |
| **Transport** | Remote hosted (no local setup needed) |
| **Endpoint** | `https://mcp.linear.app/mcp` (HTTP) or `https://mcp.linear.app/sse` (SSE) |

**Configuration:**
```json
{
  "mcpServers": {
    "Linear": {
      "type": "http",
      "url": "https://mcp.linear.app/mcp"
    }
  }
}
```

**Why Linear fits Dev Lab:**
- Human gets: Full Linear UI (boards, roadmaps, cycles, visualization)
- Agent gets: MCP tools to query/update same data
- No adapter pattern needed - same source of truth, different interfaces

### [Notion MCP](https://developers.notion.com/docs/mcp) (Official) - Alternative

| Aspect | Details |
|--------|---------|
| **Tools** | Pages, databases, blocks, comments, users |
| **Operations** | CRUD on all content types, query databases |
| **Auth** | OAuth (one-click for supported clients) |
| **Rate limit** | 180 requests/min |
| **Optimization** | Token-efficient, Markdown editing |

**Trade-off:** Linear = opinionated project management, Notion = flexible but you design the structure.

**Preference:** Linear for Jira-like workflow.

---

## Browser/UI Interaction: Playwright MCP

### Recommendation: Playwright MCP with VNC-enabled container

**Rationale:** Tool-based browser access lets agent decide when to inspect UI. VNC solves headless limitation for frontend development.

### [Playwright MCP](https://github.com/microsoft/playwright-mcp) (Microsoft Official)

| Aspect | Details |
|--------|---------|
| **Approach** | Accessibility tree (not screenshots) |
| **Browsers** | Chrome, Firefox, WebKit, Edge |
| **Core tools** | click, type, navigate, screenshot |
| **Tab management** | list, create, close, switch tabs |
| **Vision needed?** | No - structured data, not pixels |
| **Speed** | Fast, lightweight |
| **Released** | March 2025 |

**Configuration:**
```json
{
  "mcpServers": {
    "playwright": {
      "command": "npx",
      "args": ["@playwright/mcp@latest"]
    }
  }
}
```

**Options evaluated:**

| Approach | Verdict |
|----------|---------|
| Raw Playwright scripts | Agent must write scripts - more burden |
| **Playwright MCP** | **Winner** - Tool-based, agent decides |
| Native Chrome integration | Tied to specific IDE |
| Computer Use API | Overkill for dev testing, expensive |

### Visual Access Solutions

The headless Docker limitation is real for frontend development. Solutions:

| Solution | How it works |
|----------|--------------|
| **VNC in container** | Browser runs in container, human watches via VNC |
| **Browserbase MCP** | Cloud browser with screenshots + AI annotations |
| **Headed mode (Phase 1)** | No Docker, run Playwright headed locally |

See [Sandbox Solutions](./20251226-architecture-sandbox-solutions.md) for implementation details.

---

## GitHub MCP

### [GitHub MCP](https://github.com/github/github-mcp-server) (Official)

| Aspect | Details |
|--------|---------|
| **PR tools** | create, merge, get_files, get_review_comments, get_status |
| **Issue tools** | create, update, add_comment, assign_copilot |
| **Security** | Sanitizes input (Unicode, HTML, code fences) |
| **Modes** | Read-only mode available (`--read-only` flag) |
| **Toolsets** | `repos,issues,pull_requests,actions,code_security` |

**Configuration:**
```json
{
  "mcpServers": {
    "github": {
      "command": "docker",
      "args": ["run", "-e", "GITHUB_TOKEN", "mcp/github-official"]
    }
  }
}
```

**Dev Lab relevance:**
- Formalizes External Peripherals pattern
- Agent uses GitHub MCP instead of `gh` CLI
- Read-only mode for QA agent safety

---

## Documentation MCPs

### [Ref.tools MCP](https://ref.tools/mcp)

Token-efficient documentation search.

| Aspect | Details |
|--------|---------|
| **Token efficiency** | Returns ~5k tokens, drops irrelevant sections |
| **Session tracking** | Never returns repeated results in same session |
| **Tools** | `ref_search_documentation`, `ref_read_url`, `ref_web_search` |

**Configuration:**
```json
{
  "mcpServers": {
    "Ref": {
      "type": "http",
      "url": "https://api.ref.tools/mcp?apiKey=YOUR_API_KEY"
    }
  }
}
```

### [Context7](https://context7.com/)

Up-to-date documentation for LLMs.

| Aspect | Details |
|--------|---------|
| **Focus** | Fresh API/library documentation |
| **Integration** | Claude, Cursor support |
| **Approach** | Pre-computed context injection |

**Note:** Overlaps with Ref.tools - evaluate which better fits workflow.

---

## Agent Tool Matrix

Based on survey findings, recommended tool allocation:

| Agent | Linear MCP | GitHub MCP | Playwright MCP | Ref.tools MCP |
|-------|------------|------------|----------------|---------------|
| **Dev** | Query tasks | Create PRs | View UI (headed/VNC) | Search docs |
| **QA** | Query tasks | Create issues | Write E2E tests + View UI | Search docs |

### Differentiation

| Capability | Dev Agent | QA Agent |
|------------|-----------|----------|
| Write production code | Yes | No (safety hook blocks) |
| Write test scripts | No | Yes |
| Create PRs | Yes | No |
| Create issues | No | Yes |
| View browser | Yes | Yes |

---

## Summary: Options Identified

| Question | Options Found | Notes |
|----------|---------------|-------|
| Task Hierarchy Source of Truth | Linear MCP, Notion MCP | Linear recommended for Jira-like workflow |
| Browser/UI Interaction | Playwright MCP + VNC | Multiple VNC solutions available |
| Tool Ecosystem Survey | Docker MCP Catalog (270+ servers) | Starting point, evaluate per need |
| Context Generation | Ref.tools MCP, Context7 | Both worth evaluating |

---

## References

- [Docker MCP Catalog](https://hub.docker.com/mcp)
- [Docker Blog: Top MCP Servers 2025](https://www.docker.com/blog/top-mcp-servers-2025/)
- [Linear MCP Docs](https://linear.app/docs/mcp)
- [Notion MCP Docs](https://developers.notion.com/docs/mcp)
- [Playwright MCP GitHub](https://github.com/microsoft/playwright-mcp)
- [GitHub MCP Server](https://github.com/github/github-mcp-server)
- [Ref.tools MCP](https://github.com/ref-tools/ref-tools-mcp)
- [Context7](https://context7.com/)
