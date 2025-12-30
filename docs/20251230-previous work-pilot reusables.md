# Previous Work - Pilot Reusables

## Source

Repository: `fully-automated-remote-agent-experiments`

An autonomous coding agent framework using Claude Agent SDK for multi-agent workflows.

---

## Reusable Components

### 1. HTML Report Generator

**Location:** `html_generator.py` + `html_report_templates/`

**What it does:**
- Converts JSONL logs → interactive HTML reports
- Dashboard with duration, cost, token usage
- Collapsible tool calls with formatted input/output
- Message filtering by type
- Dark theme (Claude.ai-inspired)
- Zero external dependencies (single HTML file)

**Structure:**
```
html_report_templates/
├── base.html                  # Main layout
├── components/
│   ├── system_message.html    # System init card
│   ├── assistant_message.html # Agent reasoning & tool calls
│   ├── user_message.html      # Tool results
│   └── result_message.html    # Final summary
├── styles/
│   ├── base.css, system.css, assistant.css, user.css, result.css
├── message_parser.py          # Structured data parsing
├── script.js                  # Interactive functionality
└── message_renderers.py       # Advanced rendering
```

**Usage:**
```bash
python generate_report.py logs/agent_run.jsonl
# Output: logs/agent_run.html
```

---

### 2. Hook System

**Location:** `agents/qa_engineer_hooks.py`

**What it does:**
- PreToolUse validators that approve/deny tool usage
- Role-based constraints (QA can't edit source, only tests)
- Command blocking (QA can't start dev servers)

**Example - Block dev servers:**
```python
async def qa_bash_validator(tool_input):
    blocked = ['npm run dev', 'npm start', 'serve', 'http-server']
    command = tool_input.get('command', '')
    for pattern in blocked:
        if pattern in command:
            return {
                'hookSpecificOutput': {
                    'permissionDecision': 'deny',
                    'permissionDecisionReason': f'QA cannot run: {pattern}'
                }
            }
    return None  # Allow
```

**Example - Restrict file paths:**
```python
async def qa_file_operation_validator(tool_input):
    allowed_paths = ['/tests/', '/test/', '/__tests__/', '/cypress/', '/playwright/']
    file_path = tool_input.get('file_path', '')
    if not any(p in file_path for p in allowed_paths):
        return {
            'hookSpecificOutput': {
                'permissionDecision': 'deny',
                'permissionDecisionReason': 'QA can only write to test directories'
            }
        }
    return None
```

---

### 3. MCP Configuration Pattern

**Location:** `main.py:29-54`

**What it does:**
- Dynamic MCP server setup with env var injection
- Clean separation of concerns

**Example:**
```python
mcp_servers = {
    "task-master": {
        "command": "npx",
        "args": ["-y", "--package=task-master-ai", "task-master-ai"],
        "env": {
            "ANTHROPIC_API_KEY": os.getenv("ANTHROPIC_API_KEY"),
            "MODEL": "claude-3-7-sonnet-20250219",
            "MAX_TOKENS": "64000",
            "TEMPERATURE": "0.2"
        }
    },
    "playwright": {
        "command": "npx",
        "args": ["@playwright/mcp@latest", "--isolated", "--headless"]
    }
}
```

---

### 4. Multi-Agent Roles

**Location:** `agents/senior_developer.py`, `agents/qa_engineer.py`

**What it does:**
- Different agents with different permissions
- Factory pattern for agent instantiation

| Agent | Purpose | Tools | Hooks |
|-------|---------|-------|-------|
| Senior Developer | Code implementation | Full access | None |
| QA Engineer | Testing/validation | Restricted | Blocks source edits, dev servers |

**Agent Definition Pattern:**
```python
def get_agent_properties(model: str, repo_path: str):
    return {
        "model": model,
        "system": """Role definition...""",
        "tools": [...],  # Available tools
        "mcp_servers": {...},  # MCP access
        "hooks": {...}  # Constraints
    }
```

---

### 5. JSONL Logger

**Location:** `logger.py`

**What it does:**
- Structured logging for HTML report generation
- Triple output: Console (Rich) + Text + JSONL

**Example output:**
```jsonl
{"type":"system","timestamp":"...","session_id":"...","tools":[...]}
{"type":"assistant","message":{"content":[{"type":"tool_use","name":"Read",...}]}}
{"type":"user","message":{"content":[{"type":"tool_result",...}]}}
{"type":"result","subtype":"success","result":"...","total_cost_usd":0.025}
```

---

### 6. Session Manager

**Location:** `session_manager.py`

**What it does:**
- Save/resume session metadata
- List previous sessions
- Get latest session for `--resume`

**API:**
```python
session_manager.save_session(session_id, metadata)
session_manager.get_session(session_id)
session_manager.list_sessions()
session_manager.get_latest_session()
```

---

### 7. Cleanup Checks

**Location:** `cleanup_checks.py`

**What it does:**
- Post-execution validation
- Verify clean state before/after agent runs

**Checks:**
```python
check_tasks_in_progress()      # Verify task-master cleanup
check_uncommitted_changes()    # Verify git workspace clean
check_playwright_processes()   # Kill stale browser processes
```

---

## Adaptation for Dev Lab

| Pilot Component | Dev Lab Usage |
|-----------------|---------------|
| HTML Report Generator | Generate execution reports for human review in VSCode |
| Hook System | Enforce role-based constraints via CLI `--settings` |
| MCP Config Pattern | Pass API keys to MCP servers in container |
| Multi-Agent Roles | Create Developer, QA, Reviewer agent configs |
| JSONL Logger | Capture via `--output-format stream-json` |
| Session Manager | Use CLI `--resume` with `session_id` from output |
| Cleanup Checks | Run via Runtime API after agent completes |

---

## Key Differences

| Aspect | Pilot (SDK) | Dev Lab (CLI) |
|--------|-------------|---------------|
| Invocation | Python SDK | `docker exec claude -p` |
| Hooks | SDK `HookMatcher` | CLI JSON config |
| Logging | Custom `JSONLLogger` | `--output-format stream-json` |
| Session | SDK session object | CLI `--resume SESSION_ID` |
| MCP | SDK `mcp_servers` dict | CLI `--mcp-config file.json` |
