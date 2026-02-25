# Proxmox2NetBox Wiki

Proxmox2NetBox is a NetBox v4 plugin for synchronizing Proxmox inventory data into NetBox.

## Scope

- Plugin-only runtime (no separate FastAPI service)
- Sync runs from NetBox UI and NetBox Jobs
- Supports Proxmox endpoint auth via password or API token

## Quick Links

- [Installation](Installation)
- [Configuration](Configuration)
- [Sync Behavior](Sync-Behavior)
- [Release and PyPI](Release-and-PyPI)
- [Troubleshooting](Troubleshooting)

## Compatibility

- NetBox: `>=4.2.0, <5.0.0`
- Python: `>=3.8`
- Package: `proxmox2netbox`
- Plugin module name in NetBox: `netbox_proxbox`
