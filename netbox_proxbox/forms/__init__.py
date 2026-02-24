from .fastapi import FastAPIEndpointFilterForm, FastAPIEndpointForm
from .netbox import NetBoxEndpointFilterForm, NetBoxEndpointForm
from .proxmox import ProxmoxEndpointFilterForm, ProxmoxEndpointForm
from .sync_process import SyncProcessFilterForm, SyncProcessForm
from .vm_backup import VMBackupFilterForm, VMBackupForm

__all__ = (
    "FastAPIEndpointFilterForm",
    "FastAPIEndpointForm",
    "NetBoxEndpointFilterForm",
    "NetBoxEndpointForm",
    "ProxmoxEndpointFilterForm",
    "ProxmoxEndpointForm",
    "SyncProcessFilterForm",
    "SyncProcessForm",
    "VMBackupFilterForm",
    "VMBackupForm",
)
        
