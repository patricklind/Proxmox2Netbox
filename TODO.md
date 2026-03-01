# TODO — Proxmox2Netbox

**Current version:** `v1.2.8` (tagged, pushed to GitHub, CI publishes to PyPI)
**State:** ruff clean · bandit 0 issues · 45 tests pass · no uncommitted changes

---

## Done ✅

| Area | Detail |
|---|---|
| Security: SSRF | `ContributingView` reads local `CONTRIBUTING.md` instead of calling GitHub API. `github.py` + `release.py` deleted. |
| Security: credential exposure | `password` + `token_value` marked `write_only=True` in `ProxmoxEndpointSerializer`. |
| Security: `verify_ssl` default | Changed `False` → `True`. Migration `0017` applied. |
| Security: bandit B105 | False-positive `# nosec B105` added to validation error messages in `serializers.py`. |
| Model: `netbox_device_type` FK | `ProxmoxEndpoint.netbox_device_type → dcim.DeviceType` (migration `0014`). |
| Model: `netbox_site` FK | `ProxmoxEndpoint.netbox_site → dcim.Site` (migration `0013`). |
| Model: `netbox_vrf` FK | `ProxmoxEndpoint.netbox_vrf → ipam.VRF` (migration `0013`). |
| Model: `ProxmoxNodeTypeMapping` | Per-node device type override table (migration `0015`). |
| Sync: device type | `_ensure_base_objects(device_type=...)` respects endpoint FK; falls back to `proxmox-node` generic type. |
| Sync: per-node mapping | `_sync_nodes` builds `node_type_map` from `ProxmoxNodeTypeMapping`; per-node type takes priority over endpoint default. |
| Sync: `netbox_site` + `netbox_vrf` | Passed through to cluster, IP assignment, and `_ensure_base_objects`. |
| Serializer | `netbox_site`, `netbox_vrf`, `netbox_device_type` exposed in API. |
| Form | `DynamicModelChoiceField` for `netbox_site`, `netbox_vrf`, `netbox_device_type`, `PasswordInput` widgets for credentials. |
| `ProxmoxEndpoint.__str__` | Handles `None` ip_address gracefully. |
| `CommonProperties.url` | Always returns `https://`; `verify_ssl` controls cert verification only. |
| Lint | ruff clean (F401, F841 fixed). |
| Tests: `_parse.py` | 45 unit tests (status, MAC, NIC, disk, IP parsing). Test runner works without Django. |
| CI | `.github/workflows/ci.yml` — lint, test matrix (3.11+3.12), build + twine check. |

---

## In Progress 🔄

Nothing actively in progress. All planned work from previous sessions is complete.

---

## Next — Prioritised Backlog

### P1 — Tests (highest gap: zero coverage on sync/model logic)

1. **`proxmox_sync.py` unit tests** — currently zero coverage on the Django-ORM-dependent functions. Strategy: extract pure-logic helpers (same pattern as `_parse.py`) and test those; mock ORM calls for the rest.
   - Functions with no test: `_safe_add_tag`, `_sync_iface_ips`, `_sync_iface_mac`, `_upsert_vm_interfaces`, `_sync_vm_disks`, `_set_vm_primary_ips`, `_sync_nodes`, `_sync_vms`, `_upsert_all_for_session`
   - Start file: `tests/test_sync_logic.py`
   - Approach: `conftest.py` stubs for `dcim.models`, `ipam.models`, `virtualization.models`

2. **Model validation tests** — `ProxmoxEndpoint.clean()` has 4 branches (password alone, token pair, mixed, neither). Currently untested.
   - Start file: `tests/test_model_validation.py`

3. **API serializer tests** — `write_only` fields, token validation in `validate()`.
   - Start file: `tests/test_serializer.py`

### P2 — Stale/cleanup logic for Proxmox nodes

Currently `_sync_nodes` collects `seen_names` but there is no stale node removal step.
Nodes that are decommissioned in Proxmox remain as `Device` objects in NetBox indefinitely.

- Add opt-in cleanup: `Device.objects.filter(cluster=cluster, tags=tag).exclude(name__in=seen_names)` → set `status='decommissioning'` or delete
- Needs a flag on `ProxmoxEndpoint` (e.g. `stale_node_cleanup: BooleanField(default=False)`)
- Migration required

### P3 — `FastAPIEndpoint` + `NetBoxEndpoint` dead code

`FastAPIEndpoint` and `NetBoxEndpoint` models exist for migration compatibility but are no longer used by any view, form, or sync function. They clutter the admin and add migration surface.

- Confirm no external consumers (check templates, views, API)
- Add a data migration that deletes existing rows (or gate behind `--noinput` confirmation)
- Remove model, forms, views, URLs, API endpoints
- Keep the migration chain intact (do NOT delete the migration, just add a removal migration)

### P4 — Broad `except Exception` in `proxmox_sync.py`

```
proxmox_sync.py:530 — except Exception: continue (VM fetch failure)
proxmox_sync.py:CommonProperties.url — except Exception: return "Error: {e}"
```

Both should log at `WARNING` level and use specific types where possible.

### P5 — CI: publish gate

Current `ci.yml` runs lint + test + build but does NOT block the PyPI publish if tests fail. Add a `needs: [lint, test]` dependency to the publish job in `.github/workflows/ci.yml` (or create `release.yml` if it doesn't exist).

---

## Known Risks / Clarifications

| Risk | Detail |
|---|---|
| `ProxmoxNodeTypeMapping` update semantics | On node UPDATE (device already exists), `device_type` is only changed when there is an explicit mapping row. The endpoint-level `netbox_device_type` is intentionally ignored for existing nodes. This is documented in code but may surprise users who change the endpoint default and expect existing nodes to be re-typed. |
| Migration dependency chain | Migrations `0013`→`0017` depend on each other in order. Any future migration must depend on `0017`. |
| `_ensure_base_objects` side-effects | Creates `Manufacturer('proxmox')`, `DeviceType('proxmox-node')`, `Site('proxmox2netbox')` on every sync if not present. These are owned by the plugin. If a user renames them in NetBox, they get recreated on next sync. |
| No rollback for stale nodes | There is no undo for node cleanup once implemented. Recommend `status=decommissioning` over hard-delete. |

---

## How to Resume

```bash
cd /opt/apps/Proxmox2Netbox

# Verify baseline
python3 -m pytest tests/ -q
python3 -m ruff check proxmox2netbox/
python3 -m bandit -r proxmox2netbox/ -ll

# Start next task (P1 — sync logic tests)
# Read the functions to test:
grep -n "^def " proxmox2netbox/services/proxmox_sync.py

# Run a migration check after any model changes:
python /opt/netbox/netbox/manage.py makemigrations --check proxmox2netbox

# Release flow (after version bump in pyproject.toml + __init__.py):
git tag -a vX.Y.Z -m "Release vX.Y.Z"
git push origin main && git push origin vX.Y.Z
```
