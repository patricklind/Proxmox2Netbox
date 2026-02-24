# netbox-proxbox

NetBox plugin for synchronizing Proxmox inventory data into NetBox (NetBox v4).

## Compatibility

- NetBox: `>=4.2.0, <5.0.0`
- Python: `>=3.8`
- Plugin package version in this repository: `0.0.6b2`

## What Works (Current Runtime)

Out-of-the-box sync requires only a configured **Proxmox Endpoint** in NetBox.

Implemented sync flows:

- Proxmox nodes -> NetBox `dcim.Device`
- Proxmox QEMU/LXC VMs -> NetBox `virtualization.VirtualMachine`
- VM interfaces from Proxmox config -> NetBox `virtualization.VMInterface`
- Endpoint metadata refresh (`mode`, `version`, `repoid`, cluster name)
- Sync process tracking in `SyncProcess`

## Runtime Architecture (Source of Truth)

Core sync logic is consolidated in:

- `netbox_proxbox/services/proxmox_sync.py`

Backward-compatible import shim (kept intentionally):

- `netbox_proxbox/proxmox_sync.py`

Primary runtime entrypoints:

- UI endpoints: `netbox_proxbox/views/sync.py`
- Connection/status badge: `netbox_proxbox/views/keepalive_status.py`
- Proxmox card data: `netbox_proxbox/views/cards.py`
- Job wrapper: `netbox_proxbox/jobs.py` (`ProxboxSyncJob`)

## Installation (NetBox v4)

### 1. Install plugin package

Inside NetBox environment:

```bash
pip install netbox-proxbox
```

### 2. Enable plugin

In NetBox `configuration.py`:

```python
PLUGINS = ["netbox_proxbox"]
```

### 3. Optional `PLUGINS_CONFIG`

No required plugin settings for core sync.

Optional legacy FastAPI/backend-service controls (only used by legacy backend service views):

```python
PLUGINS_CONFIG = {
    "netbox_proxbox": {
        "fastapi": {
            "sudo": {
                "user": "",
                "password": "",
            }
        }
    }
}
```

### 4. Run migrations/static

```bash
python manage.py migrate netbox_proxbox
python manage.py collectstatic --no-input
```

## Configure and Run Sync

### Configure Proxmox Endpoint

In NetBox UI:

- `Plugins -> Proxbox -> Endpoints -> Proxmox Endpoints`
- Create at least one endpoint with:
  - `username`
  - either `password` **or** (`token_name` + `token_value`)
  - host via `domain` and/or `ip_address`

### Run sync from UI

- `Plugins -> Proxbox -> Full Update`
- Available actions:
  - `Sync Nodes`
  - `Sync Virtual Machines`
  - `Full Update Sync`

### Run sync as NetBox Job (wrapper)

`jobs.py` provides a queue-compatible wrapper around the existing service layer.

Example from NetBox shell:

```python
from netbox_proxbox.jobs import ProxboxSyncJob
from netbox_proxbox.choices import SyncTypeChoices

# Full sync
ProxboxSyncJob.enqueue(sync_type=SyncTypeChoices.ALL)

# Devices only
ProxboxSyncJob.enqueue(sync_type=SyncTypeChoices.DEVICES)

# Virtual machines only
ProxboxSyncJob.enqueue(sync_type=SyncTypeChoices.VIRTUAL_MACHINES)
```

Behavior note:

- Job class is an orchestrator only.
- Sync mapping, payloads, and upsert logic remain in `services/proxmox_sync.py`.

## FastAPI / WebSocket Status

FastAPI/WebSocket components are **not required** for core Proxmox -> NetBox sync runtime.
They are kept for legacy compatibility paths and should be treated as optional unless explicitly needed in your deployment.

## Development & Validation

### Static checks

```bash
ruff check netbox_proxbox --select F401,F403,F811,F821,F841,E712
python -m compileall -q netbox_proxbox
```

### Django checks (inside NetBox runtime)

```bash
python manage.py check
python manage.py makemigrations --check --dry-run
```

### Tests

Current repository state contains no active pytest test modules.

```bash
pytest
# expected: no tests ran
```

## Publish to PyPI

### Prerequisites

- You must own the `netbox-proxbox` project on PyPI.
- If the name is unavailable for your account, change `project.name` in `pyproject.toml` to a unique name before publishing.
- Add `PYPI_API_TOKEN` as a repository secret in GitHub.

### Local preflight

```bash
python -m build
twine check dist/*
```

### Publish via GitHub Actions

- Create a GitHub Release (or run the `Publish Python Package` workflow manually).
- The workflow builds and uploads distributions to PyPI.
- After publish:

```bash
pip install netbox-proxbox
```

## Repository Layout (Relevant Runtime Files)

```text
netbox_proxbox/
  __init__.py
  jobs.py
  models/
  services/
    proxmox_sync.py
  proxmox_sync.py          # compatibility shim
  views/
    sync.py
    keepalive_status.py
    cards.py
  urls.py
  forms/
  filtersets.py
  tables/
```

## Legacy/Needs-Review Areas

The following are kept to avoid accidental runtime regressions, but are not part of core sync runtime:

- `netbox_proxbox/websocket_client.py`
- `netbox_proxbox/views/proxbox_backend.py`
- `FASTAPI.md` and other legacy backend-oriented docs
