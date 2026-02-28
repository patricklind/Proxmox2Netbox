# Network (IPAM)

## Interface sync

Each VM/container network interface (`net0`, `net1`, …) is synced as a `virtualization.VMInterface`.

- Interface name derived from Proxmox config key
- MAC address synced as `primary_mac_address` (NetBox 4.5+ `MACAddress` model)

## IP address sync

IPs are assigned per interface — each `VMInterface` only receives the IPs belonging to that interface.

**Source priority:**
1. Static IPs from Proxmox VM config (`ip=` / `ip6=` fields per `net` key)
2. QEMU guest agent — `network-get-interfaces` queried and IPs matched to interfaces by MAC address (QEMU VMs only; not available for LXC)

**VRF placement:**
If `netbox_vrf` is set on the endpoint, all synced IPs are assigned to that VRF.

**Stale cleanup:**
IPs present in NetBox but no longer in Proxmox config are removed. This runs on every sync — even when the interface has no IPs configured, old IPs are cleaned up.

## What is NOT synced

- Proxmox SDN (Software-Defined Networking) zones and VNets are not synced.
- Proxmox firewall rules are not synced.
- VLAN tags on VM interfaces are not currently synced to NetBox.
