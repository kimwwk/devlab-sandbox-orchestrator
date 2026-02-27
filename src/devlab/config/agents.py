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
        "model": "sonnet",
        "tools": None,  # All tools allowed
        "disallowed_tools": None,
        "mcp_servers": DEFAULT_MCP_SERVERS,
        "hooks": None,  # No restrictions
        "system_prompt_append": None,
    },
    "qa": {
        "name": "qa",
        "description": "QA agent restricted to test files only",
        "model": "haiku",
        "tools": None,  # All tools, but with restrictions via disallowed
        "disallowed_tools": None,  # Use hooks for path-based restrictions
        "mcp_servers": DEFAULT_MCP_SERVERS,
        "hooks": {
            "PreToolUse": [
                {
                    "matcher": "Write|Edit",
                    "hooks": [
                        {
                            "type": "command",
                            "command": "bash -c 'echo $TOOL_INPUT | jq -r .file_path | grep -qE \"/(tests?|__tests__|cypress|playwright)/\" || (echo \"QA can only write to test directories\" >&2 && exit 2)'",
                            "timeout": 5
                        }
                    ]
                },
                {
                    "matcher": "Bash",
                    "hooks": [
                        {
                            "type": "command",
                            "command": "bash -c 'echo $TOOL_INPUT | jq -r .command | grep -qvE \"npm (run dev|start)|yarn (dev|start)|serve|http-server\" || (echo \"QA cannot start dev servers\" >&2 && exit 2)'",
                            "timeout": 5
                        }
                    ]
                }
            ]
        },
        "system_prompt_append": "You are a QA engineer. Focus on testing and validation. Do not modify source code outside of test directories.",
    },
    "reviewer": {
        "name": "reviewer",
        "description": "Read-only reviewer agent for code review",
        "model": "sonnet",
        "tools": ["Read", "Glob", "Grep", "WebFetch", "WebSearch"],  # Read-only tools
        "disallowed_tools": None,
        "mcp_servers": None,  # No browser needed for review
        "hooks": None,
        "system_prompt_append": "You are a code reviewer. Analyze the code and provide feedback. Do not make any changes.",
    },
    "analyst": {
        "name": "analyst",
        "description": "Analysis orchestrator for protocol-driven multi-agent workflows",
        "model": "sonnet",
        "tools": None,
        "disallowed_tools": None,
        "mcp_servers": None,
        "hooks": None,
        "system_prompt_append": None,
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
