from netbox.views import generic
from utilities.views import register_model_view

from proxmox2netbox.models import ProxmoxNodeTypeMapping
from proxmox2netbox.tables import ProxmoxNodeTypeMappingTable
from proxmox2netbox.filtersets import ProxmoxNodeTypeMappingFilterSet
from proxmox2netbox.forms import ProxmoxNodeTypeMappingForm, ProxmoxNodeTypeMappingFilterForm


__all__ = (
    'ProxmoxNodeTypeMappingView',
    'ProxmoxNodeTypeMappingListView',
    'ProxmoxNodeTypeMappingEditView',
    'ProxmoxNodeTypeMappingDeleteView',
)


@register_model_view(ProxmoxNodeTypeMapping)
class ProxmoxNodeTypeMappingView(generic.ObjectView):
    queryset = ProxmoxNodeTypeMapping.objects.select_related('endpoint', 'device_type__manufacturer')


@register_model_view(ProxmoxNodeTypeMapping, 'list', path='', detail=False)
class ProxmoxNodeTypeMappingListView(generic.ObjectListView):
    queryset = ProxmoxNodeTypeMapping.objects.select_related('endpoint', 'device_type__manufacturer')
    table = ProxmoxNodeTypeMappingTable
    filterset = ProxmoxNodeTypeMappingFilterSet
    filterset_form = ProxmoxNodeTypeMappingFilterForm


@register_model_view(ProxmoxNodeTypeMapping, 'add', detail=False)
@register_model_view(ProxmoxNodeTypeMapping, 'edit')
class ProxmoxNodeTypeMappingEditView(generic.ObjectEditView):
    queryset = ProxmoxNodeTypeMapping.objects.all()
    form = ProxmoxNodeTypeMappingForm


@register_model_view(ProxmoxNodeTypeMapping, 'delete')
class ProxmoxNodeTypeMappingDeleteView(generic.ObjectDeleteView):
    queryset = ProxmoxNodeTypeMapping.objects.all()
