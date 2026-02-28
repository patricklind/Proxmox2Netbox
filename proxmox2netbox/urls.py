from django.urls import include, path
from utilities.urls import get_model_urls

from proxmox2netbox import views

app_name = 'proxmox2netbox'

urlpatterns = [
    # Home View
    path('', views.HomeView.as_view(), name='home'),
    path('contributing/', views.ContributingView.as_view(), name='contributing'),
    
    # ProxmoxEndpoint Model URLs
    path('endpoints/proxmox/<int:pk>/', include(get_model_urls('proxmox2netbox', 'proxmoxendpoint'))),
    path('endpoints/proxmox/', include(get_model_urls('proxmox2netbox', 'proxmoxendpoint', detail=False))),
    
    # SyncProcess Model URLs
    path('sync-processes/<int:pk>/', include(get_model_urls('proxmox2netbox', 'syncprocess'))),
    path('sync-processes/', include(get_model_urls('proxmox2netbox', 'syncprocess', detail=False))),

    # ProxmoxNodeTypeMapping Model URLs
    path('node-type-mappings/<int:pk>/', include(get_model_urls('proxmox2netbox', 'proxmoxnodetypemapping'))),
    path('node-type-mappings/', include(get_model_urls('proxmox2netbox', 'proxmoxnodetypemapping', detail=False))),
    
    # Manual Sync (HTTP Request)
    path('sync/devices', views.sync_devices, name='sync_devices'),
    path('sync/virtual-machines', views.sync_virtual_machines, name='sync_virtual_machines'),
    path('sync/full-update', views.sync_full_update, name='sync_full_update'),
    
    path('keepalive-status/<str:service>/<int:pk>', views.get_service_status, name='keepalive_status'),
    path('proxmox-card/<int:pk>', views.get_proxmox_card, name='proxmox_card'),
]
