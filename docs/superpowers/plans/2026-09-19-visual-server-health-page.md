# visual_server 健康检查页 Implementation Plan

> **For agentic workers:** Steps use checkbox syntax. User requested immediate implementation after spec approval.

**Goal:** Dedicated `/health` page with PG/RQ/CLI checks; remove header health polls; CLI path from Settings.

**Architecture:** Light `/api/health` unchanged; authenticated `/api/system/status` runs subprocess probe with `CLI_*` settings; frontend Health page + AppShell cleanup.

**Tech Stack:** FastAPI, React/Ant, subprocess

## Global Constraints

- Probe = A (callable via `-h`), no dry-run
- Header health dots fully removed
- Do not change worker job launch in this round

---

### Task 1: Backend CLI config + probe + status API
- [x] Settings: `cli_python`, `cli_module`, `cli_cwd`, `cli_probe_args`
- [x] `check_cli()` + `system_status_payload`
- [x] `GET /api/system/status` (auth)
- [x] Schemas `SystemStatusOut`

### Task 2: Frontend Health page + shell cleanup
- [x] `Health.tsx`, route, menu, `api.systemStatus`
- [x] Remove header dots and health polling from AppShell

### Task 3: Restart + verify
- [x] Restart BE with DATA_ROOTS; hit status API; confirm health still light
- [x] Lazy-import in `ms_mosaic/__main__.py` so `-h` works without heavy deps
