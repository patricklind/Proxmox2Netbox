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

## Endpoint Sync Controls

Each endpoint has switches for what the sync is allowed to touch:

| Field | Description |
|---|---|
| `sync_enabled` | Include or skip the endpoint entirely |
| `sync_nodes` | Create/update Proxmox nodes as NetBox devices |
| `sync_qemu_vms` | Create/update QEMU virtual machines |
| `sync_lxc_containers` | Create/update LXC containers as NetBox virtual machines |
| `sync_vm_interfaces` | Create/update VM interfaces from Proxmox network config |
| `sync_vm_ips` | Assign VM interface IPs from Proxmox config and guest-agent data |
| `sync_guest_agent_ips` | Use QEMU guest-agent data when static config has no IPs |
| `sync_vm_disks` | Create/update virtual disks from Proxmox disk config |
| `prune_stale_vm_interfaces` | Delete plugin-managed VM interfaces no longer reported by Proxmox |
| `prune_stale_vm_ips` | Delete plugin-managed interface IPs no longer reported by Proxmox |
| `prune_stale_vm_disks` | Delete plugin-managed virtual disks no longer reported by Proxmox |

Defaults preserve the previous behavior: all object types are synced and stale
plugin-managed VM interfaces, IPs, and disks are pruned.

## NetBox Permissions

For normal NetBox users, grant permissions through NetBox object permissions:

- Open the plugin home page and endpoint status cards: `view` on
  `proxmox2netbox.ProxmoxEndpoint`
- Run manual sync actions and change the sync schedule: `change` on
  `proxmox2netbox.ProxmoxEndpoint`
- Manage endpoints: `view/add/change/delete` on
  `proxmox2netbox.ProxmoxEndpoint`
- View sync history: `view` on `proxmox2netbox.SyncProcess`
- Manage node device type mappings: `view/add/change/delete` on
  `proxmox2netbox.ProxmoxNodeTypeMapping`

## Per-Node Device Type Mapping

For individual node hardware overrides, use:

`Plugins → Proxmox2NetBox → Configuration → Node Type Mappings`

Map a specific node hostname (e.g. `pve01`) to a specific NetBox DeviceType. Nodes without an explicit mapping use the endpoint-level device type, or the generic *Proxmox Node* fallback.

See [Required Parameters](./required-parameters.md) for the minimum setup before first sync.
