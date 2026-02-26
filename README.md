# Proxmox2NetBox

NetBox plugin for synchronizing Proxmox inventory data into NetBox (NetBox v4).

## Compatibility

- NetBox: `>=4.2.0, <5.0.0`
- Python: `>=3.8`
- Plugin package version in this repository: `1.1.3`

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
- Job wrapper: `netbox_proxbox/jobs.py` (`Proxmox2NetBoxSyncJob`)

## Installation (NetBox v4)

### 1. Install plugin package

Inside NetBox environment:

```bash
pip install proxmox2netbox
```

If you run `netbox-docker`, also pin the package in your Docker requirements file so it survives rebuilds/redeploys:

```text
# local_requirements.txt
proxmox2netbox==1.1.3
```

### 2. Enable plugin

In NetBox `configuration.py`:

```python
PLUGINS = ["proxmox2netbox"]
```

### 3. Run migrations/static

```bash
python manage.py migrate
python manage.py collectstatic --no-input
```

## Configure and Run Sync

### Configure Proxmox Endpoint

In NetBox UI:

- `Plugins -> Proxmox2NetBox -> Endpoints -> Proxmox Endpoints`
- Create at least one endpoint with:
  - `username`
  - either `password` **or** (`token_name` + `token_value`)
  - host via `domain` and/or `ip_address`

### Run sync from UI

- `Plugins -> Proxmox2NetBox -> Full Update`
- Available actions:
  - `Sync Nodes`
  - `Sync Virtual Machines`
  - `Full Update Sync`

### Run sync as NetBox Job (wrapper)

`jobs.py` provides a queue-compatible wrapper around the existing service layer.

Example from NetBox shell:

```python
from netbox_proxbox.jobs import Proxmox2NetBoxSyncJob
from netbox_proxbox.choices import SyncTypeChoices

# Full sync
Proxmox2NetBoxSyncJob.enqueue(sync_type=SyncTypeChoices.ALL)

# Devices only
Proxmox2NetBoxSyncJob.enqueue(sync_type=SyncTypeChoices.DEVICES)

# Virtual machines only
Proxmox2NetBoxSyncJob.enqueue(sync_type=SyncTypeChoices.VIRTUAL_MACHINES)
```

Behavior note:

- Job class is an orchestrator only.
- Sync mapping, payloads, and upsert logic remain in `services/proxmox_sync.py`.

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

- You must have access to the [`proxmox2netbox`](https://pypi.org/project/proxmox2netbox/) project on PyPI.
- If the name is unavailable for your account, change `project.name` in `pyproject.toml` to a unique name before publishing.
- Configure one of these publish methods:
- Add `PYPI_API_TOKEN` as a repository secret in GitHub, or
- Configure a matching Trusted Publisher in PyPI for this GitHub repository/workflow:
- Owner: `patricklind`
- Repository: `Proxmox2Netbox`
- Workflow file: `.github/workflows/publish-python-package.yml`
- Environment name: `pypi`

### Local preflight

```bash
python -m build
twine check dist/*
```

### Publish via GitHub Actions

- Bump `version` in `pyproject.toml` and plugin config version in source.
- Create and push a tag:

```bash
git tag -a vX.Y.Z -m "Release vX.Y.Z"
git push origin vX.Y.Z
```

- `release.yml` creates the GitHub Release from the tag and dispatches package publish.
- `publish-python-package.yml` publishes to PyPI (release event and manual/dispatch supported).
- After publish:

```bash
pip install proxmox2netbox
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

## Scope

This repository ships a NetBox plugin runtime only.  
Legacy FastAPI/backend-service components are removed from runtime, docs, and packaging scope.

## Wiki

- GitHub Wiki URL: `https://github.com/patricklind/Proxmox2Netbox/wiki`
- Wiki source files in this repository: `wiki/`
