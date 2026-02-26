from django.shortcuts import render
from django.views import View

from proxmox2netbox import github

from .cards import get_proxmox_card
from .keepalive_status import get_service_status
from .endpoints import (
    ProxmoxEndpointDeleteView,
    ProxmoxEndpointEditView,
    ProxmoxEndpointListView,
    ProxmoxEndpointView,
)
from .sync import sync_devices, sync_full_update, sync_virtual_machines
from .sync_process import (
    SyncProcessAddView,
    SyncProcessDeleteView,
    SyncProcessEditView,
    SyncProcessListView,
    SyncProcessView,
)

from proxmox2netbox.models import ProxmoxEndpoint

__all__ = (
    "ContributingView",
    "HomeView",
    "ProxmoxEndpointDeleteView",
    "ProxmoxEndpointEditView",
    "ProxmoxEndpointListView",
    "ProxmoxEndpointView",
    "SyncProcessAddView",
    "SyncProcessDeleteView",
    "SyncProcessEditView",
    "SyncProcessListView",
    "SyncProcessView",
    "get_proxmox_card",
    "get_service_status",
    "sync_devices",
    "sync_full_update",
    "sync_virtual_machines",
)

class HomeView(View):
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

    # service incoming GET HTTP requests
    def get(self, request):
        """Get request."""

        proxmox_endpoint_obj = ProxmoxEndpoint.objects.all()
        if proxmox_endpoint_obj.count() <= 0:
            proxmox_endpoint_obj = None

        return render(
            request,
            self.template_name,
            {
                'proxmox_endpoint_list': proxmox_endpoint_obj,
            }
        )

class ContributingView(View):
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
        
        return render(
            request,
            self.template_name,
            {
                "html": github.get(filename = "CONTRIBUTING.md"),
                "title": title,
            }
        )
