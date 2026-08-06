# Agent Dashboard — Backend

Python/FastAPI backend for KZTEK Agent Dashboard.

## Quick start

```powershell
cd tools/agent-dashboard/backend
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -r requirements.txt
python -m agent_dashboard       # starts on http://localhost:7770
```

## Environment variables

| Variable | Default | Description |
|---|---|---|
| `DASHBOARD_PORT` | `7770` | HTTP port |
| `DASHBOARD_HOST` | `0.0.0.0` | Bind address |
| `IDLE_THRESHOLD_SEC` | `300` | Seconds before Running → Idle |
| `ENDED_THRESHOLD_SEC` | `1800` | Seconds before Idle → Ended |
| `POLLING_INTERVAL_MS` | `500` | watchdog poll interval (Windows) |
| `DATA_DIR` | `backend/data/` | SQLite + accounts.enc location |
| `FORCE_NATIVE_WATCHER` | unset | Set to `1` to use native watcher on Windows |

## Run tests

```powershell
pip install pytest pytest-asyncio
pytest -q
```
