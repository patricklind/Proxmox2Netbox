# Network (IPAM)

## Interface sync

Each VM/container network interface (`net0`, `net1`, …) is synced as a `virtualization.VMInterface`.

- Interface name derived from Proxmox config key
- MAC address synced as `primary_mac_address` (NetBox 4.5+ `MACAddress` model)

## IP address sync

IPs are assigned per interface — each `VMInterface` only receives the IPs belonging to that interface.

**Source priority:**
1. Static IPs from Proxmox VM config (`ip=` / `ip6=` fields per `net` key)
2. QEMU guest agent — when `sync_guest_agent_ips` is enabled,
   `network-get-interfaces` is queried and IPs are matched to interfaces by MAC
   address (QEMU VMs only; not available for LXC)

**VRF placement:**
If `netbox_vrf` is set on the endpoint, all synced IPs are assigned to that VRF.

**Stale cleanup:**
Only IPs previously managed by `proxmox2netbox` are eligible for automatic
cleanup, and cleanup only runs when `prune_stale_vm_ips` is enabled. Manual IP
assignments in NetBox are preserved, and no cleanup is performed when Proxmox
provides no authoritative IP data for the interface.

## What is NOT synced

- Proxmox SDN (Software-Defined Networking) zones and VNets are not synced.
- Proxmox firewall rules are not synced.
- VLAN tags on VM interfaces are not currently synced to NetBox.
