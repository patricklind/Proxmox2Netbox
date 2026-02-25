from django.urls import include, path
from utilities.urls import get_model_urls

from netbox_proxbox import views

app_name = 'netbox_proxbox'

urlpatterns = [
    # Home View
    path('', views.HomeView.as_view(), name='home'),
    path('contributing/', views.ContributingView.as_view(), name='contributing'),
    
    # ProxmoxEndpoint Model URLs
    path('endpoints/proxmox/<int:pk>/', include(get_model_urls('netbox_proxbox', 'proxmoxendpoint'))),
    path('endpoints/proxmox/', include(get_model_urls('netbox_proxbox', 'proxmoxendpoint', detail=False))),
    
    # SyncProcess Model URLs
    path('sync-processes/<int:pk>/', include(get_model_urls('netbox_proxbox', 'syncprocess'))),
    path('sync-processes/', include(get_model_urls('netbox_proxbox', 'syncprocess', detail=False))),
    
    # Manual Sync (HTTP Request)
    path('sync/devices', views.sync_devices, name='sync_devices'),
    path('sync/virtual-machines', views.sync_virtual_machines, name='sync_virtual_machines'),
    path('sync/full-update', views.sync_full_update, name='sync_full_update'),
    
    path('keepalive-status/<str:service>/<int:pk>', views.get_service_status, name='keepalive_status'),
    path('proxmox-card/<int:pk>', views.get_proxmox_card, name='proxmox_card'),
]
