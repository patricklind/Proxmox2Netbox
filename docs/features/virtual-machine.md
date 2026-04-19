# Virtual Machines

Proxmox QEMU VMs are synced to NetBox as `virtualization.VirtualMachine`
objects when `sync_qemu_vms` is enabled on the endpoint.

## What gets synced

| Proxmox field | NetBox field |
|---|---|
| VM name | Virtual machine name |
| Node name | Cluster node |
| Cluster name | Cluster |
| vCPU count | vCPUs |
| Memory (MB) | Memory (MB) |
| VM state | Status (`active` / `offline`) |

## Interfaces

Each network interface from the VM config (`net0`, `net1`, …) is created as a `virtualization.VMInterface`:

- Interface name is derived from the Proxmox config key (e.g. `net0`)
- MAC address is set as the `primary_mac_address` (NetBox 4.5+ `MACAddress` model)

## IP Addresses

IPs are assigned per interface — each interface only gets its own IPs.

**Sources (in priority order):**
1. Static IPs from Proxmox VM config (`ip=` field on `net0`, `net1`, …)
2. QEMU guest agent IPs, when `sync_guest_agent_ips` is enabled — matched to the correct interface by MAC address

**VRF:** IPs are placed in the VRF configured on the endpoint (if set).

**Stale cleanup:** plugin-managed IPs no longer present in Proxmox config are
removed from NetBox when `prune_stale_vm_ips` is enabled.

## Cluster placement

VMs are associated with the NetBox Cluster that corresponds to the Proxmox cluster.
If `netbox_site` is set on the endpoint, the cluster is scoped to that site.
