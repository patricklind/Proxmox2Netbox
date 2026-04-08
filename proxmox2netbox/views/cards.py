from django.contrib.auth.decorators import user_passes_test
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_GET

from django_htmx.middleware import HtmxDetails

from proxmox2netbox.models import ProxmoxEndpoint


class HtmxHttpRequest(HttpRequest):
    htmx: HtmxDetails


@user_passes_test(lambda u: u.is_superuser)
@require_GET
def get_proxmox_card(
    request: HtmxHttpRequest,
    pk: int,
) -> HttpResponse:
    try:
        obj = ProxmoxEndpoint.objects.select_related('ip_address').get(pk=pk)
    except ProxmoxEndpoint.DoesNotExist:
        return HttpResponse('<div class="card"><div class="card-body text-danger">Endpoint not found</div></div>')

    return render(
        request,
        "proxmox2netbox/home/proxmox_card.html",
        {"object": obj},
    )
