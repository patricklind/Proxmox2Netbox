# Configuration

Proxmox2NetBox is configured through the NetBox UI. No configuration file is required.

## Proxmox Endpoint

Create at least one endpoint under:

`Plugins → Proxmox2NetBox → Endpoints → Proxmox Endpoints`

### Required fields

| Field | Description |
|---|---|
| `name` | Display name for this endpoint |
| `domain` and/or `ip_address` | Proxmox host address |
| `username` | Proxmox user (e.g. `root@pam`) |
| `password` **or** `token_name` + `token_value` | Authentication credentials |

### Optional fields

| Field | Description |
|---|---|
| `port` | Proxmox API port (default: `8006`) |
| `verify_ssl` | TLS certificate verification (default: enabled) |
| `netbox_site` | NetBox Site to place synced nodes and VMs in |
| `netbox_vrf` | NetBox VRF to assign synced IP addresses to |
| `netbox_device_type` | NetBox DeviceType for synced Proxmox nodes (e.g. *Dell PowerEdge R740*) |

## Per-Node Device Type Mapping

For individual node hardware overrides, use:

`Plugins → Proxmox2NetBox → Configuration → Node Type Mappings`

Map a specific node hostname (e.g. `pve01`) to a specific NetBox DeviceType. Nodes without an explicit mapping use the endpoint-level device type, or the generic *Proxmox Node* fallback.

See [Required Parameters](./required-parameters.md) for the minimum setup before first sync.
