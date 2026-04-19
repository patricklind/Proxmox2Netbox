# Sync Behavior

## Covered objects

- Proxmox nodes → NetBox `dcim.Device`
- QEMU/LXC VMs → NetBox `virtualization.VirtualMachine`
- VM interfaces → NetBox `virtualization.VMInterface`
- Endpoint metadata refresh (`mode`, `version`, `repoid`, cluster name)
- Sync process tracking (`SyncProcess`)

Each endpoint can limit this scope. Endpoint controls decide whether nodes,
QEMU VMs, LXC containers, VM interfaces, VM IPs, guest-agent IP fallback,
virtual disks, and stale-object pruning are enabled for that endpoint.

## IP assignment

IPs are synced from Proxmox VM config (`net0`, `net1`, …) to each `VMInterface` individually.

- Each interface gets only its own IPs (keyed by interface index from Proxmox config).
- **QEMU guest agent fallback:** when enabled and VM config has no static IPs, the plugin queries the guest agent and matches IPs to interfaces by MAC address.
- Only IPs previously managed by `proxmox2netbox` are removed from NetBox during stale cleanup, and only when endpoint pruning is enabled.
- If Proxmox provides no authoritative IP data for an interface, existing NetBox IP assignments are preserved.
- IPs are assigned to the VRF configured on the endpoint (if set).

## Device type assignment (nodes)

Proxmox nodes are synced as NetBox `dcim.Device`. The device type is determined in this priority order:

1. **Per-node mapping** — if a `ProxmoxNodeTypeMapping` exists for the node name, that DeviceType is used.
2. **Endpoint device type** — if `netbox_device_type` is set on the endpoint, that DeviceType is used.
3. **Generic fallback** — a generic *Proxmox Node* DeviceType (manufacturer: *Proxmox*) is created and used.

## Site and VRF placement

- If `netbox_site` is set on the endpoint, synced nodes and VMs are placed in that NetBox Site.
- If `netbox_vrf` is set on the endpoint, synced IP addresses are assigned to that VRF.

## Execution paths

- UI actions in plugin views (`Plugins -> Proxmox2NetBox`)
- NetBox Job wrapper: `Proxmox2NetBoxSyncJob`

## Idempotency

Sync is idempotent — re-running produces the same result as the previous run. Objects are matched by stable keys (node name, VM name, interface name) and updated in place.
