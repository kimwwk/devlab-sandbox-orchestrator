# Dev Lab

Runtime Orchestrator for AI agents running in isolated sandbox containers.

## Prerequisites

- Docker
- Python 3.10+
- [uv](https://github.com/astral-sh/uv) (recommended) or pip

## Setup

```bash
# Install dependencies
uv sync

# Copy and configure environment variables
cp .env.example .env
# Edit .env with your API keys:
#   ANTHROPIC_API_KEY=sk-ant-...
#   GITHUB_TOKEN=ghp_...  (for private repos)

# Load environment variables
source .env
```

## Commands

### Build an image

```bash
uv run python cli.py build node
```

Builds the `devlab-sandbox:node` Docker image with Claude Code CLI installed.

### Run a task

```bash
uv run python cli.py run our-pot-app.yaml
```

Runs the task defined in the YAML config file. This will:
1. Build the image (if needed)
2. Start a container
3. Clone the repository
4. Setup MCP servers
5. Invoke the agent
6. Return the result
7. Stop the container

Use `--keep` to keep the container running after the task:

```bash
uv run python cli.py run our-pot-app.yaml --keep
```

### List resources

```bash
uv run python cli.py list
```

Lists all devlab images and running containers.

### Stop a container

```bash
uv run python cli.py stop our-pot-app
```

Stops and removes the container.

## Project Config (YAML)

Create a YAML file for each project:

```yaml
name: my-project
repo: https://github.com/owner/repo.git
toolchain: node

# Agent to use (developer, qa, reviewer)
agent: developer

# Task to execute
task: |
  Your task description here.
  Can be multi-line.

# Optional overrides
model: sonnet  # haiku, sonnet, opus
port: 8888     # VNC port
```

## Access Points

When a container is running:

| Service | URL |
|---------|-----|
| VNC | http://localhost:8888/vnc/index.html?autoconnect=true |
| VSCode | http://localhost:8888/code-server/ |

## Agent Roles

| Agent | Description | Access |
|-------|-------------|--------|
| `developer` | Full-access developer | All tools |
| `qa` | QA engineer | Can only write to test directories |
| `reviewer` | Code reviewer | Read-only |

## Architecture

```
project.yaml (you define)
         ↓ read by
Runtime Orchestrator (Python)
         ↓ provisions
AIO Sandbox Container
         ↓ runs
Claude Code CLI (agent)
         ↓ works on
Your repository (cloned inside container)
```

### 3-Layer Provisioning

| Layer | Mechanism | What |
|-------|-----------|------|
| 1. Build | `docker build` | Toolchain image (Claude Code, node/python) |
| 2. Start | `docker run` | Container with credentials |
| 3. Exec | `docker exec` | Clone repo, setup MCP, invoke agent |

## Future possibility 

- [x] Linear-Driven Task Execution
  - Agent queries Linear for assigned task (instead of YAML task field)
  - Uses Linear MCP tools we just validated
  - Agent posts result as Linear comment
  - Updates issue status (in progress → done)
- [ ] npm install did it first in setup
- [x] refine different roles in each agent and have clear boundaries
- [x] allow kick start the claude code idea grooming with agent team too
- [x] HTML Reports
  - Capture --output-format stream-json
  - Feed into HTML generator
  - Port html_generator.py from PoC
  - Generate report after each run for human review
- [ ] monitor token usage
  - need to avoid over long time running.
