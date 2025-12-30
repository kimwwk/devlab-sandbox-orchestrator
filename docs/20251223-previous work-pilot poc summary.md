# Pilot PoC Project Summary

**What it is**: An autonomous SDLC framework using Claude Agent SDK to create specialized AI agents that handle the complete software development workflow - from task implementation to PR creation to QA testing.

## Architecture

### Core Structure

```
Agent Registry (factory pattern)
  ├─> Senior Developer Agent (implements features, creates PRs)
  ├─> QA Engineer Agent (tests features, writes E2E tests)
  └─> [Extensible for new agents]
```

### Environment Setup (`main.py`)

The entry point that configures the execution environment:

- **MCP Server Configuration**: Initializes task-master-ai and Playwright servers
- **Agent Initialization**: Loads agent from registry with appropriate model, tools, and hooks
- **Hook System Setup**: Configures PreToolUse validators for safety constraints
- **Session Management**: Handles new sessions, resume modes, and session state persistence
- **Logging Infrastructure**: Sets up triple logging (console, text, JSONL)
- **Cleanup Validation**: Runs post-execution checks for workspace hygiene
- **Report Generation**: Converts JSONL logs to HTML audit reports

### Key Components

**Agent System** (`agents/`):
- Agent registry and factory pattern
- Specialized agent implementations (senior_developer, qa_engineer)
- Safety hooks for QA agent

**Infrastructure**:
- `session_manager.py` - Save/load agent sessions
- `logger.py` - Triple logging system
- `cleanup_checks.py` - Workspace validation

**Reporting**:
- `html_generator.py` - JSONL to HTML conversion
- `html_report_templates/` - Jinja2 templates and CSS
- `generate_report.py` - Standalone report utility

## How It Works

### Project-Level Workflow

When you run `main.py`:

1. **Environment Setup**: Configure MCP servers, logging, hooks, and agent
2. **Agent Execution**: Run the agent with its configured prompt and tools
3. **Cleanup Validation**: Check for uncommitted changes, in-progress tasks, stale processes
4. **Session Persistence**: Save session state for potential resume
5. **Report Generation**: Convert JSONL logs to HTML audit report

### Agent-Level Workflow

What the agent autonomously does during execution:

1. **Fetch Task**: Query task-master MCP server for next task
2. **Plan Work**: Break down task using TodoWrite tool
3. **Execute**: Implement features or write tests using full toolkit
4. **Deliver**: Create pull request (senior_developer) or test report (qa_engineer)
5. **Update Status**: Mark task as 'review' or 'done' in task-master

## Design Principles

- **Goal-oriented agents** - Not procedural; agents decide their approach
- **Single responsibility** - Each agent has one clear purpose
- **Safety through hooks** - PreToolUse validators enforce constraints (e.g., QA can't edit source code)
- **Session resumability** - Save/load sessions to handle failures and PR feedback

## Agents

### Current Agents

- **`senior_developer`** - Full development toolkit, creates features
- **`qa_engineer`** - Limited toolkit with safety hooks, tests and validates

### Extensibility

- Add agents via registry pattern
- Configure tools, hooks, prompts per agent
- MCP architecture for external integrations
- Template-based HTML reporting

## Integration & Configuration

**MCP Servers**:
- `task-master-ai` - Task management (get_tasks, set_task_status, update_task)
- `Playwright` - Browser automation (navigate, click, fill forms, take screenshots)

**Hooks System**:
- Custom validation rules per agent
- PreToolUse validators enforce safety constraints

**Logging**:
- Console output (Rich library with colors/formatting)
- Text logs (`logs/agent_run_TIMESTAMP.log`)
- JSONL logs (`logs/agent_run_TIMESTAMP.jsonl`)
- HTML reports (`logs/agent_run_TIMESTAMP.html`)

**Git Workflow**:
- Feature branches
- Commits with co-authoring
- PR creation via GitHub CLI

## Usage

```bash
uv run main.py --repo-path /path/to/project [OPTIONS]
```

**Options**:
- `--repo-path` (required) - Target repository path
- `--model` (optional) - haiku/sonnet/opus (default: sonnet)
- `--agent` (optional) - senior_developer/qa_engineer (default: senior_developer)
- `--resume <session_id>` - Resume a previous session
- `--resume-latest` - Resume the most recent session
