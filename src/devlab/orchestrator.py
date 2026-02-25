"""Core orchestration logic for Dev Lab."""

from typing import Any

from .config import load_project, get_agent, get_env_vars
from .config.agents import merge_agent_config
from .layers import build_image, start_container, stop_container, is_running
from .layers.build import get_image_tag
from .layers.exec import clone_repo, setup_mcp, invoke_agent
from . import callback


def compose_task_prompt(project_config: dict[str, Any]) -> str:
    """Compose the task prompt for the agent.

    If linear_issue is specified, compose a role-appropriate structured prompt.
    Otherwise, use the literal task field.

    Args:
        project_config: Project configuration from YAML

    Returns:
        Task prompt string
    """
    linear_issue = project_config.get("linear_issue")
    if linear_issue:
        from .prompts.linear import compose_linear_prompt
        agent_role = project_config.get("agent", "developer")
        return compose_linear_prompt(linear_issue, agent_role)
    return project_config["task"]


def run(project_config: dict[str, Any], cleanup: bool = True) -> dict[str, Any]:
    """Run a task based on project configuration.

    This is the main orchestration flow:
    1. Build image (if needed)
    2. Start container
    3. Clone repo
    4. Setup MCP
    5. Invoke agent
    6. Return result
    7. Cleanup (optional)

    Args:
        project_config: Project configuration from YAML
        cleanup: Whether to stop container after task (default: True)

    Returns:
        Agent result dictionary
    """
    name = project_config["name"]
    repo = project_config["repo"]
    toolchain = project_config["toolchain"]
    task = compose_task_prompt(project_config)
    port = project_config.get("port", 8888)

    # Get environment variables
    env = get_env_vars()

    # Get agent configuration
    agent_name = project_config.get("agent", "developer")
    agent = get_agent(agent_name)

    # Merge with project-level overrides
    agent = merge_agent_config(agent, {
        "model": project_config.get("model"),
        "mcp_servers": project_config.get("mcp_servers"),
    })

    # Container name based on project
    container_name = f"devlab-{name}"

    try:
        # Layer 1: Build image
        print("\n=== Layer 1: Build ===")
        image_tag = get_image_tag(toolchain)
        build_image(toolchain)

        # Layer 2: Start container
        print("\n=== Layer 2: Start ===")
        if is_running(container_name):
            print(f"Container {container_name} already running, reusing...")
        else:
            start_container(
                image=image_tag,
                name=container_name,
                env=env,
                port=port,
            )

        # Layer 3: Exec
        print("\n=== Layer 3: Exec ===")

        # Clone repo
        clone_repo(
            container=container_name,
            repo_url=repo,
            token=env.get("GITHUB_TOKEN"),
        )

        # Setup MCP
        if agent.get("mcp_servers"):
            setup_mcp(container_name, agent["mcp_servers"])

        # Invoke agent
        result = invoke_agent(
            container=container_name,
            task=task,
            model=agent.get("model", "sonnet"),
            tools=agent.get("tools"),
            disallowed_tools=agent.get("disallowed_tools"),
            mcp_config_path="/home/gem/.claude/mcp.json" if agent.get("mcp_servers") else None,
        )

        print("\n=== Result ===")
        if result.get("is_error"):
            print(f"Task failed: {result.get('result', 'Unknown error')}")
        else:
            print(f"Task completed successfully")
            if result.get("total_cost_usd"):
                print(f"Cost: ${result['total_cost_usd']:.4f}")
            if result.get("duration_ms"):
                print(f"Duration: {result['duration_ms'] / 1000:.1f}s")

        # Notify on completion
        notify_config = project_config.get("notify")
        if notify_config:
            print("\n=== Notify ===")
            callback.notify(notify_config, project_config, result)

        return result

    finally:
        if cleanup:
            print("\n=== Cleanup ===")
            stop_container(container_name)


def run_from_file(config_path: str, cleanup: bool = True) -> dict[str, Any]:
    """Run a task from a YAML config file.

    Args:
        config_path: Path to project YAML file
        cleanup: Whether to stop container after task

    Returns:
        Agent result dictionary
    """
    config = load_project(config_path)
    return run(config, cleanup=cleanup)
