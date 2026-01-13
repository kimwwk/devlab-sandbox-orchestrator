"""Layer 2: Start - Container lifecycle management."""

import subprocess
import time
from typing import Optional


def is_running(name: str) -> bool:
    """Check if a container is running.

    Args:
        name: Container name

    Returns:
        True if container is running
    """
    result = subprocess.run(
        ["docker", "container", "inspect", "-f", "{{.State.Running}}", name],
        capture_output=True,
        text=True,
    )
    return result.returncode == 0 and result.stdout.strip() == "true"


def container_exists(name: str) -> bool:
    """Check if a container exists (running or stopped).

    Args:
        name: Container name

    Returns:
        True if container exists
    """
    result = subprocess.run(
        ["docker", "container", "inspect", name],
        capture_output=True,
    )
    return result.returncode == 0


def start_container(
    image: str,
    name: str,
    env: dict[str, str],
    port: int = 8888,
) -> str:
    """Start a new container.

    Args:
        image: Docker image tag
        name: Container name
        env: Environment variables (ANTHROPIC_API_KEY, GITHUB_TOKEN)
        port: Host port to map to container's 8080 (default: 8888)

    Returns:
        Container name

    Raises:
        RuntimeError: If container already exists
        subprocess.CalledProcessError: If docker run fails
    """
    if container_exists(name):
        if is_running(name):
            raise RuntimeError(f"Container '{name}' is already running")
        else:
            # Remove stopped container
            subprocess.run(["docker", "rm", name], check=True)

    # Build docker run command
    cmd = [
        "docker", "run",
        "--security-opt", "seccomp=unconfined",  # Required for Chrome
        "--rm",  # Auto-remove when stopped
        "-d",  # Detached
        "-p", f"{port}:8080",  # VNC/API port
        "--name", name,
    ]

    # Add environment variables
    for key, value in env.items():
        cmd.extend(["-e", f"{key}={value}"])

    # Add image
    cmd.append(image)

    print(f"Starting container {name} from {image}...")
    subprocess.run(cmd, check=True)

    # Wait for container to be ready
    _wait_for_ready(name)

    print(f"Container {name} is ready")
    print(f"  VNC: http://localhost:{port}/vnc/index.html?autoconnect=true")
    print(f"  VSCode: http://localhost:{port}/code-server/")

    return name


def _wait_for_ready(name: str, timeout: int = 30) -> None:
    """Wait for container to be ready.

    Args:
        name: Container name
        timeout: Maximum seconds to wait

    Raises:
        TimeoutError: If container doesn't become ready
    """
    start = time.time()
    while time.time() - start < timeout:
        if is_running(name):
            # Give services a moment to start
            time.sleep(2)
            return
        time.sleep(0.5)

    raise TimeoutError(f"Container '{name}' did not start within {timeout}s")


def stop_container(name: str) -> None:
    """Stop and remove a container.

    Args:
        name: Container name
    """
    if not container_exists(name):
        print(f"Container '{name}' does not exist")
        return

    print(f"Stopping container {name}...")
    subprocess.run(["docker", "stop", name], check=True)
    print(f"Container {name} stopped")


def get_container_port(name: str) -> Optional[int]:
    """Get the host port mapped to container's 8080.

    Args:
        name: Container name

    Returns:
        Host port or None if not found
    """
    result = subprocess.run(
        ["docker", "port", name, "8080"],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return None

    # Output format: 0.0.0.0:8888 or :::8888
    output = result.stdout.strip()
    if ":" in output:
        return int(output.split(":")[-1])
    return None
