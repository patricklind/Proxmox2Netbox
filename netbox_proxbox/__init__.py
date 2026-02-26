# Netbox plugin related import
from netbox.plugins import PluginConfig

class Proxmox2NetBoxConfig(PluginConfig):
    name = "netbox_proxbox"
    verbose_name = "Proxmox2NetBox"
    description = "Integrates Proxmox and Netbox"
    version = "1.1.1"
    author = "Patrick Wulff Lind"
    author_email = "mail@patricklind.dk"
    # Keep a floor for supported NetBox features and avoid blocking newer 4.x releases.
    min_version = "4.2.0"
    max_version = "4.99.99"
    base_url = "proxmox2netbox"
    required_settings = []

    def ready(self):
        super().ready()
        from . import jobs  # noqa: F401

config = Proxmox2NetBoxConfig
