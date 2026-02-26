# Netbox plugin related import
from django.apps import apps
from netbox.plugins import PluginConfig

class Proxmox2NetBoxConfig(PluginConfig):
    name = "netbox_proxbox"
    verbose_name = "Proxmox2NetBox"
    description = "Integrates Proxmox and Netbox"
    version = "1.1.3"
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
        # Allow PLUGINS = ["proxmox2netbox"] while keeping legacy app label/migrations.
        original_get_app_config = apps.get_app_config
        if getattr(original_get_app_config, "__proxbox_alias__", False):
            return

        def _get_app_config_with_alias(app_label):
            if app_label == "proxmox2netbox":
                app_label = "netbox_proxbox"
            return original_get_app_config(app_label)

        _get_app_config_with_alias.__proxbox_alias__ = True
        apps.get_app_config = _get_app_config_with_alias

config = Proxmox2NetBoxConfig
