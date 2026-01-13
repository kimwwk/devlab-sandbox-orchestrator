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
    required = ["name", "repo", "task"]
    missing = [f for f in required if f not in config]
    if missing:
        raise ValueError(f"Missing required fields: {missing}")

    # Set defaults
    config.setdefault("toolchain", "node")
    config.setdefault("agent", "developer")
    config.setdefault("model", None)  # Use agent default
    config.setdefault("mcp_servers", None)  # Use agent default
    config.setdefault("port", 8888)

    return config


def get_env_vars() -> dict[str, str]:
    """Get required environment variables.

    Returns:
        Dictionary with ANTHROPIC_API_KEY and GITHUB_TOKEN

    Raises:
        ValueError: If required env vars are not set
    """
    env = {}

    # Required
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY environment variable not set")
    env["ANTHROPIC_API_KEY"] = api_key

    # Optional but recommended for private repos
    github_token = os.environ.get("GITHUB_TOKEN")
    if github_token:
        env["GITHUB_TOKEN"] = github_token

    return env
