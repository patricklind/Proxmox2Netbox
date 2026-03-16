# Proxmox2NetBox

Proxmox2NetBox is a NetBox v4 plugin that synchronizes Proxmox inventory data into NetBox.

## Runtime Scope

This project is plugin-only:

- No external FastAPI service is required.
- No separate backend deployment is required.
- Sync runs directly from the NetBox plugin UI and NetBox jobs.

## Compatibility

- NetBox: `>=4.2.0, <5.0.0`
- Python: `>=3.8`
- Proxmox VE: `>=8.x` (tested baseline)

## What Sync Covers

- Proxmox nodes → NetBox `dcim.Device`
- Proxmox QEMU/LXC VMs → NetBox `virtualization.VirtualMachine`
- VM interfaces → NetBox `virtualization.VMInterface` with per-interface IP assignment
- QEMU guest-agent IPs as fallback when static VM config has no IPs (MAC-based interface matching)
- Plugin-managed stale IPs removed when authoritative Proxmox IP data exists
- Endpoint-level Site and VRF mapping (devices/IPs placed in the configured NetBox Site/VRF)
- Per-endpoint Node Device Type (real hardware model, e.g. Dell PowerEdge R740)
- Per-node Device Type Mapping for individual node overrides
- Endpoint metadata refresh (`mode`, `version`, `repoid`, cluster name)
- Sync process tracking (`SyncProcess`)

## Quick Start

1. Install the package in NetBox venv: `pip install proxmox2netbox`
2. Enable plugin in NetBox config: `PLUGINS = ["proxmox2netbox"]`
3. Run migrations/static collection.
4. Add at least one Proxmox endpoint in plugin UI.
5. Run sync from plugin home page or queue the NetBox job.

## Installation Guides

- [Installing using pip](./installation/1-installing-plugin.md)
- [Installing using git](./installation/2-installing-plugin-git.md)
- [Installing using Docker](./installation/3-installing-plugin-docker.md)
