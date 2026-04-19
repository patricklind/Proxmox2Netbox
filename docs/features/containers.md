# LXC Containers

Proxmox LXC containers are synced to NetBox in the same way as QEMU VMs — as
`virtualization.VirtualMachine` objects — when `sync_lxc_containers` is enabled
on the endpoint.

## What gets synced

| Proxmox field | NetBox field |
|---|---|
| Container name | Virtual machine name |
| Node name | Cluster node |
| Cluster name | Cluster |
| vCPU count | vCPUs |
| Memory (MB) | Memory (MB) |
| Container state | Status (`active` / `offline`) |

## Interfaces and IPs

LXC container network interfaces (`net0`, `net1`, …) are synced as `VMInterface` objects with MAC addresses.

IP assignment follows the same logic as for QEMU VMs:
- Static IPs from container config
- Only plugin-managed stale IPs are removed, and only when `prune_stale_vm_ips`
  is enabled and authoritative Proxmox IP data exists

> Note: LXC containers do not support the QEMU guest agent, so the guest-agent IP fallback is not available for containers.
