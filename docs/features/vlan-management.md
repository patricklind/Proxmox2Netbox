# VLAN Management

> **Not currently implemented.** VLAN sync from Proxmox to NetBox is not part of the current plugin scope.

## Current state

The plugin syncs VM network interfaces and their IP addresses, but does not create or update NetBox VLAN objects based on Proxmox data.

VLAN tags configured on Proxmox VM bridge interfaces are not currently read or mapped to NetBox VLANs.

## Workaround

VLANs should be managed directly in NetBox, either manually or via another sync tool (e.g. the UniFi sync plugin for network-level VLAN data).

## Future

VLAN sync may be added in a future release. Track progress in [GitHub Issues](https://github.com/patricklind/Proxmox2NetBox/issues).
