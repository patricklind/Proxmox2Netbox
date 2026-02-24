import logging

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_GET

from django_htmx.middleware import HtmxDetails

from netbox_proxbox.models import ProxmoxEndpoint
from netbox_proxbox.proxmox_sync import get_endpoint_cluster_summary

logger = logging.getLogger(__name__)


class HtmxHttpRequest(HttpRequest):
    htmx: HtmxDetails


@require_GET
def get_proxmox_card(
    request: HtmxHttpRequest,
    pk: int,
) -> HttpResponse:
    template_name = "netbox_proxbox/home/proxmox_card.html"

    proxmox_object = None
    try:
        proxmox_object = ProxmoxEndpoint.objects.get(pk=pk)
    except ProxmoxEndpoint.DoesNotExist:
        proxmox_object = None

    cluster_data: dict = {}
    if proxmox_object is not None:
        try:
            cluster_data = get_endpoint_cluster_summary(proxmox_object)
        except Exception as exc:  # noqa: BLE001
            logger.warning("Unable to load Proxmox card data for endpoint %s: %s", proxmox_object, exc)
            cluster_data = {"error": str(exc)}

    return render(
        request,
        template_name,
        {
            "cluster_data": cluster_data,
            "object": proxmox_object,
        },
    )
