from django.contrib import messages
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_GET

from django_htmx.middleware import HtmxDetails

from netbox_proxbox.services.proxmox_sync import (
    ProxmoxSyncError,
    sync_devices as sync_devices_service,
    sync_full_update as sync_full_update_service,
    sync_virtual_machines as sync_virtual_machines_service,
)


class HtmxHttpRequest(HttpRequest):
    htmx: HtmxDetails


def _run_sync(request: HtmxHttpRequest, template_name: str, sync_callable) -> HttpResponse:
    result = {}
    try:
        result = sync_callable()
        if result.get("errors"):
            messages.warning(
                request,
                f"Sync completed with {len(result['errors'])} error(s). Check details below.",
            )
        else:
            messages.success(request, "Sync completed successfully.")
    except ProxmoxSyncError as exc:
        messages.error(request, str(exc))
        result = {"errors": [str(exc)]}
    except Exception as exc:  # noqa: BLE001
        messages.error(request, f"Unexpected sync error: {exc}")
        result = {"errors": [str(exc)]}

    return render(request, template_name, {"result": result})


@require_GET
def sync_devices(request: HtmxHttpRequest) -> HttpResponse:
    return _run_sync(
        request=request,
        template_name="netbox_proxbox/sync_devices.html",
        sync_callable=sync_devices_service,
    )


@require_GET
def sync_virtual_machines(request: HtmxHttpRequest) -> HttpResponse:
    return _run_sync(
        request=request,
        template_name="netbox_proxbox/sync_virtual_machines.html",
        sync_callable=sync_virtual_machines_service,
    )


@require_GET
def sync_full_update(request: HtmxHttpRequest) -> HttpResponse:
    return _run_sync(
        request=request,
        template_name="netbox_proxbox/sync_full_update.html",
        sync_callable=sync_full_update_service,
    )
