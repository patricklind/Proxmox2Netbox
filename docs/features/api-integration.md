# API Integration

## Proxmox API

The plugin connects directly to the Proxmox VE REST API from the NetBox runtime.

**Authentication modes:**
- Username + password (`root@pam` style)
- Username + API token (`token_name` + `token_value`)

**Endpoints used:**
- `/api2/json/nodes` — list cluster nodes
- `/api2/json/nodes/{node}/qemu` — list QEMU VMs
- `/api2/json/nodes/{node}/lxc` — list LXC containers
- `/api2/json/nodes/{node}/qemu/{vmid}/config` — VM config (interfaces, IPs)
- `/api2/json/nodes/{node}/qemu/{vmid}/agent/network-get-interfaces` — guest agent IPs (QEMU only)
- `/api2/json/cluster/status` — cluster name and node membership

## NetBox REST API (plugin endpoints)

The plugin exposes its own models via NetBox's REST API under `/api/plugins/proxmox2netbox/`.

Available endpoints:
- `/api/plugins/proxmox2netbox/endpoints/` — `ProxmoxEndpoint` CRUD
- `/api/plugins/proxmox2netbox/sync-processes/` — `SyncProcess` read

The serializers expose all endpoint fields including `netbox_site`, `netbox_vrf`, and `netbox_device_type`.
