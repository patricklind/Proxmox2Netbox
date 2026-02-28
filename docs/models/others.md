# Other Data Models

## ProxmoxEndpoint

Stores connection details and sync configuration for one Proxmox cluster.

Key fields: `name`, `domain`, `ip_address`, `port`, `username`, `password`, `token_name`, `token_value`, `verify_ssl`, `netbox_site`, `netbox_vrf`, `netbox_device_type`.

Managed via: `Plugins → Proxmox2NetBox → Endpoints → Proxmox Endpoints`

## ProxmoxNodeTypeMapping

Maps a specific Proxmox node hostname to a NetBox `DeviceType`.

Key fields: `endpoint` (FK to ProxmoxEndpoint), `node_name`, `device_type` (FK to `dcim.DeviceType`).

Managed via: `Plugins → Proxmox2NetBox → Configuration → Node Type Mappings`

When a sync runs, nodes are matched by name against this table. A match overrides the endpoint-level device type.

## SyncProcess

Records metadata about each sync execution.

Key fields: `endpoint`, `started`, `completed`, `status`.

Read-only in UI and REST API.

## NetBox objects created by sync

| NetBox model | Created by |
|---|---|
| `dcim.Manufacturer` | Auto-created as *Proxmox* for the generic device type |
| `dcim.DeviceType` | Generic *Proxmox Node* (auto-created) or selected from endpoint/mapping |
| `dcim.DeviceRole` | Auto-created as *Server* |
| `dcim.Device` | One per Proxmox node |
| `virtualization.ClusterType` | Auto-created as *Proxmox* |
| `virtualization.Cluster` | One per Proxmox cluster |
| `virtualization.VirtualMachine` | One per QEMU VM or LXC container |
| `virtualization.VMInterface` | One per `net` key in VM config |
| `dcim.MACAddress` | One per interface with a MAC address |
| `ipam.IPAddress` | One per configured or agent-reported IP |
