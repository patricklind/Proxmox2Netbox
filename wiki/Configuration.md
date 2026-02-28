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
