"""Push JSONL reports to the devlab-reports GitHub repository.

Uploads the full conversation JSONL (from stream-json output) to
kimwwk/devlab-reports via the GitHub Contents API. One API call per run.
"""

import base64
import json
import os
import urllib.error
import urllib.request
from datetime import datetime, timezone
from typing import Any

REPORTS_REPO = "kimwwk/devlab-reports"


def publish(
    jsonl_path: str,
    project_config: dict[str, Any],
    result: dict[str, Any],
) -> bool:
    """Push a JSONL file to the devlab-reports repo.

    Destination: data/{owner}/{repo}/{timestamp}_{task_name}.jsonl

    Args:
        jsonl_path: Path to the JSONL file to upload
        project_config: Project configuration (name, repo, etc.)
        result: Task result dict

    Returns:
        True if published successfully, False otherwise
    """
    token = os.environ.get("GITHUB_TOKEN") or _gh_token()
    if not token:
        print("Report skipped: no GITHUB_TOKEN")
        return False

    if not jsonl_path or not os.path.exists(jsonl_path):
        print("Report skipped: no JSONL file")
        return False

    # Extract owner/repo from URL like https://github.com/kimwwk/our-pot-app.git
    repo_url = project_config.get("repo", "")
    parts = repo_url.rstrip("/").removesuffix(".git").split("/")
    if len(parts) >= 2:
        owner, repo_name = parts[-2], parts[-1]
    else:
        owner, repo_name = "unknown", "unknown"

    task_name = project_config.get("name", "unknown")
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    dest_path = f"data/{owner}/{repo_name}/{timestamp}_{task_name}.jsonl"

    # Read and base64-encode
    with open(jsonl_path, "r") as f:
        content = f.read()
    encoded = base64.b64encode(content.encode("utf-8")).decode("ascii")

    # Compose commit message
    status = "failed" if result.get("is_error") else "done"
    commit_msg = f"[{task_name}] {status} — {owner}/{repo_name}"

    # PUT to GitHub Contents API
    api_url = f"https://api.github.com/repos/{REPORTS_REPO}/contents/{dest_path}"
    payload = {
        "message": commit_msg,
        "content": encoded,
    }

    return _put(api_url, payload, token)


def _put(url: str, payload: dict, token: str) -> bool:
    """Send a PUT request to GitHub API. Returns True on success."""
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        },
        method="PUT",
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            print(f"Report published: {resp.status} → {_dest_path(url)}")
            return True
    except urllib.error.HTTPError as e:
        print(f"Report failed: HTTP {e.code} from {url}")
        return False
    except urllib.error.URLError as e:
        print(f"Report failed: {e.reason} connecting to {url}")
        return False
    except Exception as e:
        print(f"Report failed: {e}")
        return False


def _dest_path(url: str) -> str:
    """Extract destination path from API URL for logging."""
    marker = "/contents/"
    idx = url.find(marker)
    return url[idx + len(marker):] if idx != -1 else url


def _gh_token() -> str | None:
    """Try to get token from gh CLI auth."""
    import subprocess

    try:
        result = subprocess.run(
            ["gh", "auth", "token"],
            capture_output=True, text=True, timeout=5,
        )
        token = result.stdout.strip()
        return token if token else None
    except Exception:
        return None
