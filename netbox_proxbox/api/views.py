from rest_framework.routers import APIRootView
from netbox.api.viewsets import NetBoxModelViewSet
from extras.models import JournalEntry
from netbox_proxbox.models import SyncProcess
from netbox_proxbox.api.serializers import SyncProcessSerializer
from netbox_proxbox.api.filters import SyncProcessFilterSet

from .. import models
from .serializers import (
    JournalEntrySerializer,
    ProxmoxEndpointSerializer,
)

class Proxmox2NetBoxRootView(APIRootView):
    """
    Proxmox2NetBox API root view
    """
    def get_view_name(self):
        return "Proxmox2NetBox"

    def get(self, request, *args, **kwargs):
        # Get the default response from the parent class
        response = super().get(request, *args, **kwargs)
        
        # Get the base URL for the API
        base_url = request.build_absolute_uri('/').rstrip('/')
        
        # Add the endpoints link to the response data
        response.data['endpoints'] = f"{base_url}/api/plugins/proxmox2netbox/endpoints/"
        
        return response

class Proxmox2NetBoxEndpointsView(APIRootView):
    def get_view_name(self):
        return "Endpoints"

class SyncProcessViewSet(NetBoxModelViewSet):
    queryset = SyncProcess.objects.all()
    serializer_class = SyncProcessSerializer
    filterset_class = SyncProcessFilterSet

class ProxmoxEndpointViewSet(NetBoxModelViewSet):
    queryset = models.ProxmoxEndpoint.objects.all()
    serializer_class = ProxmoxEndpointSerializer

class JournalEntryViewSet(NetBoxModelViewSet):
    """
    ViewSet for managing journal entries associated with SyncProcess objects.
    
    This ViewSet provides CRUD operations for journal entries and allows filtering
    entries by their associated SyncProcess object.
    
    Attributes:
        queryset: Base queryset of all JournalEntry objects
        serializer_class: JournalEntrySerializer for data serialization
        
    Methods:
        get_queryset: Filters journal entries by SyncProcess object_id if provided
        
    API Endpoints:
        GET /api/plugins/proxmox2netbox/journal-entries/ - List all journal entries
        GET /api/plugins/proxmox2netbox/journal-entries/?object_id=<id> - Filter by SyncProcess
        POST /api/plugins/proxmox2netbox/journal-entries/ - Create new entry
        PUT /api/plugins/proxmox2netbox/journal-entries/<id>/ - Update entry
        DELETE /api/plugins/proxmox2netbox/journal-entries/<id>/ - Delete entry
        
    Example Usage:
        # Get all journal entries for a specific SyncProcess
        GET /api/plugins/proxmox2netbox/journal-entries/?object_id=1
        
        # Create a new journal entry
        POST /api/plugins/proxmox2netbox/journal-entries/
        {
            "assigned_object_type": "syncprocess",
            "assigned_object_id": 1,
            "kind": "info",
            "comments": "Sync process started"
        }
    """
    queryset = JournalEntry.objects.all()
    serializer_class = JournalEntrySerializer
    
    def get_queryset(self):
        """
        Filter journal entries by SyncProcess object_id if provided in query params.
        
        This method extends the base queryset to allow filtering journal entries
        by their associated SyncProcess object. When the 'object_id' query parameter
        is present, it filters the queryset to only include entries for that specific
        SyncProcess.
        
        Returns:
            QuerySet: Filtered queryset of JournalEntry objects
            
        Example:
            # Get all journal entries for SyncProcess with ID 1
            queryset = JournalEntry.objects.filter(
                assigned_object_type__model='syncprocess',
                assigned_object_id=1
            )
        """
        queryset = super().get_queryset()
        if 'object_id' in self.request.query_params:
            queryset = queryset.filter(
                assigned_object_type__model='syncprocess',
                assigned_object_id=self.request.query_params['object_id']
            )
        return queryset

    
