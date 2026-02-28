# Virtual Machine (Data Model)

Proxmox QEMU VMs and LXC containers are represented in NetBox as `virtualization.VirtualMachine`.

## Fields populated by sync

| NetBox field | Source |
|---|---|
| `name` | VM/container name from Proxmox |
| `cluster` | Proxmox cluster → NetBox Cluster |
| `vcpus` | vCPU count |
| `memory` | Memory in MB |
| `status` | `active` (running) / `offline` (stopped) |

## Related objects created by sync

| NetBox model | Source |
|---|---|
| `virtualization.VMInterface` | `net0`, `net1`, … from Proxmox VM config |
| `dcim.MACAddress` | MAC from `net` config key; set as `primary_mac_address` |
| `ipam.IPAddress` | Static IPs from VM config or QEMU guest agent |

## Cluster and site

- The Proxmox cluster is synced as a NetBox `virtualization.Cluster`.
- If `netbox_site` is set on the endpoint, the cluster is scoped to that site (via the `scope` generic FK on NetBox 4.x Cluster).
