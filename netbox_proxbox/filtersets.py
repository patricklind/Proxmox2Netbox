from netbox.filtersets import NetBoxModelFilterSet
from .models import ProxmoxEndpoint, SyncProcess


class SyncProcessFilterSet(NetBoxModelFilterSet):
    """
    FilterSet for SyncProcess model.
    It is used in the SyncProcessListView.
    """
    class Meta:
        model = SyncProcess
        fields = ['id', 'name', 'sync_type', 'status', 'started_at', 'completed_at', 'runtime']

    def search(self, queryset, name, value):
        return queryset.filter(name__icontains=value)


class ProxmoxEndpointFilterSet(NetBoxModelFilterSet):
    class Meta:
        model = ProxmoxEndpoint
        fields = ['id', 'name', 'domain', 'ip_address', 'mode']
    
    def search(self, queryset, name, value):
        return queryset.filter(name__icontains=value)
