import pathlib

from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import render
from django.views import View

from .cards import get_proxmox_card
from .keepalive_status import get_service_status
from .endpoints import (
    ProxmoxEndpointDeleteView,
    ProxmoxEndpointEditView,
    ProxmoxEndpointListView,
    ProxmoxEndpointView,
)
from .sync import sync_devices, sync_full_update, sync_virtual_machines, get_sync_schedule, set_sync_schedule
from .sync_process import (
    SyncProcessAddView,
    SyncProcessDeleteView,
    SyncProcessEditView,
    SyncProcessListView,
    SyncProcessView,
)
from .node_type_mapping import (
    ProxmoxNodeTypeMappingView,
    ProxmoxNodeTypeMappingListView,
    ProxmoxNodeTypeMappingEditView,
    ProxmoxNodeTypeMappingDeleteView,
)

from proxmox2netbox.models import ProxmoxEndpoint

__all__ = (
    "ContributingView",
    "HomeView",
    "ProxmoxEndpointDeleteView",
    "ProxmoxEndpointEditView",
    "ProxmoxEndpointListView",
    "ProxmoxEndpointView",
    "ProxmoxNodeTypeMappingView",
    "ProxmoxNodeTypeMappingListView",
    "ProxmoxNodeTypeMappingEditView",
    "ProxmoxNodeTypeMappingDeleteView",
    "SyncProcessAddView",
    "SyncProcessDeleteView",
    "SyncProcessEditView",
    "SyncProcessListView",
    "SyncProcessView",
    "get_proxmox_card",
    "get_service_status",
    "get_sync_schedule",
    "set_sync_schedule",
    "sync_devices",
    "sync_full_update",
    "sync_virtual_machines",
)

class SuperuserRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_superuser


class HomeView(SuperuserRequiredMixin, View):
    """
    ## HomeView class-based view to handle incoming GET HTTP requests.
    
    ### Attributes:
    - **template_name (str):** The path to the HTML template used for rendering the view.
    
    ### Methods:
    - **get(request):**
            Handles GET requests to the view.
            Renders Proxmox endpoint overview for out-of-the-box sync.
            
            **Args:**
            - **request (HttpRequest):** The HTTP request object.
            
            **Returns:**
            - **HttpResponse:** The rendered HTML response.
    """
    
    template_name = 'proxmox2netbox/home.html'

    def get(self, request):
        endpoints = ProxmoxEndpoint.objects.select_related('ip_address').all()
        last_synced = endpoints.filter(last_synced__isnull=False).order_by('-last_synced').values_list('last_synced', flat=True).first()

        return render(
            request,
            self.template_name,
            {
                'proxmox_endpoint_list': endpoints if endpoints.exists() else None,
                'last_synced': last_synced,
            }
        )

class ContributingView(SuperuserRequiredMixin, View):
    """
    **ContributingView** handles the rendering of the contributing page for the Proxmox2NetBox project.
    
    **Attributes:**
    - **template_name (str):** The path to the HTML template for the contributing page.
    
    **Methods:**
    - **get(request):** Handles GET HTTP requests and renders the contributing page with the content
    of the 'CONTRIBUTING.md' file and a title.
    """
    
    template_name = 'proxmox2netbox/contributing.html'

    # service incoming GET HTTP requests
    def get(self, request):
        """Get request."""

        title = "Contributing to Proxmox2NetBox Project"
        content = None
        for candidate in (
            pathlib.Path(__file__).parent.parent / 'CONTRIBUTING.md',
            pathlib.Path(__file__).parent.parent.parent / 'CONTRIBUTING.md',
        ):
            if candidate.is_file():
                content = candidate.read_text(encoding='utf-8')
                break

        return render(
            request,
            self.template_name,
            {
                "html": content,
                "title": title,
            }
        )
