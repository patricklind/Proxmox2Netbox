# Configuration

## Proxmox Endpoint

Create at least one endpoint in:

`Plugins -> Proxmox2NetBox -> Endpoints -> Proxmox Endpoints`

Required endpoint data:

- `name`
- `domain` and/or `ip_address`
- `username`
- `password` or (`token_name` + `token_value`)

Optional endpoint data:

- `port` (default `8006`)
- `verify_ssl`
- `netbox_site` — NetBox Site to assign synced nodes and VMs to
- `netbox_vrf` — NetBox VRF to assign synced IP addresses to
- `netbox_device_type` — NetBox DeviceType for synced Proxmox nodes (e.g. *Dell PowerEdge R740*); falls back to generic *Proxmox Node* if not set

## Endpoint sync controls

Each endpoint has switches for what sync is allowed to create, update, and prune:

- `sync_enabled` — include or skip this endpoint
- `sync_nodes` — Proxmox nodes as NetBox devices
- `sync_qemu_vms` — QEMU virtual machines
- `sync_lxc_containers` — LXC containers as NetBox virtual machines
- `sync_vm_interfaces` — VM interfaces from Proxmox config
- `sync_vm_ips` — VM interface IP addresses
- `sync_guest_agent_ips` — QEMU guest-agent IP fallback when static config has no IPs
- `sync_vm_disks` — NetBox virtual disks from Proxmox disk config
- `prune_stale_vm_interfaces` — delete plugin-managed VM interfaces missing from Proxmox
- `prune_stale_vm_ips` — delete plugin-managed IPs missing from Proxmox
- `prune_stale_vm_disks` — delete plugin-managed virtual disks missing from Proxmox

Defaults preserve the previous behavior: endpoint enabled, all object types
synced, and stale plugin-managed VM interfaces/IPs/disks pruned.

## NetBox permissions

Grant permissions through standard NetBox object permissions:

- open plugin home/status cards: `view` on `proxmox2netbox.ProxmoxEndpoint`
- run manual sync actions or change sync schedule: `change` on `proxmox2netbox.ProxmoxEndpoint`
- manage endpoints: `view/add/change/delete` on `proxmox2netbox.ProxmoxEndpoint`
- view sync history: `view` on `proxmox2netbox.SyncProcess`
- manage node device type mappings: `view/add/change/delete` on `proxmox2netbox.ProxmoxNodeTypeMapping`

## Authentication

Supported modes:

- Username + password
- Username + API token (`token_name`, `token_value`)

## Per-Node Device Type Mapping

For fine-grained control over individual node hardware types, use:

`Plugins -> Proxmox2NetBox -> Configuration -> Node Type Mappings`

Map a specific node name (e.g. `pve01`) to a specific NetBox DeviceType. This overrides the endpoint-level device type for that node. Nodes without a mapping use the endpoint default (or the generic fallback).

## Notes

- Plugin performs direct calls to Proxmox API from NetBox runtime.
- Missing optional fields should not block sync unless endpoint cannot authenticate.
