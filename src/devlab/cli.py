"""CLI entry point for Dev Lab.

Usage:
    python -m devlab run <project.yaml>     Run a task
    python -m devlab build <toolchain>      Build an image
    python -m devlab stop <container>       Stop a container
    python -m devlab list                   List running containers
"""

import argparse
import sys

from dotenv import load_dotenv
load_dotenv()

from .orchestrator import run_from_file
from .layers.build import build_image, list_images, get_image_tag, image_exists
from .layers.start import stop_container, is_running


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
            print(f"  {line}")
    else:
        print("  (none running)")

    return 0


def main() -> int:
    """Main CLI entry point."""
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

    # list command
    list_parser = subparsers.add_parser("list", help="List devlab resources")
    list_parser.set_defaults(func=cmd_list)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
