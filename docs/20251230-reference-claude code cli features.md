# Reference - Claude Code CLI Features

## Overview

Features available in Claude Code CLI for orchestrator integration.

**Base Command:**
```bash
claude --dangerously-skip-permissions \
  --output-format json \
  --mcp-config /path/to/mcp.json \
  --settings /path/to/settings.json \
  --model sonnet \
  -p "Your task"
```

---

## Output Formats

| Format | Flag | Use Case |
|--------|------|----------|
| `text` | (default) | Human readable |
| `json` | `--output-format json` | Single result, easy parsing |
| `stream-json` | `--output-format stream-json --verbose` | Real-time tool monitoring |

### JSON Output Structure

```json
{
  "type": "result",
  "subtype": "success",
  "is_error": false,
  "result": "The final answer...",
  "duration_ms": 4095,
  "total_cost_usd": 0.025,
  "session_id": "uuid-for-resume",
  "num_turns": 2,
  "usage": {
    "input_tokens": 100,
    "output_tokens": 50
  }
}
```

### Stream-JSON Events

```jsonl
{"type":"system","session_id":"...","tools":[...],"model":"..."}
{"type":"assistant","message":{"content":[{"type":"tool_use","name":"Read","input":{...}}]}}
{"type":"user","message":{"content":[{"type":"tool_result","is_error":false}]}}
{"type":"result","subtype":"success","result":"..."}
```

---

## MCP Configuration

### File Location

```bash
# Global
~/.claude.json

# Project-specific
/path/to/project/.claude/mcp.json

# CLI override
--mcp-config /path/to/mcp.json
```

### Stdio MCP Server

```json
{
  "mcpServers": {
    "my-server": {
      "command": "npx",
      "args": ["@my/mcp-server"],
      "env": {
        "API_KEY": "${API_KEY}"
      }
    }
  }
}
```

### HTTP MCP Server with Authentication

```json
{
  "mcpServers": {
    "my-api": {
      "type": "http",
      "url": "https://api.example.com/mcp",
      "headers": {
        "Authorization": "Bearer ${API_TOKEN}"
      }
    }
  }
}
```

### API Key Headers

```json
{
  "mcpServers": {
    "my-api": {
      "type": "http",
      "url": "https://api.example.com/mcp",
      "headers": {
        "X-API-Key": "${API_KEY}",
        "X-API-Secret": "${API_SECRET}"
      }
    }
  }
}
```

---

## Hooks

### Hook Types

| Event | When | Use Case |
|-------|------|----------|
| `PreToolUse` | Before tool executes | Validate/block tool calls |
| `PostToolUse` | After tool executes | Log, update status |
| `Stop` | Agent stops | Cleanup, notify |
| `SessionStart` | Session begins | Validate environment |

### Hook Actions

| Type | Description |
|------|-------------|
| `command` | Run shell script |
| `prompt` | Ask Claude to evaluate |

### Configuration Example

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          {
            "type": "command",
            "command": "bash ./scan-secrets.sh",
            "timeout": 30
          }
        ]
      },
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "prompt",
            "prompt": "Is this bash command safe for production?",
            "timeout": 20
          }
        ]
      },
      {
        "matcher": "mcp__.*__delete.*",
        "hooks": [
          {
            "type": "prompt",
            "prompt": "Confirm deletion is intentional and reversible"
          }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "bash ./update-status.sh",
            "timeout": 15
          }
        ]
      }
    ],
    "Stop": [
      {
        "matcher": ".*",
        "hooks": [
          {
            "type": "command",
            "command": "bash ./notify-completion.sh",
            "timeout": 30
          }
        ]
      }
    ],
    "SessionStart": [
      {
        "matcher": ".*",
        "hooks": [
          {
            "type": "command",
            "command": "bash ./validate-permissions.sh",
            "timeout": 20
          }
        ]
      }
    ]
  }
}
```

### Hook Script Example (scan-secrets.sh)

```bash
#!/bin/bash
input=$(cat)
content=$(echo "$input" | jq -r '.tool_input.content')

# Check for secret patterns
if echo "$content" | grep -qE "(api[_-]?key|password|secret|token).{0,20}['\"]?[A-Za-z0-9]{20,}"; then
  echo '{"decision": "deny", "reason": "Potential secret detected"}' >&2
  exit 2
fi

exit 0
```

---

## Model Selection

### CLI Flag

```bash
claude --model haiku -p "Quick task"
claude --model sonnet -p "Complex task"
claude --model opus -p "Very complex task"
```

### Model Aliases

| Alias | Full Model ID |
|-------|---------------|
| `haiku` | `claude-3-5-haiku-20241022` |
| `sonnet` | `claude-sonnet-4-5-20250929` |
| `opus` | `claude-opus-4-5-20251101` |

### Fallback Model

```bash
claude --model opus --fallback-model sonnet -p "Try opus, fallback to sonnet if overloaded"
```

---

## Settings Override

### CLI Flag

```bash
# From file
claude --settings /path/to/settings.json -p "..."

# Inline JSON
claude --settings '{"temperature": 0.5}' -p "..."
```

### Settings File Structure

```json
{
  "model": "sonnet",
  "temperature": 0.2,
  "maxTokens": 64000,
  "permissions": {
    "allowedTools": ["Read", "Glob", "Grep"],
    "disallowedTools": ["Bash", "Write"]
  }
}
```

---

## Session Management

### Resume Session

```bash
# By session ID (from previous output)
claude --resume abc123-session-id -p "Continue"

# Latest session
claude --continue -p "Continue"
```

### Fork Session

```bash
# Resume but create new session ID
claude --resume abc123 --fork-session -p "Branch off"
```

### Disable Persistence

```bash
# Don't save session (ephemeral)
claude --no-session-persistence -p "One-off task"
```

---

## Tool Control

### Allow Specific Tools

```bash
claude --allowed-tools "Read,Glob,Grep" -p "Read-only task"
```

### Disallow Specific Tools

```bash
claude --disallowed-tools "Bash,Write,Edit" -p "Safe task"
```

### Specify Tool Set

```bash
# Only these tools available
claude --tools "Read,Glob,Grep,WebFetch" -p "Research task"

# Disable all tools
claude --tools "" -p "Just answer, no tools"
```

---

## Permission Modes

| Mode | Flag | Description |
|------|------|-------------|
| `default` | (none) | Ask for permissions |
| `bypassPermissions` | `--dangerously-skip-permissions` | Skip all permission checks |
| `plan` | `--permission-mode plan` | Plan mode |
| `acceptEdits` | `--permission-mode acceptEdits` | Auto-accept file edits |

---

## System Prompt

### Override

```bash
claude --system-prompt "You are a code reviewer..." -p "Review this"
```

### Append

```bash
claude --append-system-prompt "Always use TypeScript" -p "Create a function"
```

---

## Budget Control

```bash
# Max spend per invocation
claude --max-budget-usd 1.00 -p "Complex task, limit to $1"
```

---

## Multi-Agent Configuration

### Different Agents with Different Configs

```bash
# Developer Agent - full access, opus model
docker exec -u gem -w /home/gem/project devlab-test \
  claude --dangerously-skip-permissions \
  --mcp-config /home/gem/.claude/mcp-developer.json \
  --model opus \
  --output-format json \
  -p "Implement feature X"

# QA Agent - restricted, haiku model
docker exec -u gem -w /home/gem/project devlab-test \
  claude --dangerously-skip-permissions \
  --mcp-config /home/gem/.claude/mcp-qa.json \
  --settings /home/gem/.claude/settings-qa.json \
  --disallowed-tools "Write,Edit" \
  --model haiku \
  --output-format json \
  -p "Test feature X"

# Reviewer Agent - read-only, sonnet model
docker exec -u gem -w /home/gem/project devlab-test \
  claude --dangerously-skip-permissions \
  --tools "Read,Glob,Grep" \
  --model sonnet \
  --output-format json \
  -p "Review the implementation"
```

---

## Summary: Key Flags for Orchestration

| Flag | Purpose |
|------|---------|
| `-p "prompt"` | Non-interactive mode |
| `--dangerously-skip-permissions` | Sandbox mode (no prompts) |
| `--output-format json` | Structured output |
| `--mcp-config file.json` | MCP servers |
| `--settings file.json` | Custom settings |
| `--model haiku\|sonnet\|opus` | Model selection |
| `--allowed-tools "..."` | Restrict tools |
| `--max-budget-usd N` | Cost limit |
| `--resume SESSION_ID` | Continue session |
