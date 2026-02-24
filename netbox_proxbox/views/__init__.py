from django.shortcuts import render
from django.views import View

try:
    from netbox import configuration
except Exception as error:
    print(error)
from netbox_proxbox import github

from .cards import get_proxmox_card
from .endpoints import (
    FastAPIEndpointDeleteView,
    FastAPIEndpointEditView,
    FastAPIEndpointListView,
    FastAPIEndpointView,
    NetBoxEndpointDeleteView,
    NetBoxEndpointEditView,
    NetBoxEndpointListView,
    NetBoxEndpointView,
    ProxmoxEndpointDeleteView,
    ProxmoxEndpointEditView,
    ProxmoxEndpointListView,
    ProxmoxEndpointView,
)
from .external_pages import DiscordView, DiscussionsView, TelegramView
from .keepalive_status import get_service_status
from .proxbox_backend import (
    FixProxboxBackendView,
    RestartProxboxBackendView,
    StatusProxboxBackendView,
    StopProxboxBackendView,
)
from .sync import sync_devices, sync_full_update, sync_virtual_machines, sync_vm_backups
from .sync_process import (
    SyncProcessAddView,
    SyncProcessDeleteView,
    SyncProcessEditView,
    SyncProcessListView,
    SyncProcessView,
)
from .vm_backup import (
    VMBackupAddView,
    VMBackupBulkDeleteView,
    VMBackupDeleteView,
    VMBackupEditView,
    VMBackupListView,
    VMBackupTabView,
    VMBackupView,
)

from netbox_proxbox.models import ProxmoxEndpoint

__all__ = (
    "CommunityView",
    "ContributingView",
    "DiscordView",
    "DiscussionsView",
    "FastAPIEndpointDeleteView",
    "FastAPIEndpointEditView",
    "FastAPIEndpointListView",
    "FastAPIEndpointView",
    "FixProxboxBackendView",
    "HomeView",
    "NetBoxEndpointDeleteView",
    "NetBoxEndpointEditView",
    "NetBoxEndpointListView",
    "NetBoxEndpointView",
    "NodesView",
    "ProxmoxEndpointDeleteView",
    "ProxmoxEndpointEditView",
    "ProxmoxEndpointListView",
    "ProxmoxEndpointView",
    "RestartProxboxBackendView",
    "StatusProxboxBackendView",
    "StopProxboxBackendView",
    "SyncProcessAddView",
    "SyncProcessDeleteView",
    "SyncProcessEditView",
    "SyncProcessListView",
    "SyncProcessView",
    "TelegramView",
    "VMBackupAddView",
    "VMBackupBulkDeleteView",
    "VMBackupDeleteView",
    "VMBackupEditView",
    "VMBackupListView",
    "VMBackupTabView",
    "VMBackupView",
    "VirtualMachinesView",
    "get_proxmox_card",
    "get_service_status",
    "sync_devices",
    "sync_full_update",
    "sync_virtual_machines",
    "sync_vm_backups",
)

class HomeView(View):
    """
    ## HomeView class-based view to handle incoming GET HTTP requests.
    
    ### Attributes:
    - **template_name (str):** The path to the HTML template used for rendering the view.
    
    ### Methods:
    - **get(request):**
            Handles GET requests to the view.
            Retrieves plugin configuration and default settings.
            Constructs the FastAPI endpoint URL.
            Renders the template with the configuration and default settings.
            
            **Args:**
            - **request (HttpRequest):** The HTTP request object.
            
            **Returns:**
            - **HttpResponse:** The rendered HTML response.
    """
    
    template_name = 'netbox_proxbox/home.html'

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

class NodesView(View):
    template = 'netbox_proxbox/devices.html'

    def get(self, request):
        plugin_configuration: dict = getattr(configuration, "PLUGINS_CONFIG", {})

        return render(
            request, 
            self.template,
            {
                "configuration": plugin_configuration
            }
        )


class VirtualMachinesView(View):
    template = 'netbox_proxbox/virtual_machines.html'

    def get(self, request):
        plugin_configuration: dict = getattr(configuration, "PLUGINS_CONFIG", {})

        return render(
            request, 
            self.template,
            {
                "configuration": plugin_configuration
            }
        )

class ContributingView(View):
    """
    **ContributingView** handles the rendering of the contributing page for the Proxbox project.
    
    **Attributes:**
    - **template_name (str):** The path to the HTML template for the contributing page.
    
    **Methods:**
    - **get(request):** Handles GET HTTP requests and renders the contributing page with the content
    of the 'CONTRIBUTING.md' file and a title.
    """
    
    template_name = 'netbox_proxbox/contributing.html'

    # service incoming GET HTTP requests
    def get(self, request):
        """Get request."""

        title = "Contributing to Proxbox Project"
        
        return render(
            request,
            self.template_name,
            {
                "html": github.get(filename = "CONTRIBUTING.md"),
                "title": title,
            }
        )


class CommunityView(View):
    """
    CommunityView handles the rendering of the community page.
    
    **Attributes:**
    - **template_name (str):** The path to the HTML template for the community page.
    
    **Methods:**
    - **get(request):** Handles GET HTTP requests and renders the community page with a title.
    """
    
    
    template_name = 'netbox_proxbox/community.html'

    # service incoming GET HTTP requests
    def get(self, request):
        """Get request."""

        title = "Join our Community!"
        
        return render(
            request,
            self.template_name,
            {
                "title": title,
            }
        )
