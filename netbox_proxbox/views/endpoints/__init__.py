from .fastapi import (
    FastAPIEndpointDeleteView,
    FastAPIEndpointEditView,
    FastAPIEndpointListView,
    FastAPIEndpointView,
)
from .netbox import (
    NetBoxEndpointDeleteView,
    NetBoxEndpointEditView,
    NetBoxEndpointListView,
    NetBoxEndpointView,
)
from .proxmox import (
    ProxmoxEndpointDeleteView,
    ProxmoxEndpointEditView,
    ProxmoxEndpointListView,
    ProxmoxEndpointView,
)

__all__ = (
    "FastAPIEndpointDeleteView",
    "FastAPIEndpointEditView",
    "FastAPIEndpointListView",
    "FastAPIEndpointView",
    "NetBoxEndpointDeleteView",
    "NetBoxEndpointEditView",
    "NetBoxEndpointListView",
    "NetBoxEndpointView",
    "ProxmoxEndpointDeleteView",
    "ProxmoxEndpointEditView",
    "ProxmoxEndpointListView",
    "ProxmoxEndpointView",
)
