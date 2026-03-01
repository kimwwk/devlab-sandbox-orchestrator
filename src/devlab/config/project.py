"""Project configuration loader."""

import os
from pathlib import Path
from typing import Any

import yaml


def load_project(config_path: str) -> dict[str, Any]:
    """Load project configuration from YAML file.

    Args:
        config_path: Path to the project YAML file

    Returns:
        Dictionary with project configuration

    Raises:
        FileNotFoundError: If config file doesn't exist
        ValueError: If required fields are missing
    """
    path = Path(config_path)
    if not path.exists():
        raise FileNotFoundError(f"Project config not found: {config_path}")

    with open(path) as f:
        config = yaml.safe_load(f)

    # Validate required fields
    required = ["name", "repo"]
    missing = [f for f in required if f not in config]
    if missing:
        raise ValueError(f"Missing required fields: {missing}")

    # Validate task source: either task or linear_issue
    if "task" not in config and "linear_issue" not in config:
        raise ValueError("Either 'task' or 'linear_issue' must be specified")

    # Set defaults
    config.setdefault("toolchain", "node")
    config.setdefault("agent", "developer")
    config.setdefault("model", None)  # Use agent default
    config.setdefault("mcp_servers", None)  # Use agent default
    config.setdefault("port", 8888)
    config.setdefault("task", None)
    config.setdefault("linear_issue", None)
    config.setdefault("notify", None)
    config.setdefault("timeout", 600)
    config.setdefault("project_env", {})
    config.setdefault("setup_command", None)

    return config


def get_env_vars() -> dict[str, str]:
    """Get required environment variables.

    Returns:
        Dictionary with ANTHROPIC_API_KEY and GITHUB_TOKEN

    Raises:
        ValueError: If required env vars are not set
    """
    env = {}

    # Required: either ANTHROPIC_API_KEY or CLAUDE_CODE_OAUTH_TOKEN
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    oauth_token = os.environ.get("CLAUDE_CODE_OAUTH_TOKEN")
    if not api_key and not oauth_token:
        raise ValueError(
            "Either ANTHROPIC_API_KEY or CLAUDE_CODE_OAUTH_TOKEN must be set"
        )
    if api_key:
        env["ANTHROPIC_API_KEY"] = api_key
    if oauth_token:
        env["CLAUDE_CODE_OAUTH_TOKEN"] = oauth_token

    # Optional but recommended for private repos
    github_token = os.environ.get("GITHUB_TOKEN")
    if github_token:
        env["GITHUB_TOKEN"] = github_token

    return env
