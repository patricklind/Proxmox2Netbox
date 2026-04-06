from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_GET

from django_htmx.middleware import HtmxDetails

from proxmox2netbox.models import ProxmoxEndpoint
from proxmox2netbox.services.proxmox_sync import check_endpoint_connection


class HtmxHttpRequest(HttpRequest):
    htmx: HtmxDetails


@login_required
@require_GET
def get_service_status(
    request: HtmxHttpRequest,
    service: str,
    pk: int,
) -> HttpResponse:
    template_name = "proxmox2netbox/status_badge.html"
    status = "unknown"

    if service == "proxmox":
        try:
            endpoint = ProxmoxEndpoint.objects.get(pk=pk)
            result = check_endpoint_connection(endpoint)
            status = "success" if result.get('ok') else "error"
        except ProxmoxEndpoint.DoesNotExist:
            status = "error"

    return render(request, template_name, {"status": status})
