"""Public plugin module alias for NetBox PLUGINS configuration.

Use `PLUGINS = ["proxmox2netbox"]` in NetBox.
The implementation lives in `netbox_proxbox` for backward compatibility.
"""

from netbox_proxbox import Proxmox2NetBoxConfig, config

__all__ = ["Proxmox2NetBoxConfig", "config"]

