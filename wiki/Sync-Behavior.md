# Sync Behavior

## Covered objects

- Proxmox nodes -> NetBox `dcim.Device`
- QEMU/LXC VMs -> NetBox `virtualization.VirtualMachine`
- VM interfaces -> NetBox `virtualization.VMInterface`
- Virtual disks -> add/update/delete per VM
- Endpoint metadata refresh (`mode`, `version`, `repoid`, cluster name)

## IP assignment (best effort)

- Plugin attempts interface IP assignment only when data is available and deterministic.
- Sync must not fail if IP information is missing or ambiguous.

## Execution paths

- UI actions in plugin views
- NetBox Job wrapper: `Proxmox2NetBoxSyncJob`

## Stability guarantees

- Sync mapping and flow should not be changed without test coverage and explicit documentation.
