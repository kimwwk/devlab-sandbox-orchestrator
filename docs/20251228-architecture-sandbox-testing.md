# Sandbox Testing

## Objective

Validate AIO Sandbox for Dev Lab's Runtime Orchestrator:
1. Docker + VNC approach works for browser access
2. 3-layer provisioning strategy works (Image → Container → Runtime API)
3. Claude Code CLI integration works

**Related:** [Sandbox Solution Decisions](./20251229-architecture-sandbox-solution-decisions.md) | [Security Audit](./20251229-architecture-sandbox-AIO%20sandbox%20security%20audit.md)

---

## Quick Reference

### Test Directory

All test artifacts are in `sandbox-testing/`:

```
sandbox-testing/
├── Dockerfile.test      # Extended image with Claude Code
├── devlab-workspace/    # Test workspace for volume mount
├── .env.example         # Template for secrets
└── .gitignore           # Excludes .env from git
```

### Setup

```bash
cd sandbox-testing

# 1. Set up secrets
cp .env.example .env
# Edit .env with ANTHROPIC_API_KEY and GITHUB_TOKEN

# 2. Load env vars
source .env

# 3. Build extended image
docker build -t devlab-sandbox:test -f Dockerfile.test .

# 4. Run container
docker run --security-opt seccomp=unconfined --rm -d \
  -p 8888:8080 \
  -e ANTHROPIC_API_KEY="$ANTHROPIC_API_KEY" \
  -e GITHUB_TOKEN="$GITHUB_TOKEN" \
  --name devlab-test \
  devlab-sandbox:test

# 5. Clone repo (for VSCode visibility)
curl -X POST http://localhost:8888/v1/shell/exec \
  -H "Content-Type: application/json" \
  -d '{"command": "git clone https://$GITHUB_TOKEN@github.com/owner/repo.git /home/gem/project"}'

# 6. Setup browser MCP
docker exec -u gem devlab-test bash -c 'mkdir -p /home/gem/.claude && cat > /home/gem/.claude/mcp.json << EOF
{
  "mcpServers": {
    "chrome_devtools": {
      "command": "/usr/bin/chrome-devtools-mcp",
      "args": ["--browserUrl", "http://127.0.0.1:9222"]
    }
  }
}
EOF'

# 7. Run Claude Code
docker exec -u gem -w /home/gem/project devlab-test \
  claude --dangerously-skip-permissions \
  --mcp-config /home/gem/.claude/mcp.json \
  -p "Your task here"
```

### Access Points

| Service | URL |
|---------|-----|
| VNC | http://localhost:8888/vnc/index.html?autoconnect=true |
| VSCode | http://localhost:8888/code-server/ |
| API Docs | http://localhost:8888/v1/docs |

---

## Results Summary

| Phase | Test | Status | Key Finding |
|-------|------|--------|-------------|
| **1** | AIO Environment | ✅ Complete | VNC + Browser + API all working |
| **2** | Image Extension | ✅ Complete | Claude Code v2.0.76 installed |
| **2** | Container Start | ✅ Complete | Mount to `/workspace`, not `/home/gem/*` |
| **2** | Runtime API | ✅ Complete | Uses `file` param, not `path` |
| **3** | Claude Code Install | ✅ Complete | Pre-installed in extended image |
| **3** | CLI Invocation | ✅ Complete | Run as `gem` user with `--dangerously-skip-permissions` |
| **3** | Browser MCP | ✅ Complete | Use Chrome DevTools MCP for VNC visibility |
| **3** | Output Analysis | ✅ Complete | CLI JSON output sufficient, SDK not needed |
| **4** | SDK (Optional) | ⏭️ Skipped | CLI sufficient |

---

## Phase 1: Environment Validation

### Test 1.1: AIO Sandbox Environment

**Status:** ✅ Complete

**Verified:**
- [x] Container starts with all components (browser, VNC, VSCode, API)
- [x] Browser can load URLs via VNC
- [x] Can run commands inside container

**Command:**
```bash
docker run --security-opt seccomp=unconfined --rm -d -p 8888:8080 --name aio-sandbox ghcr.io/agent-infra/sandbox:latest
```

---

## Phase 2: Provisioning Layers

Tests the 3-layer provisioning strategy: **Image Build → Container Start → Runtime API**

### Test 2.1: Layer B - Image Extension

**Status:** ✅ Complete

**Verified:**
- [x] Can build custom image FROM aio-sandbox
- [x] Can install Claude Code via npm
- [x] Can add custom apt packages
- [x] Extended image runs correctly

**Results:**
```
/usr/bin/claude
2.0.76 (Claude Code)
```

**Dockerfile.test:**
```dockerfile
FROM ghcr.io/agent-infra/sandbox:latest

# Install Claude Code
RUN npm install -g @anthropic-ai/claude-code

# Install additional tools (example)
RUN apt-get update && apt-get install -y jq && rm -rf /var/lib/apt/lists/*
```

---

### Test 2.2: Layer C - Container Start Configuration

**Status:** ✅ Complete

**Verified:**
- [x] Volume mount works for workspace
- [x] Environment variables are accessible inside container
- [x] Credentials can be injected via env vars

**Finding:** Cannot mount to `/home/gem/*` - container entrypoint needs write access there for setup. **Use `/workspace` instead.**

**Working Command:**
```bash
docker run --security-opt seccomp=unconfined --rm -d \
  -p 8888:8080 \
  -v /path/to/workspace:/workspace \
  -e GITHUB_TOKEN=xxx \
  -e ANTHROPIC_API_KEY=xxx \
  --name devlab-test \
  devlab-sandbox:test
```

**Verification:**
```bash
# Mount verified
docker exec devlab-test ls -la /workspace
# total 12
# -rw-r--r-- 1 gem 990 15 Dec 30 10:51 README.md

# Env vars verified
docker exec devlab-test printenv | grep -E "GITHUB_TOKEN|ANTHROPIC_API_KEY"
# GITHUB_TOKEN=xxx
# ANTHROPIC_API_KEY=xxx
```

---

### Test 2.3: Layer A - Runtime API Provisioning

**Status:** ✅ Complete

**Verified:**
- [x] `/v1/shell/exec` can run setup commands
- [x] `/v1/file/write` can inject config files
- [x] `/v1/file/read` can verify setup
- [x] Can install packages at runtime

**Finding:** File API uses `file` parameter, not `path`.

**API Examples:**

```bash
# Shell exec - returns JSON with output and exit_code
curl -X POST http://localhost:8888/v1/shell/exec \
  -H "Content-Type: application/json" \
  -d '{"command": "echo hello && pwd && whoami"}'
# {"success":true,"data":{"output":"hello\n/home/gem\ngem","exit_code":0}}

# File write - uses "file" not "path"
curl -X POST http://localhost:8888/v1/file/write \
  -H "Content-Type: application/json" \
  -d '{"file": "/home/gem/CLAUDE.md", "content": "# Context\n\nTest."}'
# {"success":true,"data":{"file":"/home/gem/CLAUDE.md","bytes_written":20}}

# File read
curl -X POST http://localhost:8888/v1/file/read \
  -H "Content-Type: application/json" \
  -d '{"file": "/home/gem/CLAUDE.md"}'
# {"success":true,"data":{"content":"# Context\n\nTest."}}
```

---

## Phase 3: Claude Code Integration

### Test 3.1: Claude Code Installation

**Status:** ✅ Complete (via Test 2.1)

Claude Code pre-installed in extended image:
- Binary: `/usr/bin/claude`
- Version: `2.0.76`

---

### Test 3.2: CLI Invocation (Non-Interactive)

**Status:** ✅ Complete

**Verified:**
- [x] Can run Claude Code with `-p` (print/prompt) flag
- [x] Output is captured via stdout
- [x] Exit codes are meaningful (0=success, 1=failure)
- [x] Can pass ANTHROPIC_API_KEY via environment
- [x] File creation works

**Critical Findings:**

| Finding | Detail |
|---------|--------|
| Must run as `gem` user | `docker exec -u gem` (not root) |
| Must skip permissions | `--dangerously-skip-permissions` required for non-interactive |
| No `--cwd` flag | Use `docker exec -w /path` instead |
| Clone to `/home/gem/project` | For VSCode visibility |

**Correct Invocation Pattern:**
```bash
# Clone repo first (for human visibility in VSCode)
curl -X POST http://localhost:8888/v1/shell/exec \
  -H "Content-Type: application/json" \
  -d '{"command": "git clone https://$GITHUB_TOKEN@github.com/owner/repo.git /home/gem/project"}'

# Invoke Claude Code
docker exec -u gem -w /home/gem/project devlab-test \
  claude --dangerously-skip-permissions -p "Your task here"
```

**Test Results:**
```bash
# Basic invocation
docker exec -u gem devlab-test claude --dangerously-skip-permissions -p "What is 2+2?"
# Output: 4

# File creation
docker exec -u gem -w /home/gem/project devlab-test \
  claude --dangerously-skip-permissions -p "Create test.txt with 'hello world'"
# Output: Done! I've created the file test.txt...
# Exit code: 0

# Verify
docker exec devlab-test cat /home/gem/project/test.txt
# Output: hello world
```

---

### Test 3.3: Browser MCP (VNC Visible)

**Status:** ✅ Complete

**Verified:**
- [x] Can configure MCP for Claude Code
- [x] Claude Code can navigate browser
- [x] Content extracted successfully
- [x] Human can watch via VNC (**Chrome DevTools MCP only**)

**Critical Finding: Two MCP Options**

| MCP Server | Package | VNC Visible? | Notes |
|------------|---------|--------------|-------|
| **Playwright MCP** | `@playwright/mcp` | ❌ No | Uses accessibility snapshots, headless |
| **Chrome DevTools MCP** | Built-in AIO | ✅ Yes | Uses existing Chrome on CDP :9222 |

**For human visibility, use Chrome DevTools MCP (AIO's built-in).**

**Setup (Chrome DevTools - Recommended):**
```bash
# Create MCP config using AIO's Chrome DevTools
docker exec -u gem devlab-test bash -c 'mkdir -p /home/gem/.claude && cat > /home/gem/.claude/mcp.json << EOF
{
  "mcpServers": {
    "chrome_devtools": {
      "command": "/usr/bin/chrome-devtools-mcp",
      "args": ["--browserUrl", "http://127.0.0.1:9222"]
    }
  }
}
EOF'
```

**Invocation (must use `--mcp-config` flag):**
```bash
docker exec -u gem -w /home/gem/project devlab-test \
  claude --dangerously-skip-permissions \
  --mcp-config /home/gem/.claude/mcp.json \
  -p "Navigate to https://example.com and describe what you see"
```

**Available Chrome DevTools Tools:**
- `navigate_page` - Navigate to URL
- `take_snapshot` - Text snapshot (a11y tree)
- `take_screenshot` - Visual screenshot
- `click`, `hover`, `fill` - Interact with elements
- `new_page`, `close_page` - Tab management
- `evaluate_script` - Run JavaScript

**Alternative: Playwright MCP (if VNC visibility not needed):**
```bash
# Add via Claude CLI
docker exec -u gem devlab-test claude mcp add playwright npx @playwright/mcp@latest

# Or manually
cat > /home/gem/.claude/mcp.json << EOF
{
  "mcpServers": {
    "playwright": {
      "command": "npx",
      "args": ["@playwright/mcp@latest"]
    }
  }
}
EOF
```

---

### Test 3.4: CLI Output Analysis (For SDK Decision)

**Status:** ✅ Complete

**Objective:** Evaluate if CLI output is sufficient or if SDK is needed.

**Finding: CLI provides structured JSON output - SDK NOT needed.**

**Output Formats:**

| Format | Flag | Use Case |
|--------|------|----------|
| `text` | (default) | Human readable |
| `json` | `--output-format json` | Single result, easy parsing |
| `stream-json` | `--output-format stream-json --verbose` | Real-time tool monitoring |

**JSON Output Example:**
```json
{
  "type": "result",
  "subtype": "success",
  "is_error": false,
  "result": "The answer...",
  "duration_ms": 4095,
  "total_cost_usd": 0.025,
  "session_id": "...",
  "usage": {...}
}
```

**Stream-JSON Shows Tool Use:**
```json
{"type":"assistant","message":{"content":[{"type":"tool_use","name":"Read","input":{...}}]}}
{"type":"user","message":{"content":[{"type":"tool_result","is_error":true}]}}
{"type":"result","subtype":"success",...}
```

**Analysis Criteria:**

| Criteria | CLI Sufficient? | Notes |
|----------|-----------------|-------|
| Task completion detection | ✅ Yes | `subtype: "success"` or `"error"` |
| Error identification | ✅ Yes | `is_error: true` + error content |
| Result extraction | ✅ Yes | `result` field has final text |
| Tool use monitoring | ✅ Yes | Stream-JSON shows each tool call |
| Cost tracking | ✅ Yes | `total_cost_usd` field |
| Session resumption | ✅ Yes | `session_id` for `--resume` |

**Decision: Use CLI, skip SDK.**

---

## Phase 4: SDK Comparison (Optional)

*Only proceed if Phase 3 tests indicate SDK is needed.*

### Test 4.1: SDK Installation

**Commands:**
```bash
docker exec devlab-test pip install claude-agent-sdk
docker exec devlab-test python -c "from claude_agent_sdk import query; print('SDK installed')"
```

### Test 4.2: SDK vs CLI Output Comparison

**Test script:**
```python
import asyncio
import json
from claude_agent_sdk import query

async def main():
    async for msg in query(prompt="What is 2+2?"):
        print(json.dumps({
            "type": type(msg).__name__,
            "content": str(msg)
        }))

asyncio.run(main())
```

---

## Key Findings

### Gotchas Discovered

| Issue | Solution |
|-------|----------|
| Cannot mount to `/home/gem/*` at start | Mount to `/workspace` OR clone to `/home/gem/project` via Runtime API |
| File API uses `file` not `path` | Use `{"file": "/path"}` in requests |
| Container needs `--security-opt seccomp=unconfined` | Required for Chrome/browser |
| `docker exec` runs as root by default | Use `docker exec -u gem` for Claude Code |
| Claude Code needs permission bypass | Use `--dangerously-skip-permissions` flag |
| No `--cwd` flag in Claude Code | Use `docker exec -w /path` instead |
| MCP config not auto-loaded | Use `--mcp-config /path/to/mcp.json` flag |
| Playwright MCP is headless | Use Chrome DevTools MCP for VNC visibility |

### Provisioning Layer Summary

| Layer | When | What | Verified |
|-------|------|------|----------|
| **B. Image** | Build time | Claude Code, git, tools | ✅ |
| **C. Container** | Start time | Volume mounts, env vars | ✅ |
| **A. Runtime** | Task time | Clone repo, inject files | ✅ |

---

## Decision Checkpoints

| After Test | Decision | Result |
|------------|----------|--------|
| 3.2 | Is CLI invocation reliable? | ✅ Yes - works with `-u gem --dangerously-skip-permissions` |
| 3.4 | Is CLI output parseable enough, or need SDK? | ✅ Yes - JSON output is fully structured |
| 4.2 | If SDK tested, is the complexity worth it? | ⏭️ Skipped - CLI sufficient |

## Final Decision

**Use CLI, not SDK.**

The Claude Code CLI with `--output-format json` provides all the structured output an orchestrator needs:
- Success/failure detection
- Result extraction
- Tool use monitoring (with `stream-json`)
- Cost tracking
- Session resumption

SDK adds complexity with no additional benefit for this use case.
