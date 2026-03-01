"""CLI entry point for Dev Lab.

Usage:
    python -m devlab run <project.yaml>     Run a task
    python -m devlab build <toolchain>      Build an image
    python -m devlab stop <container>       Stop a container
    python -m devlab list                   List running containers
    python -m devlab agent [name]           Show available agent roles
"""

import argparse
import os
import signal
import sys

from dotenv import load_dotenv
load_dotenv()

from .orchestrator import run_from_file
from .layers.build import build_image, list_images, get_image_tag, image_exists
from .layers.start import stop_container, is_running
from .config.agents import AGENTS

# --- Signal-safe container cleanup ---

from ._state import get_active_container


def _cleanup_on_signal(signum: int, frame) -> None:
    """Handle SIGHUP/SIGTERM by stopping the active container, then exiting."""
    container = get_active_container()
    if container:
        try:
            stop_container(container)
        except Exception:
            pass  # Best-effort cleanup
    sys.exit(128 + signum)


def _install_signal_handlers() -> None:
    """Install signal handlers for graceful shutdown.

    SIGHUP: sent when terminal closes (the & backgrounding problem).
    SIGTERM: sent by kill, systemd, docker stop, etc.
    SIGINT: already raises KeyboardInterrupt which triggers finally blocks.
    """
    signal.signal(signal.SIGHUP, _cleanup_on_signal)
    signal.signal(signal.SIGTERM, _cleanup_on_signal)


def cmd_run(args: argparse.Namespace) -> int:
    """Run a task from project config."""
    try:
        result = run_from_file(args.config, cleanup=not args.keep)

        if result.get("is_error"):
            print(f"\nError: {result.get('result', 'Unknown error')}")
            return 1

        print(f"\nResult:\n{result.get('result', '')}")
        return 0

    except FileNotFoundError as e:
        print(f"Error: {e}")
        return 1
    except ValueError as e:
        print(f"Configuration error: {e}")
        return 1
    except Exception as e:
        print(f"Error: {e}")
        return 1


def cmd_build(args: argparse.Namespace) -> int:
    """Build a toolchain image."""
    try:
        tag = build_image(args.toolchain, force=args.force)
        print(f"Built: {tag}")
        return 0
    except FileNotFoundError as e:
        print(f"Error: {e}")
        return 1
    except Exception as e:
        print(f"Build failed: {e}")
        return 1


def cmd_stop(args: argparse.Namespace) -> int:
    """Stop a container."""
    container = args.container
    if not container.startswith("devlab-"):
        container = f"devlab-{container}"

    try:
        stop_container(container)
        return 0
    except Exception as e:
        print(f"Error: {e}")
        return 1


def _is_pid_alive(pid: int) -> bool:
    """Check if a process with the given PID is alive."""
    try:
        os.kill(pid, 0)
        return True
    except (OSError, ProcessLookupError):
        return False


def _check_orphaned(container_name: str) -> bool:
    """Check if a container's managing devlab process is dead.

    Returns True if the pidfile exists but the process is gone.
    """
    pidfile = f"/tmp/{container_name}.pid"
    if not os.path.exists(pidfile):
        return False  # No pidfile = can't tell, assume not orphaned
    try:
        with open(pidfile) as f:
            pid = int(f.read().strip())
        return not _is_pid_alive(pid)
    except (ValueError, OSError):
        return True  # Corrupt pidfile = likely orphaned


def cmd_agent(args: argparse.Namespace) -> int:
    """Show agent information."""
    name = args.name

    if name:
        # Show details for a specific agent
        if name not in AGENTS:
            available = ", ".join(AGENTS.keys())
            print(f"Unknown agent '{name}'. Available: {available}")
            return 1

        agent = AGENTS[name]
        print(f"\n  {agent['name']}")
        print(f"  {agent['description']}")
        print()
        print(f"  When to use:    {agent.get('use_when', 'N/A')}")
        print(f"  What to expect: {agent.get('expect', 'N/A')}")
        print()
        print(f"  Model:          {agent.get('model', 'default')}")
        tools = agent.get("tools")
        print(f"  Tools:          {', '.join(tools) if tools else 'all'}")
        mcp = agent.get("mcp_servers")
        print(f"  MCP servers:    {', '.join(mcp.keys()) if mcp else 'none'}")
        print()
        return 0

    # List all agents
    print("\nAvailable agents:\n")
    for agent in AGENTS.values():
        print(f"  {agent['name']:<12} {agent['description']}")
        print(f"  {'':<12} Use when: {agent.get('use_when', 'N/A')}")
        print()

    print(f"Run 'devlab agent <name>' for full details.")
    return 0


def cmd_list(args: argparse.Namespace) -> int:
    """List devlab resources."""
    print("Images:")
    images = list_images()
    if images:
        for img in images:
            print(f"  {img}")
    else:
        print("  (none)")

    print("\nContainers:")
    import subprocess
    result = subprocess.run(
        ["docker", "ps", "--filter", "name=devlab-", "--format", "{{.Names}}\t{{.Status}}"],
        capture_output=True,
        text=True,
    )
    if result.stdout.strip():
        for line in result.stdout.strip().split("\n"):
            name = line.split("\t")[0].strip()
            suffix = "  (orphaned)" if _check_orphaned(name) else ""
            print(f"  {line}{suffix}")
    else:
        print("  (none running)")

    return 0


def main() -> int:
    """Main CLI entry point."""
    _install_signal_handlers()

    parser = argparse.ArgumentParser(
        prog="devlab",
        description="Dev Lab - Runtime Orchestrator for AI agents",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # run command
    run_parser = subparsers.add_parser("run", help="Run a task from project config")
    run_parser.add_argument("config", help="Path to project YAML file")
    run_parser.add_argument("--keep", action="store_true", help="Keep container running after task")
    run_parser.set_defaults(func=cmd_run)

    # build command
    build_parser = subparsers.add_parser("build", help="Build a toolchain image")
    build_parser.add_argument("toolchain", help="Toolchain name (node, python, fullstack)")
    build_parser.add_argument("--force", action="store_true", help="Force rebuild")
    build_parser.set_defaults(func=cmd_build)

    # stop command
    stop_parser = subparsers.add_parser("stop", help="Stop a container")
    stop_parser.add_argument("container", help="Container name or project name")
    stop_parser.set_defaults(func=cmd_stop)

    # agent command
    agent_parser = subparsers.add_parser("agent", help="Show available agent roles")
    agent_parser.add_argument("name", nargs="?", default=None, help="Agent name for details")
    agent_parser.set_defaults(func=cmd_agent)

    # list command
    list_parser = subparsers.add_parser("list", help="List devlab resources")
    list_parser.set_defaults(func=cmd_list)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
