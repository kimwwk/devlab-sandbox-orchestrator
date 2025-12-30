# Dev Lab

## Ultimate Goal (live update)

I am building a system where I can delegate real software development work to AI agents that operate autonomously within defined boundaries, freeing me to focus on higher-level decisions while maintaining full control over orchestration and quality.

## Core Concepts

### Environment Over Model

The primary architectural philosophy is that the environment (context, tools, permissions, memory, and interfaces provided to an AI) matters more than the specific LLM. Models are ephemeral; the LLM is a replaceable "brain" that optimizes decisions based on the environment you build around it.

### Agents as Decision Engines

Agents are valuable because they function as decision engines: they can plan, choose tools, and execute without requiring a human to micromanage their internal reasoning. The workflow should be designed so agents can operate autonomously within clearly defined goals and constraints.

### Primary Engine

We are currently committing to Claude Code as the primary engine because it behaves like an autonomous terminal-based developer: it can navigate the filesystem, run installed tools, and interact directly with the OS.

This aligns with the philosophy because it emphasizes capability via environment/tool access, not model-specific prompt tricks.

### Tooling Is a Portfolio, Not a Lock-in

While vendor friction is real (different SDKs, schemas, wrappers), "primary tool" is a current preference, not a permanent dependency. Over time, I expect to evaluate multiple tools/agents, adopt what each does best, and possibly combine them—treating tools as a portfolio I can swap or compose as the ecosystem evolves.

### It Is an Ecosystem

I am not rigidly trying to build everything. The system includes:
- **Internal agents**: Custom agents I build and control (Dev Lab agents)
- **External peripherals**: Existing tools and automations I leverage (e.g., GitHub Actions, CI/CD bots)

External peripherals don't speak my protocol and aren't mandatory modules. They exist in the broader ecosystem, and my agents interact with them as a human developer would—through standard interfaces (PRs, comments, issues, CI status).

## Constraints & Preferences

### Philosophy

- **Environment over Model**: The workflow should be built around tool access, context management, memory, and interfaces—not fragile prompt engineering tailored to one model.

### Model Tolerance

- Open to closed-source models (Claude, GPT, etc.).

### Primary Tool (Current)

- **Claude Code** is the current preferred "engine," primarily for terminal-native autonomy.

### Vendor Friction

- Acknowledge lock-in friction (SDKs/wrappers/schemas), but treat it as a temporary tradeoff.
- Intend to mitigate by designing the system so "brains/tools" can be swapped as better options appear.

### Human-Led Orchestration (Phased Approach)

- **For now, I am the orchestrator.** I personally coordinate which agents run, when they run, and how outputs are combined. There are no orchestration scripts or orchestrator agents at this stage.
- **Layer-by-layer evolution:** Start simple (single agent execution), then gradually introduce additional layers (planner/orchestrator agents, multi-agent collaboration) as reliability improves.
- **Future direction:** Agents should eventually be able to communicate and coordinate with each other, but only after the base agents are proven dependable.
- **Current limitations are acceptable:** No overnight runs, no parallelization. These are intentional scope constraints for this phase.

### Sandbox by Default

- Every agent runs in an isolated **sandbox environment** by default. At least container level.
- Primary purpose: **Safety** (agents cannot break production or affect unintended systems).
- No implicit sharing between agents (files, tools, credentials, memory). Sharing must be explicit and permissioned.

## State Boundaries

Clear boundaries define what state exists, who owns it, and how it flows.

### Agent-Private State

Working memory, scratch files, internal reasoning, session context.
- Never shared between agents
- Dies with the agent session (unless explicitly persisted via session save)
- Example: Agent's todo list, internal planning notes, temporary test files

### Project State

Repository files, branches, PRs, issues, CI status, task records.
- The shared reality that all agents and peripherals interact with
- Accessed through standard tools and interfaces (Git, GitHub API, task-master MCP)
- Agents read and write project state; they don't share it directly with each other
- External peripherals (GitHub Actions) also read/write project state
- Example: A PR created by senior_developer is visible to QA agent, GitHub Actions, and me

### Orchestration State

Which agents have run, what they produced, what's pending, what decisions I've made.
- **Owned by me personally** (not scripts, not agents)
- Agents do not read orchestration state; they receive specific task instructions derived from my decisions
- I observe project state changes to inform my orchestration decisions
- Example: I see CI passed, I decide to trigger QA agent, I provide QA agent with relevant context

### State Flow

```
Me (Orchestrator)
    │
    ├── Observes: Project State (PRs, CI status, task status)
    │
    ├── Decides: What agent runs next, with what context
    │
    └── Instructs: Agent receives Task Instructions + Project Context
            │
            Agent executes (Agent-Private State)
            │
            └── Writes to: Project State (commits, PRs, task updates)
                    │
                    External Peripherals react (GitHub Actions runs CI)
                    │
                    └── Updates: Project State (CI status, comments)
```

## Repository Constraints

To keep things focused and enable agents to work effectively, target repositories must align with certain constraints:

- **Documentation requirements**: README, background information, project context files must exist
- **Consistent structure**: Agents expect discoverable entry points, not arbitrary layouts
- **Task definitions**: Clear task records (via task-master or similar) that agents can query

These constraints are not bureaucratic overhead—they are the environment that makes agents effective.

## External Peripherals Integration

External peripherals (GitHub Actions, CI/CD systems, bots) are not part of Dev Lab's internal architecture. They are existing ecosystem tools that:

- **Trigger on their own rules** (push events, PR events, schedules)
- **Read/write Project State** through standard interfaces
- **Don't receive Task Instructions** from me directly
- **Produce observable outputs** (CI pass/fail, comments, status checks) that I consume as orchestrator

My agents interact with peripherals the same way a human developer would: push code, wait for CI, read the results, respond to comments.

This is intentional. The underlying principle is that my agents are my representatives working like humans, and the GitHub ecosystem represents decades of tooling built for human developers. Leverage, don't rebuild.

## Agentic Solution Techniques

### Agent Design Principles

To help agents work efficiently and effectively, design agent prompts to be **goal-oriented** rather than procedural. Agents should have autonomy and act as decision engines, not follow deterministic workflows.

### What to Include in Agent Prompts

- **Goals**: Define clear long-term and/or short-term objectives
- **Role**: Establish the agent's perspective and responsibilities
- **Task Instructions**: Provide the task with specific instructions that give strong hints on how to complete it
- **Project Context**: Share relevant background information
- **Soft Guidance**: Offer best practices and principles rather than rigid rules

### What to Avoid in Agent Prompts

- **Step-by-step procedures**: Rigid steps are not always necessary or accurate. Let agents determine their approach based on goals and context.
