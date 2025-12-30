# AIO Sandbox Security Audit

## Objective

Investigate AIO Sandbox codebase for security risks before adoption in Dev Lab.

**Related:** [Sandbox Solution Decisions](./20251229-architecture-sandbox-solution-decisions.md)

---

## Scope

| Category | Focus |
|----------|-------|
| **Malware** | Hidden malicious code, backdoors |
| **Data Exfiltration** | Unauthorized data transmission |
| **Hidden Remote Servers** | Undocumented external connections |

**Out of scope:** Generic open source risks, sandbox escape risks, baseline security trade-offs.

---

## Project Background

| Attribute | Value |
|-----------|-------|
| **Repository** | [github.com/agent-infra/sandbox](https://github.com/agent-infra/sandbox) |
| **License** | Apache 2.0 |
| **Stars** | ~1.8k |
| **Maintainer** | agent-infra (likely ByteDance - volcengine references, UI-TARS integration) |
| **Security Policy** | No SECURITY.md |
| **Known CVEs** | None specific to this project |

---

## Code Inspection

### Components Reviewed

| Component | Location | Type |
|-----------|----------|------|
| **gem-server** | `/opt/gem-server/src/gem/` | Python (FastAPI) |
| **python-server** | `/opt/python3.12/.../site-packages/app/` | Python (FastAPI) |
| **Config files** | `/opt/gem/` | Shell scripts, JSON, nginx |
| **MCP config** | `/opt/gem/mcp-hub.json` | JSON |
| **Entrypoint** | `/opt/gem/run.sh` | Bash |
| **Process manager** | `/opt/gem/supervisord/` | Supervisord configs |

### Server Code Analysis

**gem-server** (`/opt/gem-server/src/gem/server.py`):
```python
# Clean FastAPI app - routers for auth, cdp, gui, ping
api = FastAPI(
    title="Environment Service",
    description="API for controlling environment and proxying CDP.",
)
```

**python-server** (`/opt/python3.12/.../app/server.py`):
```python
# Service container pattern - registers local services only
services.register('sandbox_service', SandboxService())
services.register('mcp_client', MCPClient())
services.register('jupyter_service', JupyterService())
# ... all local services
```

### Entrypoint Analysis

**run.sh** key finding:
```bash
export OTEL_SDK_DISABLED=true  # OpenTelemetry disabled
```

---

## Security Checks

### 1. Telemetry/Analytics Search

```bash
grep -r "telemetry|analytics|tracking|beacon|sentry|datadog" /opt/gem-server/src/ /opt/.../app/
```

**Result:** Only found "tracking" in a code comment about WebSocket logging state. No telemetry.

### 2. External URLs Search

```bash
grep -r "https://|http://" ... | grep -v "localhost|127.0.0.1"
```

**Result:** Only GitHub issue URLs in code comments. No external endpoints.

### 3. Config External Endpoints

**MCP Hub Config** (`/opt/gem/mcp-hub.json`):
```json
{
  "mcpServers": {
    "sandbox": { "url": "http://127.0.0.1:8091/mcp" },
    "browser": { "url": "http://127.0.0.1:8100/mcp" },
    "chrome_devtools": { "command": "/usr/bin/chrome-devtools-mcp" }
  }
}
```
All localhost - no external servers.

### 4. Background Jobs

| Check | Result |
|-------|--------|
| Crontab | Not installed |
| Supervisord | Standard services only (browser, nginx, vnc, jupyter, code-server, mcp) |

### 5. Listening Ports

| Port | Service | Binding |
|------|---------|---------|
| 8080 | Nginx gateway | 0.0.0.0 (exposed) |
| 8079 | MCP hub | 0.0.0.0 |
| 8088 | Gem server | 0.0.0.0 |
| 8091 | Python server | 0.0.0.0 |
| 8100 | MCP browser | 0.0.0.0 |
| 8200 | Code server | 0.0.0.0 |
| 8888 | Jupyter | 0.0.0.0 |
| 5900 | VNC | **localhost** |
| 9222 | Chrome CDP | **localhost** |
| 6080 | VNC WebSocket | 0.0.0.0 |

VNC and CDP properly bound to localhost only.

---

## Findings

### No Evidence Found

| Risk | Evidence |
|------|----------|
| **Malware** | No hidden code, backdoors, or suspicious patterns |
| **Data Exfiltration** | No telemetry, no external data transmission |
| **Hidden Remote Servers** | All configs point to localhost, no undocumented endpoints |

### Positive Indicators

- OpenTelemetry explicitly disabled (`OTEL_SDK_DISABLED=true`)
- Code-server runs with `--disable-telemetry`
- Clean FastAPI server code with no external dependencies
- VNC/CDP bound to localhost for security
- Apache 2.0 license, publicly auditable
- Active development with 1.8k stars

### Minor Observations

| Observation | Impact |
|-------------|--------|
| Server code not in GitHub source repo | Must inspect Docker image (done) |
| ByteDance/VolcEngine affiliation | Known, not hidden. VolcEngine provider only for cloud deployment |
| No SECURITY.md | Minor - no formal vulnerability disclosure process |

---

## Verdict

**APPROVED for Dev Lab use.**

No evidence of malware, data exfiltration, or hidden remote servers. The codebase is clean, standard FastAPI applications with all configs pointing to localhost.

---

## References

- [AIO Sandbox GitHub](https://github.com/agent-infra/sandbox)
- [ByteDance UI-TARS Desktop](https://github.com/bytedance/UI-TARS-desktop) (uses AIO Sandbox)
- [Context7 Documentation](https://context7.com/agent-infra/sandbox)
