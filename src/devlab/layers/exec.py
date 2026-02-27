"""Layer 3: Exec - Task execution inside container."""

import json
import subprocess
from typing import Any, Optional


def _docker_exec(
    container: str,
    command: str,
    user: str = "gem",
    workdir: Optional[str] = None,
    capture_output: bool = True,
) -> subprocess.CompletedProcess:
    """Execute command inside container.

    Args:
        container: Container name
        command: Shell command to execute
        user: User to run as (default: gem)
        workdir: Working directory inside container
        capture_output: Whether to capture stdout/stderr

    Returns:
        CompletedProcess with output
    """
    cmd = ["docker", "exec", "-u", user]

    if workdir:
        cmd.extend(["-w", workdir])

    cmd.extend([container, "bash", "-c", command])

    return subprocess.run(
        cmd,
        capture_output=capture_output,
        text=True,
    )


def configure_git(
    container: str,
    token: Optional[str] = None,
    user_name: str = "devlab-agent",
    user_email: str = "devlab-agent@noreply.github.com",
) -> None:
    """Configure git credentials and identity inside container.

    Sets up the credential store, git identity, and gh CLI auth
    in a single docker exec call.

    Args:
        container: Container name
        token: GitHub token for credential store and gh auth
        user_name: Git commit author name
        user_email: Git commit author email
    """
    lines = [
        f'git config --global user.name "{user_name}"',
        f'git config --global user.email "{user_email}"',
    ]

    if token:
        lines.extend([
            f'echo "https://x-access-token:{token}@github.com" > ~/.git-credentials',
            "git config --global credential.helper store",
            f'echo "{token}" | gh auth login --with-token 2>/dev/null || true',
        ])

    result = _docker_exec(container, " && ".join(lines))

    if result.returncode != 0:
        print(f"Git config warning: {result.stderr.strip()}")
    elif token:
        print("Git configured: credentials, identity, gh CLI")
    else:
        print("Git configured: identity only (no token)")


def clone_repo(
    container: str,
    repo_url: str,
    path: str = "/home/gem/project",
) -> None:
    """Clone a git repository inside the container.

    Relies on configure_git() having set up the credential helper
    so no token injection into the URL is needed.

    Args:
        container: Container name
        repo_url: Repository URL (https://github.com/owner/repo.git)
        path: Destination path inside container

    Raises:
        RuntimeError: If clone fails
    """
    # Remove existing directory if present
    _docker_exec(container, f"rm -rf {path}")

    print(f"Cloning {repo_url} to {path}...")
    result = _docker_exec(container, f"git clone {repo_url} {path}")

    if result.returncode != 0:
        raise RuntimeError(f"Failed to clone repo: {result.stderr}")

    print(f"Successfully cloned to {path}")


def setup_mcp(container: str, mcp_config: dict[str, Any]) -> None:
    """Write MCP configuration file inside container.

    Args:
        container: Container name
        mcp_config: MCP servers configuration

    Raises:
        RuntimeError: If setup fails
    """
    config_dir = "/home/gem/.claude"
    config_file = f"{config_dir}/mcp.json"

    # Create config directory
    _docker_exec(container, f"mkdir -p {config_dir}")

    # Write config file
    config_json = json.dumps({"mcpServers": mcp_config}, indent=2)
    # Escape for shell
    escaped = config_json.replace("'", "'\"'\"'")

    result = _docker_exec(
        container,
        f"cat > {config_file} << 'EOF'\n{config_json}\nEOF"
    )

    if result.returncode != 0:
        raise RuntimeError(f"Failed to write MCP config: {result.stderr}")

    print(f"MCP config written to {config_file}")


def invoke_agent(
    container: str,
    task: str,
    model: str = "sonnet",
    tools: Optional[list[str]] = None,
    disallowed_tools: Optional[list[str]] = None,
    mcp_config_path: Optional[str] = "/home/gem/.claude/mcp.json",
    workdir: str = "/home/gem/project",
    output_format: str = "json",
    timeout: int = 600,
) -> dict[str, Any]:
    """Invoke Claude Code CLI inside container.

    Args:
        container: Container name
        task: Task prompt for the agent
        model: Model to use (haiku, sonnet, opus)
        tools: List of allowed tools (None = all)
        disallowed_tools: List of disallowed tools
        mcp_config_path: Path to MCP config file
        workdir: Working directory for agent
        output_format: Output format (json, stream-json, text)
        timeout: Timeout in seconds

    Returns:
        Parsed JSON result from Claude Code

    Raises:
        RuntimeError: If invocation fails
        TimeoutError: If agent times out
    """
    # Build claude command
    cmd_parts = [
        "claude",
        "--dangerously-skip-permissions",
        "--output-format", output_format,
        "--model", model,
    ]

    # Add MCP config if exists
    if mcp_config_path:
        cmd_parts.extend(["--mcp-config", mcp_config_path])

    # Add tool restrictions
    if tools:
        cmd_parts.extend(["--tools", ",".join(tools)])
    if disallowed_tools:
        cmd_parts.extend(["--disallowed-tools", ",".join(disallowed_tools)])

    # Add task prompt (escape single quotes)
    escaped_task = task.replace("'", "'\"'\"'")
    cmd_parts.extend(["-p", f"'{escaped_task}'"])

    cmd = " ".join(cmd_parts)

    print(f"Invoking agent with model={model}...")
    print(f"Task: {task[:100]}..." if len(task) > 100 else f"Task: {task}")

    # Execute
    result = subprocess.run(
        [
            "docker", "exec",
            "-u", "gem",
            "-w", workdir,
            container,
            "bash", "-c", cmd,
        ],
        capture_output=True,
        text=True,
        timeout=timeout,
    )

    # Parse output
    if output_format == "json":
        try:
            return json.loads(result.stdout)
        except json.JSONDecodeError:
            return {
                "type": "result",
                "subtype": "error",
                "is_error": True,
                "result": result.stdout or result.stderr,
                "raw_stdout": result.stdout,
                "raw_stderr": result.stderr,
                "exit_code": result.returncode,
            }
    else:
        return {
            "type": "result",
            "subtype": "success" if result.returncode == 0 else "error",
            "is_error": result.returncode != 0,
            "result": result.stdout,
            "raw_stderr": result.stderr,
            "exit_code": result.returncode,
        }


def run_command(container: str, command: str, workdir: str = "/home/gem/project") -> dict[str, Any]:
    """Run a shell command inside container.

    Args:
        container: Container name
        command: Shell command
        workdir: Working directory

    Returns:
        Dict with output, stderr, and exit_code
    """
    result = _docker_exec(container, command, workdir=workdir)
    return {
        "output": result.stdout,
        "stderr": result.stderr,
        "exit_code": result.returncode,
    }
