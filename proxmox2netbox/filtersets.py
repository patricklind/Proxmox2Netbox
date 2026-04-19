from netbox.filtersets import NetBoxModelFilterSet
from .models import ProxmoxEndpoint, ProxmoxNodeTypeMapping, SyncProcess


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
        fields = [
            'id', 'name', 'domain', 'ip_address', 'mode',
            'sync_enabled', 'sync_nodes', 'sync_qemu_vms', 'sync_lxc_containers',
        ]

    def search(self, queryset, name, value):
        return queryset.filter(name__icontains=value)


class ProxmoxNodeTypeMappingFilterSet(NetBoxModelFilterSet):
    class Meta:
        model = ProxmoxNodeTypeMapping
        fields = ['id', 'endpoint', 'node_name', 'device_type']

    def search(self, queryset, name, value):
        return queryset.filter(node_name__icontains=value)
