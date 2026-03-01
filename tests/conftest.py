"""
Pytest configuration for Proxmox2NetBox unit tests.

Stubs out all NetBox / Django modules so the plugin package can be imported
without a running Django application.  Tests in this suite only cover pure
utility functions that have no side effects and no DB dependencies.
"""
import sys
import types


def _stub(name: str, **attrs):
    """Create and register a stub module with optional attributes."""
    mod = types.ModuleType(name)
    for k, v in attrs.items():
        setattr(mod, k, v)
    sys.modules[name] = mod
    return mod


# ---------------------------------------------------------------------------
# netbox stubs
# ---------------------------------------------------------------------------
class _PluginConfig:
    """Minimal PluginConfig stub."""
    name = ""
    verbose_name = ""
    description = ""
    version = ""
    author = ""
    author_email = ""
    min_version = ""
    max_version = ""
    base_url = ""
    required_settings = []

    def ready(self):
        pass


_stub("netbox")
_stub("netbox.plugins", PluginConfig=_PluginConfig)
_stub("netbox.models")
_stub("netbox.jobs", JobFailed=Exception, JobRunner=object)
_stub("netbox.context")

# ---------------------------------------------------------------------------
# Django stubs (minimal — only what's needed for the import chain)
# ---------------------------------------------------------------------------
_django = _stub("django")
_stub("django.db", models=types.ModuleType("django.db.models"))
_django_models = _stub("django.db.models")
_django_models.Model = object
_django_models.CharField = lambda **kw: None
_django_models.BooleanField = lambda **kw: None
_django_models.ForeignKey = lambda **kw: None
_django_models.PositiveIntegerField = lambda **kw: None

_stub("django.contrib")
_stub("django.contrib.contenttypes")
_stub("django.contrib.contenttypes.models", ContentType=object)
_stub("django.core")
_stub("django.core.validators", MaxValueValidator=lambda x: None, MinValueValidator=lambda x: None)
_stub("django.core.exceptions", ValidationError=Exception)
_stub("django.urls", reverse=lambda *a, **kw: "/")
_stub("django.utils")
_stub("django.utils.translation", gettext_lazy=lambda s: s)
_stub("django.utils.timezone")

# ---------------------------------------------------------------------------
# NetBox app stubs
# ---------------------------------------------------------------------------
for _app in (
    "dcim", "dcim.models",
    "ipam", "ipam.models",
    "extras", "extras.models", "extras.models.tags", "extras.choices",
    "virtualization", "virtualization.models",
    "users", "users.models",
    "taggit", "taggit.managers",
    "utilities", "utilities.json",
):
    _stub(_app)

# Stub proxmoxer so proxmox_sync can be imported
_stub("proxmoxer", ProxmoxAPI=object)
