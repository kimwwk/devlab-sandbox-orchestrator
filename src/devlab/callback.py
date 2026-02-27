"""Webhook callback for notifying Forge when tasks complete.

Posts task results to an n8n webhook, which relays to the
configured channels (Telegram, Slack, or both).
"""

import json
import urllib.request
import urllib.error
from typing import Any


def notify(notify_config: dict[str, Any], project_config: dict[str, Any], result: dict[str, Any]) -> bool:
    """Send task completion notification to the n8n webhook.

    Args:
        notify_config: Notify section from YAML (webhook, channels)
        project_config: The YAML project config (name, repo, agent, etc.)
        result: Task result dict from Claude Code CLI

    Returns:
        True if delivered, False otherwise
    """
    webhook_url = notify_config.get("webhook")
    if not webhook_url:
        print("Notify skipped: no webhook URL")
        return False

    channels = notify_config.get("channels", ["telegram", "slack"])
    is_error = result.get("is_error", False)

    # Format numbers cleanly
    cost = result.get("total_cost_usd")
    cost_str = f"{cost:.2f}" if cost else "?"

    duration_ms = result.get("duration_ms")
    if duration_ms:
        secs = duration_ms / 1000
        duration_str = f"{secs / 60:.1f}m" if secs >= 60 else f"{secs:.0f}s"
    else:
        duration_str = "?"

    payload = {
        "channels": channels,
        "task_name": project_config.get("name", "unknown"),
        "repo": project_config.get("repo", ""),
        "agent": project_config.get("agent", "developer"),
        "model": result.get("model") or project_config.get("model", "sonnet"),
        "status": "failed" if is_error else "done",
        "cost_usd": cost_str,
        "duration": duration_str,
        "result_summary": _truncate(result.get("result", ""), 300),
    }

    return _post(webhook_url, payload)


def _truncate(text: str, max_len: int) -> str:
    if not text:
        return ""
    return text[:max_len] + ("..." if len(text) > max_len else "")


def _post(url: str, payload: dict) -> bool:
    """Send a POST request. Returns True on success."""
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            print(f"Notify delivered: {resp.status} {url}")
            return True
    except urllib.error.HTTPError as e:
        print(f"Notify failed: HTTP {e.code} from {url}")
        return False
    except urllib.error.URLError as e:
        print(f"Notify failed: {e.reason} connecting to {url}")
        return False
    except Exception as e:
        print(f"Notify failed: {e}")
        return False
