import logging
import math
import re
from dataclasses import dataclass, field
from typing import Any

from django.contrib.contenttypes.models import ContentType
from django.utils import timezone

from dcim.models import Device, DeviceRole, DeviceType, Manufacturer, Site
from extras.models.tags import Tag, TaggedItem
from virtualization.models import Cluster, ClusterType, VirtualDisk, VMInterface, VirtualMachine

from proxmoxer import ProxmoxAPI

from proxmox2netbox.choices import ProxmoxModeChoices, SyncStatusChoices, SyncTypeChoices
from proxmox2netbox.models import ProxmoxEndpoint, SyncProcess

logger = logging.getLogger(__name__)

MANAGED_TAG_SLUG = "proxmox2netbox"
LEGACY_MANAGED_TAG_SLUGS = (
    "proxbox",
    "netbox-proxbox",
    "proxmox2netbox-plugin",
)


class ProxmoxSyncError(Exception):
    """Raised when Proxmox synchronization fails."""


@dataclass
class EndpointSession:
    endpoint: ProxmoxEndpoint
    client: Any
    host: str
    version: dict = field(default_factory=dict)


def _safe_add_tag(obj: Any, tag: Tag) -> None:
    if obj.pk is None:
        return
    content_type = ContentType.objects.get_for_model(obj, for_concrete_model=False)
    # Keep only the canonical managed tag on synchronized objects.
    legacy_slugs = [slug for slug in LEGACY_MANAGED_TAG_SLUGS if slug != tag.slug]
    if legacy_slugs:
        TaggedItem.objects.filter(
            content_type=content_type,
            object_id=obj.pk,
            tag__slug__in=legacy_slugs,
        ).delete()

    qs = TaggedItem.objects.filter(
        content_type=content_type,
        object_id=obj.pk,
        tag=tag,
    ).order_by("pk")
    first = qs.first()
    if first is not None:
        duplicate_qs = qs.exclude(pk=first.pk)
        if duplicate_qs.exists():
            duplicate_qs.delete()
        return
    TaggedItem.objects.create(content_type=content_type, object_id=obj.pk, tag=tag)


def _endpoint_hosts(endpoint: ProxmoxEndpoint) -> list[str]:
    hosts: list[str] = []
    if endpoint.domain:
        hosts.append(endpoint.domain.strip())
    if endpoint.ip_address:
        hosts.append(str(endpoint.ip_address.address).split("/")[0])
    # Keep order and remove empty/duplicates
    return list(dict.fromkeys([host for host in hosts if host]))


def _auth_options(endpoint: ProxmoxEndpoint) -> list[tuple[str, dict[str, str]]]:
    options: list[tuple[str, dict[str, str]]] = []
    token_name = (endpoint.token_name or "").strip()
    token_value = (endpoint.token_value or "").strip()
    password = (endpoint.password or "").strip()

    if token_name and token_value:
        options.append(("token", {"token_name": token_name, "token_value": token_value}))
    if password:
        options.append(("password", {"password": password}))
    if not options:
        raise ProxmoxSyncError(
            f"Endpoint '{endpoint}' has no usable credentials. Provide password or token name/value."
        )
    return options


def connect_endpoint(endpoint: ProxmoxEndpoint) -> EndpointSession:
    hosts = _endpoint_hosts(endpoint)
    if not hosts:
        raise ProxmoxSyncError(
            f"Endpoint '{endpoint}' has neither domain nor IP address configured."
        )

    auth_options = _auth_options(endpoint)
    connection_errors: list[str] = []

    for host in hosts:
        for auth_type, auth_kwargs in auth_options:
            try:
                client = ProxmoxAPI(
                    host,
                    user=endpoint.username,
                    port=endpoint.port,
                    verify_ssl=endpoint.verify_ssl,
                    **auth_kwargs,
                )
                version = client.version.get()
                return EndpointSession(endpoint=endpoint, client=client, host=host, version=version or {})
            except Exception as exc:  # noqa: BLE001 - any proxmox/auth/network error
                connection_errors.append(f"{host} via {auth_type}: {exc}")

    raise ProxmoxSyncError(
        f"Unable to connect to endpoint '{endpoint}'. Attempts: {' | '.join(connection_errors)}"
    )


def _cluster_status_data(client: Any) -> tuple[str, str | None, list[dict]]:
    status_rows = client.cluster.status.get()
    nodes = [row for row in status_rows if row.get("type") == "node"]
    cluster_row = next((row for row in status_rows if row.get("type") == "cluster"), None)

    if cluster_row:
        mode = ProxmoxModeChoices.PROXMOX_MODE_CLUSTER
        cluster_name = cluster_row.get("name")
    elif len(nodes) == 1:
        mode = ProxmoxModeChoices.PROXMOX_MODE_STANDALONE
        cluster_name = nodes[0].get("name")
    else:
        mode = ProxmoxModeChoices.PROXMOX_MODE_UNDEFINED
        cluster_name = None

    return mode, cluster_name, nodes


def _update_endpoint_metadata(session: EndpointSession) -> dict[str, Any]:
    endpoint = session.endpoint
    mode, cluster_name, nodes = _cluster_status_data(session.client)
    version = session.version or {}

    updated_fields: list[str] = []
    new_name = cluster_name or endpoint.name
    if endpoint.name != new_name:
        endpoint.name = new_name
        updated_fields.append("name")
    if endpoint.mode != mode:
        endpoint.mode = mode
        updated_fields.append("mode")
    if endpoint.version != version.get("version"):
        endpoint.version = version.get("version")
        updated_fields.append("version")
    if endpoint.repoid != version.get("repoid"):
        endpoint.repoid = version.get("repoid")
        updated_fields.append("repoid")
    if updated_fields:
        endpoint.save(update_fields=updated_fields)

    return {
        "mode": mode,
        "name": cluster_name or endpoint.name,
        "version": version.get("version"),
        "repoid": version.get("repoid"),
        "nodes": nodes,
    }


def _ensure_base_objects(mode: str) -> dict[str, Any]:
    tag, _ = Tag.objects.get_or_create(
        slug=MANAGED_TAG_SLUG,
        defaults={
            "name": "Proxmox2NetBox",
            "color": "ff5722",
            "description": "Objects managed by proxmox2netbox",
        },
    )
    manufacturer, _ = Manufacturer.objects.get_or_create(
        slug="proxmox",
        defaults={"name": "Proxmox"},
    )
    device_type, _ = DeviceType.objects.get_or_create(
        slug="proxmox-node",
        defaults={"manufacturer": manufacturer, "model": "Proxmox Node"},
    )
    site, _ = Site.objects.get_or_create(
        slug="proxmox2netbox",
        defaults={"name": "Proxmox2NetBox"},
    )
    node_role, _ = DeviceRole.objects.get_or_create(
        slug="proxmox-node",
        defaults={"name": "Proxmox Node", "vm_role": False},
    )
    qemu_role, _ = DeviceRole.objects.get_or_create(
        slug="proxmox-vm-qemu",
        defaults={"name": "Proxmox VM (QEMU)", "vm_role": True},
    )
    lxc_role, _ = DeviceRole.objects.get_or_create(
        slug="proxmox-vm-lxc",
        defaults={"name": "Proxmox Container (LXC)", "vm_role": True},
    )
    cluster_type, _ = ClusterType.objects.get_or_create(
        slug=f"proxmox-{mode}",
        defaults={"name": f"Proxmox {mode.capitalize()}"},
    )
    return {
        "tag": tag,
        "manufacturer": manufacturer,
        "device_type": device_type,
        "site": site,
        "node_role": node_role,
        "qemu_role": qemu_role,
        "lxc_role": lxc_role,
        "cluster_type": cluster_type,
    }


def _upsert_cluster(cluster_name: str, cluster_type: ClusterType, tag: Tag) -> Cluster:
    clusters = Cluster.objects.filter(name=cluster_name).order_by("pk")
    cluster = clusters.first()
    if cluster is None:
        cluster = Cluster.objects.create(name=cluster_name, type=cluster_type)
    elif cluster.type_id != cluster_type.id:
        cluster.type = cluster_type
        cluster.save(update_fields=["type"])
    _safe_add_tag(cluster, tag)
    return cluster


def _status_from_proxmox(value: str | None) -> str:
    return "active" if value in {"running", "active"} else "offline"


def _extract_vm_config_networks(config: dict[str, Any]) -> list[tuple[str, dict[str, str]]]:
    interfaces: list[tuple[str, dict[str, str]]] = []
    for key, raw_value in config.items():
        if not re.match(r"^net\d+$", key):
            continue
        if not isinstance(raw_value, str):
            continue
        values: dict[str, str] = {}
        for item in raw_value.split(","):
            if "=" not in item:
                continue
            k, v = item.split("=", 1)
            values[k.strip()] = v.strip()
        interfaces.append((key, values))
    return interfaces


def _size_token_to_mb(size_token: str | None) -> int | None:
    if not size_token:
        return None
    match = re.match(r"^\s*(\d+(?:\.\d+)?)\s*([kmgtp]?)(?:b)?\s*$", size_token.strip(), re.IGNORECASE)
    if not match:
        return None

    value = float(match.group(1))
    unit = (match.group(2) or "").upper()
    unit_multipliers = {
        "": 1,  # Proxmox size values are usually MB when unit is omitted
        "K": 1 / 1024,
        "M": 1,
        "G": 1024,
        "T": 1024 * 1024,
        "P": 1024 * 1024 * 1024,
    }
    multiplier = unit_multipliers.get(unit)
    if multiplier is None:
        return None

    size_mb = int(math.ceil(value * multiplier))
    return max(size_mb, 1)


def _extract_vm_config_disks(config: dict[str, Any]) -> list[dict[str, Any]]:
    disk_items: list[dict[str, Any]] = []
    for key, raw_value in config.items():
        is_qemu_disk = re.match(r"^(scsi|sata|virtio|ide|efidisk)\d+$", key)
        is_lxc_disk = key == "rootfs" or re.match(r"^mp\d+$", key)
        if not (is_qemu_disk or is_lxc_disk):
            continue
        if not isinstance(raw_value, str):
            continue

        segments = [segment.strip() for segment in raw_value.split(",") if segment.strip()]
        if not segments:
            continue

        source = segments[0]
        attrs: dict[str, str] = {}
        for segment in segments[1:]:
            if "=" not in segment:
                continue
            attr_key, attr_value = segment.split("=", 1)
            attrs[attr_key.strip()] = attr_value.strip()

        if attrs.get("media") == "cdrom":
            continue

        size_mb = _size_token_to_mb(attrs.get("size"))
        if size_mb is None:
            continue

        description = source
        mountpoint = attrs.get("mp")
        if mountpoint:
            description = f"{source} (mount: {mountpoint})"
        description = description[:200]

        disk_items.append(
            {
                "name": key,
                "size": size_mb,
                "description": description,
            }
        )
    return disk_items


def _fetch_vm_config(client: Any, node_name: str, vm_type: str, vmid: int) -> dict[str, Any] | None:
    try:
        if vm_type == "qemu":
            return client.nodes(node_name).qemu(vmid).config.get()
        return client.nodes(node_name).lxc(vmid).config.get()
    except Exception as exc:  # noqa: BLE001
        logger.warning("Unable to fetch VM config for %s/%s/%s: %s", node_name, vm_type, vmid, exc)
        return None


def _upsert_vm_interfaces(
    vm: VirtualMachine,
    vm_type: str,
    vmid: int,
    node_name: str,
    client: Any,
    tag: Tag,
    vm_config: dict[str, Any] | None = None,
) -> tuple[int, int]:
    created_count = 0
    updated_count = 0

    if vm_config is None:
        vm_config = _fetch_vm_config(client=client, node_name=node_name, vm_type=vm_type, vmid=vmid)
    if vm_config is None:
        return created_count, updated_count

    for default_iface_name, attrs in _extract_vm_config_networks(vm_config):
        iface_name = attrs.get("name", default_iface_name)

        iface, created = VMInterface.objects.get_or_create(
            virtual_machine=vm,
            name=iface_name,
            defaults={
                "enabled": True,
                "description": "Imported from Proxmox",
            },
        )
        if created:
            created_count += 1
        else:
            changed = False
            if not iface.enabled:
                iface.enabled = True
                changed = True
            if changed:
                iface.save()
                updated_count += 1
        _safe_add_tag(iface, tag)

    return created_count, updated_count


def _sync_vm_disks(vm: VirtualMachine, vm_config: dict[str, Any], tag: Tag) -> tuple[int, int, int]:
    created_count = 0
    updated_count = 0
    deleted_count = 0

    desired_disks = _extract_vm_config_disks(vm_config)
    desired_by_name = {disk["name"]: disk for disk in desired_disks}

    for disk_name, disk_data in desired_by_name.items():
        disk, created = VirtualDisk.objects.get_or_create(
            virtual_machine=vm,
            name=disk_name,
            defaults={
                "size": disk_data["size"],
                "description": disk_data["description"],
            },
        )
        if created:
            created_count += 1
        else:
            changed = False
            if disk.size != disk_data["size"]:
                disk.size = disk_data["size"]
                changed = True
            if disk.description != disk_data["description"]:
                disk.description = disk_data["description"]
                changed = True
            if changed:
                disk.save(update_fields=["size", "description"])
                updated_count += 1

        _safe_add_tag(disk, tag)

    stale_qs = (
        VirtualDisk.objects.filter(virtual_machine=vm, tags=tag)
        .exclude(name__in=desired_by_name.keys())
        .order_by("pk")
    )
    deleted_count = stale_qs.count()
    if deleted_count:
        stale_qs.delete()

    return created_count, updated_count, deleted_count


def _upsert_devices_for_session(session: EndpointSession) -> dict[str, int]:
    metadata = _update_endpoint_metadata(session)
    mode = metadata["mode"]
    cluster_name = metadata["name"] or session.host
    nodes = metadata["nodes"]
    base = _ensure_base_objects(mode)

    cluster = _upsert_cluster(cluster_name, base["cluster_type"], base["tag"])

    created = 0
    updated = 0
    for node in nodes:
        node_name = node.get("name")
        if not node_name:
            continue
        desired_status = "active" if node.get("online") == 1 else "offline"
        device, was_created = Device.objects.get_or_create(
            name=node_name,
            defaults={
                "device_type": base["device_type"],
                "role": base["node_role"],
                "site": base["site"],
                "status": desired_status,
                "cluster": cluster,
                "description": "Imported from Proxmox by proxmox2netbox",
            },
        )
        if was_created:
            created += 1
        else:
            changed = False
            if device.device_type_id != base["device_type"].id:
                device.device_type = base["device_type"]
                changed = True
            if device.role_id != base["node_role"].id:
                device.role = base["node_role"]
                changed = True
            if device.site_id != base["site"].id:
                device.site = base["site"]
                changed = True
            if device.cluster_id != cluster.id:
                device.cluster = cluster
                changed = True
            if device.status != desired_status:
                device.status = desired_status
                changed = True
            if changed:
                device.save()
                updated += 1
        _safe_add_tag(device, base["tag"])

    return {"created_devices": created, "updated_devices": updated}


def _upsert_virtual_machines_for_session(session: EndpointSession) -> dict[str, int]:
    metadata = _update_endpoint_metadata(session)
    mode = metadata["mode"]
    cluster_name = metadata["name"] or session.host
    base = _ensure_base_objects(mode)

    cluster = _upsert_cluster(cluster_name, base["cluster_type"], base["tag"])

    resources = session.client.cluster.resources.get()
    vm_resources = [resource for resource in resources if resource.get("type") in {"qemu", "lxc"}]

    created_vm = 0
    updated_vm = 0
    created_iface = 0
    updated_iface = 0
    created_disk = 0
    updated_disk = 0
    deleted_disk = 0

    for resource in vm_resources:
        vm_type = resource.get("type", "qemu")
        vmid = int(resource.get("vmid", 0))
        vm_name = resource.get("name") or f"{vm_type}-{vmid}"
        role = base["qemu_role"] if vm_type == "qemu" else base["lxc_role"]
        node_name = resource.get("node")
        backing_device = Device.objects.filter(name=node_name).first() if node_name else None

        desired = {
            "status": _status_from_proxmox(resource.get("status")),
            "cluster": cluster,
            "device": backing_device,
            "role": role,
            "vcpus": int(resource.get("maxcpu", 0)) or None,
            "memory": int((resource.get("maxmem", 0) or 0) / 1_000_000) or None,
            "disk": int((resource.get("maxdisk", 0) or 0) / 1_000_000) or None,
            "comments": "Imported from Proxmox by proxmox2netbox",
        }

        vm, was_created = VirtualMachine.objects.get_or_create(name=vm_name, defaults=desired)
        if was_created:
            created_vm += 1
        else:
            changed = False
            for field_name, field_value in desired.items():
                if getattr(vm, field_name) != field_value:
                    setattr(vm, field_name, field_value)
                    changed = True
            if changed:
                vm.save()
                updated_vm += 1

        _safe_add_tag(vm, base["tag"])

        if node_name and vmid:
            vm_config = _fetch_vm_config(
                client=session.client,
                node_name=node_name,
                vm_type=vm_type,
                vmid=vmid,
            )
        else:
            vm_config = None

        if vm_config:
            iface_created, iface_updated = _upsert_vm_interfaces(
                vm=vm,
                vm_type=vm_type,
                vmid=vmid,
                node_name=node_name,
                client=session.client,
                tag=base["tag"],
                vm_config=vm_config,
            )
            created_iface += iface_created
            updated_iface += iface_updated

            disk_created, disk_updated, disk_deleted = _sync_vm_disks(
                vm=vm,
                vm_config=vm_config,
                tag=base["tag"],
            )
            created_disk += disk_created
            updated_disk += disk_updated
            deleted_disk += disk_deleted

    return {
        "created_virtual_machines": created_vm,
        "updated_virtual_machines": updated_vm,
        "created_vm_interfaces": created_iface,
        "updated_vm_interfaces": updated_iface,
        "created_virtual_disks": created_disk,
        "updated_virtual_disks": updated_disk,
        "deleted_virtual_disks": deleted_disk,
    }


def _run_sync(sync_type: str, per_endpoint_func) -> dict[str, Any]:
    endpoints = list(ProxmoxEndpoint.objects.all())
    if not endpoints:
        raise ProxmoxSyncError("No Proxmox endpoints configured.")

    started_at = timezone.now()
    process = SyncProcess.objects.create(
        name=f"sync-{sync_type}-{started_at.isoformat()}",
        sync_type=sync_type,
        status=SyncStatusChoices.SYNCING,
        started_at=started_at,
    )

    result: dict[str, Any] = {
        "sync_type": sync_type,
        "started_at": started_at,
        "completed_at": None,
        "runtime_seconds": None,
        "endpoints": 0,
        "errors": [],
    }

    try:
        for endpoint in endpoints:
            try:
                session = connect_endpoint(endpoint)
                endpoint_result = per_endpoint_func(session)
                result["endpoints"] += 1
                for key, value in endpoint_result.items():
                    result[key] = result.get(key, 0) + value
            except Exception as exc:  # noqa: BLE001
                logger.exception("Sync failed for endpoint %s: %s", endpoint, exc)
                result["errors"].append(f"{endpoint}: {exc}")

        completed_at = timezone.now()
        runtime = (completed_at - started_at).total_seconds()
        result["completed_at"] = completed_at
        result["runtime_seconds"] = runtime
        process.completed_at = completed_at
        process.runtime = runtime
        process.status = (
            SyncStatusChoices.COMPLETED if not result["errors"] else SyncStatusChoices.FAILED
        )
        process.save(update_fields=["completed_at", "runtime", "status"])
        return result
    except Exception:
        process.status = SyncStatusChoices.FAILED
        process.completed_at = timezone.now()
        process.runtime = (process.completed_at - started_at).total_seconds()
        process.save(update_fields=["completed_at", "runtime", "status"])
        raise


def check_endpoint_connection(endpoint: ProxmoxEndpoint) -> tuple[bool, str | None]:
    try:
        connect_endpoint(endpoint)
        return True, None
    except Exception as exc:  # noqa: BLE001
        return False, str(exc)


def get_endpoint_cluster_summary(endpoint: ProxmoxEndpoint) -> dict[str, Any]:
    session = connect_endpoint(endpoint)
    return _update_endpoint_metadata(session)


def sync_devices() -> dict[str, Any]:
    return _run_sync(SyncTypeChoices.DEVICES, _upsert_devices_for_session)


def sync_virtual_machines() -> dict[str, Any]:
    return _run_sync(SyncTypeChoices.VIRTUAL_MACHINES, _upsert_virtual_machines_for_session)


def sync_full_update() -> dict[str, Any]:
    devices_result = sync_devices()
    vms_result = sync_virtual_machines()

    return {
        "sync_type": SyncTypeChoices.ALL,
        "started_at": devices_result.get("started_at"),
        "completed_at": vms_result.get("completed_at"),
        "runtime_seconds": (devices_result.get("runtime_seconds") or 0)
        + (vms_result.get("runtime_seconds") or 0),
        "endpoints": max(devices_result.get("endpoints", 0), vms_result.get("endpoints", 0)),
        "created_devices": devices_result.get("created_devices", 0),
        "updated_devices": devices_result.get("updated_devices", 0),
        "created_virtual_machines": vms_result.get("created_virtual_machines", 0),
        "updated_virtual_machines": vms_result.get("updated_virtual_machines", 0),
        "created_vm_interfaces": vms_result.get("created_vm_interfaces", 0),
        "updated_vm_interfaces": vms_result.get("updated_vm_interfaces", 0),
        "created_virtual_disks": vms_result.get("created_virtual_disks", 0),
        "updated_virtual_disks": vms_result.get("updated_virtual_disks", 0),
        "deleted_virtual_disks": vms_result.get("deleted_virtual_disks", 0),
        "errors": [*devices_result.get("errors", []), *vms_result.get("errors", [])],
    }
