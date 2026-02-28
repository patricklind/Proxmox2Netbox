# Synchronized Data

## Proxmox Nodes → NetBox Devices

Each Proxmox cluster node is synced as a `dcim.Device`.

| Proxmox field | NetBox field |
|---|---|
| Node name | Device name |
| Cluster name | Cluster (virtualization) |
| Endpoint site | Device site |
| Device type (endpoint or mapping) | Device type |

**Device type priority:**
1. Per-node mapping (`ProxmoxNodeTypeMapping`) — if the node name has an explicit mapping
2. Endpoint `netbox_device_type` — if set on the endpoint
3. Generic *Proxmox Node* fallback (auto-created, manufacturer: *Proxmox*)

## VMs and Containers → NetBox Virtual Machines

QEMU VMs and LXC containers are synced as `virtualization.VirtualMachine`.

| Proxmox field | NetBox field |
|---|---|
| VM name | Virtual machine name |
| Node name | Cluster node |
| Cluster name | Cluster |
| vCPU count | vCPUs |
| Memory (MB) | Memory |

## VM Interfaces → NetBox VMInterfaces

Each network interface from the Proxmox VM config (`net0`, `net1`, …) is synced as a `virtualization.VMInterface`.

| Proxmox field | NetBox field |
|---|---|
| Interface name | Interface name |
| MAC address | Primary MAC address |

## IP Addresses

IPs are synced per interface — each `VMInterface` only receives its own IPs.

**Sources (in priority order):**
1. Static IPs from Proxmox VM config (`ip=` field on `net0`, `net1`, …)
2. QEMU guest agent IPs (if guest agent is running) — matched to interface by MAC address

**VRF placement:** IPs are assigned to the VRF configured on the endpoint (if set).

**Stale cleanup:** IPs that are no longer present in Proxmox config are removed from NetBox.
