# Netbox plugin related import
from netbox.plugins import PluginConfig

class ProxboxConfig(PluginConfig):
    name = "netbox_proxbox"
    verbose_name = "Proxbox"
    description = "Integrates Proxmox and Netbox"
    version = "0.0.6b2"
    author = "Emerson Felipe (@emersonfelipesp)"
    author_email = "emersonfelipe.2003@gmail.com"
    # Keep a floor for supported NetBox features and avoid blocking newer 4.x releases.
    min_version = "4.2.0"
    max_version = "4.99.99"
    base_url = "proxbox"
    required_settings = []

    def ready(self):
        super().ready()
        from . import jobs  # noqa: F401

config = ProxboxConfig
