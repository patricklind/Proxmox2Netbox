# Containers (Data Model)

LXC containers are synced identically to QEMU VMs — both are represented as `virtualization.VirtualMachine` in NetBox.

## Fields populated by sync

| NetBox field | Source |
|---|---|
| `name` | Container name from Proxmox |
| `cluster` | Proxmox cluster → NetBox Cluster |
| `vcpus` | vCPU count |
| `memory` | Memory in MB |
| `status` | `active` (running) / `offline` (stopped) |

## Differences from QEMU VMs

- QEMU guest agent is not available for LXC containers — IP fallback via guest agent does not apply.
- Static IPs from the LXC container network config are synced normally.

## Related objects created by sync

| NetBox model | Source |
|---|---|
| `virtualization.VMInterface` | `net0`, `net1`, … from container config |
| `dcim.MACAddress` | MAC from `net` config key |
| `ipam.IPAddress` | Static IPs from container config |
