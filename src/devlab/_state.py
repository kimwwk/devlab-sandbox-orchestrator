"""Shared mutable state for signal-safe container cleanup.

Kept in a separate module to avoid circular imports between
cli.py and orchestrator.py.
"""

import os

_active_container: str | None = None


def set_active_container(name: str) -> None:
    """Register the container that should be cleaned up on signal."""
    global _active_container
    _active_container = name


def clear_active_container() -> None:
    """Clear the active container (called after normal cleanup)."""
    global _active_container
    _active_container = None


def get_active_container() -> str | None:
    """Return the currently active container name, if any."""
    return _active_container


def pidfile_path(container_name: str) -> str:
    """Return the pidfile path for a container."""
    return f"/tmp/{container_name}.pid"


def write_pidfile(container_name: str) -> None:
    """Write current PID to the container's pidfile."""
    path = pidfile_path(container_name)
    with open(path, "w") as f:
        f.write(str(os.getpid()))


def remove_pidfile(container_name: str) -> None:
    """Remove the container's pidfile."""
    path = pidfile_path(container_name)
    try:
        os.unlink(path)
    except OSError:
        pass
