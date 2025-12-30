# Helpful Tools to Leverage

Analysis of tools that can accelerate Dev Lab development.

---

## [Context7](https://context7.com/)

Up-to-date documentation aggregation for LLMs and AI code editors.

### Strong Points

- **Fresh documentation context** - Always current API/library references
- **Context generation** - Pre-computes relevant documentation snippets for LLMs
- **Claude integration** - Direct support for Claude and code editors like Cursor
- **Library management** - Can add custom documentation sources
- **Reduces file reading** - Agents get context without reading every file

### Dev Lab Relevance

| Dev Lab Need | How Context7 Helps |
|--------------|-------------------|
| Context Generation Strategy | Pre-computes codebase awareness before agent runs |
| Memory Persistence | Fresh docs reduce agent reliance on stale context |
| Environment Provisioning | Can inject documentation context into agent environment |

### Integration Approach

```bash
# Could be used in Runtime Orchestrator's context provisioning step:
# 1. Query Context7 for relevant framework/library docs
# 2. Inject into agent's context before spawn
```

---

## [Ref.tools MCP](https://ref.tools/mcp)

Token-efficient documentation search via MCP protocol.

### Strong Points

- **Token efficiency** - Returns most relevant ~5k tokens, drops irrelevant sections
- **Session tracking** - Never returns repeated results in same session
- **Reduces context rot** - Avoids 20k+ token dumps from naive web scraping
- **Three specialized tools**:
  - `ref_search_documentation` - Technical docs search
  - `ref_read_url` - Full page content reader
  - `ref_web_search` - Fallback web search
- **MCP-native** - Plug-and-play with existing MCP setup

### Dev Lab Relevance

| Dev Lab Need | How Ref.tools Helps |
|--------------|---------------------|
| Tool Ecosystem | Ready-made MCP server, no custom build needed |
| Context Management | Session-aware search minimizes wasted tokens |
| Agent Autonomy | Agents can self-serve documentation needs |
| Environment over Model | Adds capability via tool, not prompt tricks |

### Integration Approach

```json
// Add to .mcp.json alongside task-master-ai
{
  "mcpServers": {
    "Ref": {
      "type": "http",
      "url": "https://api.ref.tools/mcp?apiKey=YOUR_API_KEY"
    }
  }
}
```

---

## [Docker MCP Catalog](https://docs.docker.com/ai/mcp-catalog-and-toolkit/catalog/)

Centralized registry of verified, containerized MCP servers.

### Strong Points

- **Verified publishers** - Partners include New Relic, Stripe, Grafana
- **Dependency isolation** - Each tool runs in container, no environment conflicts
- **Two server types**:
  - **Local servers** - Docker-built, digitally signed, offline-capable
  - **Remote servers** - Connect to GitHub, Notion, Linear, etc.
- **Security & verification** - Signed releases, publisher verification
- **Cross-platform** - Consistent behavior across systems
- **Simplified setup** - MCP Toolkit handles configuration

### Available Servers (Relevant to Dev Lab)

| Server | Use Case |
|--------|----------|
| GitHub MCP | PR creation, issue management, code review |
| Postgres/Database MCPs | Agent database access |
| Browser MCPs | UI testing, visual verification |
| Notion/Linear MCPs | Alternative task hierarchy tools |

### Dev Lab Relevance

| Dev Lab Need | How Docker MCP Helps |
|--------------|---------------------|
| Tool Ecosystem Survey | Pre-built solutions before custom work |
| Sandbox by Default | Containerized isolation aligns with safety philosophy |
| Tooling as Portfolio | Swap/compose tools without rebuilding |
| Browser/UI Interaction | Browser MCPs address open architecture question |
| External Peripherals | GitHub MCP formalizes agent-GitHub interaction |

### Integration Approach

```bash
# Use Docker MCP Toolkit in Runtime Orchestrator
# 1. Provision container-based MCP servers per agent type
# 2. Dev agent gets GitHub + Database MCPs
# 3. QA agent gets Browser + GitHub MCPs
```

---

## Summary: Priority for Dev Lab

| Tool | Priority | Reason |
|------|----------|--------|
| Docker MCP Catalog | **High** | Addresses Tool Ecosystem Survey, Sandbox isolation, Browser/UI question |
| Ref.tools MCP | **Medium** | Token-efficient docs, easy MCP integration |
| Context7 | **Medium** | Pre-computed context, but overlaps with Ref.tools |

### Recommended Next Steps

1. **Explore Docker MCP Catalog** - Survey available servers, identify gaps
2. **Add Ref.tools MCP** - Low-effort add to existing .mcp.json
3. **Evaluate Context7** - Compare with Ref.tools for context provisioning approach

### Addresses Open Architecture Questions

| Question (from [backbone](./20251224-architecture-backbone.md)) | Tool Solution |
|--------------------------------------------------------------|---------------|
| Browser/UI Interaction | Docker MCP Browser servers |
| Tool Ecosystem Survey | Docker MCP Catalog |
| Context Generation Strategy | Context7 + Ref.tools |
| What gaps require custom work? | Survey Docker MCP first |