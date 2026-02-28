# Storage

> **Not currently synced.** Proxmox storage pools and disk configuration are not synced to NetBox by this plugin.

## Current state

The plugin does not read Proxmox storage pool data (`/api2/json/nodes/{node}/storage`) or map it to NetBox objects.

VM disk sizes visible in Proxmox are not currently written to NetBox `VirtualDisk` objects.

## What IS synced

The plugin syncs:
- Proxmox nodes → NetBox devices
- VMs and LXC containers → NetBox virtual machines
- VM network interfaces and IPs → NetBox VMInterfaces and IP addresses

## Future

Storage sync (e.g. disk size on VMs, storage pool inventory) may be considered in a future release.
