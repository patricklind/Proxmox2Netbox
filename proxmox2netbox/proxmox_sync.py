"""Compatibility shim for the Proxmox sync service layer.

The sync implementation lives in ``proxmox2netbox.services.proxmox_sync``.
Keep importing from ``proxmox2netbox.proxmox_sync`` to avoid breaking
existing callers.
"""

from proxmox2netbox.services.proxmox_sync import (
    ProxmoxSyncError,
    check_endpoint_connection,
    connect_endpoint,
    get_endpoint_cluster_summary,
    sync_devices,
    sync_full_update,
    sync_virtual_machines,
)

__all__ = [
    "ProxmoxSyncError",
    "check_endpoint_connection",
    "connect_endpoint",
    "get_endpoint_cluster_summary",
    "sync_devices",
    "sync_full_update",
    "sync_virtual_machines",
]
