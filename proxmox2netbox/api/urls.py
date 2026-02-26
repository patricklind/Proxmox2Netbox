from netbox.api.routers import NetBoxRouter
from django.urls import path, include
from . import views

app_name = 'proxmox2netbox'

# Create endpoints router
endpoints_router = NetBoxRouter()
endpoints_router.APIRootView = views.Proxmox2NetBoxEndpointsView
endpoints_router.register('proxmox', views.ProxmoxEndpointViewSet, basename='proxmox-endpoint')

# Create main router
router = NetBoxRouter()
router.APIRootView = views.Proxmox2NetBoxRootView

router.register('sync-processes', views.SyncProcessViewSet)
router.register('journal-entries', views.JournalEntryViewSet)

urlpatterns = [
    path('endpoints/', include((endpoints_router.urls, 'endpoints'), namespace='endpoints')),
    path('', include(router.urls)),
]
