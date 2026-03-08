"""Agent role configurations.

Based on patterns from pilot POC (fully-automated-remote-agent-experiments).
See docs/20251230-previous work-pilot reusables.md
"""

from typing import Any

# Default MCP servers for browser interaction
DEFAULT_MCP_SERVERS = {
    "chrome_devtools": {
        "command": "/usr/bin/chrome-devtools-mcp",
        "args": ["--browserUrl", "http://127.0.0.1:9222"]
    }
}

# Agent role definitions
AGENTS: dict[str, dict[str, Any]] = {
    "developer": {
        "name": "developer",
        "description": "Full-access developer agent for code implementation",
        "use_when": "You need code written, bugs fixed, features implemented, or refactoring done.",
        "expect": "Has full tool access including file editing, terminal, and browser. "
                  "Will make changes to your codebase directly.",
        "model": "sonnet",
        "tools": None,  # All tools allowed
        "disallowed_tools": None,
        "mcp_servers": DEFAULT_MCP_SERVERS,
        "hooks": None,  # No restrictions
    },
    "qa": {
        "name": "qa",
        "description": "QA agent for testing and validation",
        "use_when": "You need tests written, test suites run, or quality validation performed.",
        "expect": "Has full tool access with browser for E2E testing. "
                  "Works in its own test repository to avoid interfering with dev work.",
        "model": "sonnet",
        "tools": None,
        "disallowed_tools": None,
        "mcp_servers": DEFAULT_MCP_SERVERS,
        "hooks": None,
    },
    "dev-lead": {
        "name": "dev-lead",
        "description": "Developer lead with architectural awareness and design thinking",
        "use_when": "You need implementation that also considers architecture, project structure, "
                    "and design foundations — not just feature code.",
        "expect": "Has full tool access including file editing, terminal, and browser. "
                  "Will assess and improve codebase design as part of implementation.",
        "model": "sonnet",
        "tools": None,  # All tools allowed
        "disallowed_tools": None,
        "mcp_servers": DEFAULT_MCP_SERVERS,
        "hooks": None,
    },
    "qa-lead": {
        "name": "qa-lead",
        "description": "QA lead with test strategy and infrastructure design thinking",
        "use_when": "You need test work that also considers test architecture, coverage strategy, "
                    "and test infrastructure setup — not just running existing tests.",
        "expect": "Has full tool access with browser for E2E testing. "
                  "Will assess and improve test structure as part of validation.",
        "model": "sonnet",
        "tools": None,
        "disallowed_tools": None,
        "mcp_servers": DEFAULT_MCP_SERVERS,
        "hooks": None,
    },
    "reviewer": {
        "name": "reviewer",
        "description": "Code reviewer that posts feedback on PRs",
        "use_when": "You want automated code review on a pull request or branch diff.",
        "expect": "Reads code and searches the codebase but cannot edit files. "
                  "Uses Bash to post review comments via gh CLI.",
        "model": "sonnet",
        "tools": ["Read", "Glob", "Grep", "Bash", "WebFetch", "WebSearch"],  # Read-only + Bash for posting PR comments
        "disallowed_tools": None,
        "mcp_servers": None,  # No browser needed for review
        "hooks": None,
    },
    "analyst": {
        "name": "analyst",
        "description": "Research and analysis agent for multi-agent workflows",
        "use_when": "You need research, architectural analysis, or protocol-driven investigation.",
        "expect": "Has full tool access. Follows instructions or protocols defined in the repository to carry out analysis.",
        "model": "sonnet",
        "tools": None,
        "disallowed_tools": None,
        "mcp_servers": None,
        "hooks": None,
    },
}


def get_agent(name: str) -> dict[str, Any]:
    """Get agent configuration by name.

    Args:
        name: Agent name (developer, qa, reviewer)

    Returns:
        Agent configuration dictionary

    Raises:
        ValueError: If agent name is not recognized
    """
    if name not in AGENTS:
        available = ", ".join(AGENTS.keys())
        raise ValueError(f"Unknown agent '{name}'. Available: {available}")

    return AGENTS[name].copy()


def merge_agent_config(agent: dict[str, Any], overrides: dict[str, Any]) -> dict[str, Any]:
    """Merge agent config with project-level overrides.

    Args:
        agent: Base agent configuration
        overrides: Project-level overrides (model, mcp_servers, etc.)

    Returns:
        Merged configuration
    """
    merged = agent.copy()

    # Override model if specified
    if overrides.get("model"):
        merged["model"] = overrides["model"]

    # Override or extend MCP servers
    if overrides.get("mcp_servers"):
        if merged["mcp_servers"]:
            merged["mcp_servers"] = {**merged["mcp_servers"], **overrides["mcp_servers"]}
        else:
            merged["mcp_servers"] = overrides["mcp_servers"]

    return merged
