import ipaddress as _ipaddress
import logging
from dataclasses import dataclass, field
from typing import Any

from django.contrib.contenttypes.models import ContentType

from dcim.models import Device, DeviceRole, DeviceType, MACAddress, Manufacturer, Site
from ipam.models import IPAddress
from extras.models.tags import Tag, TaggedItem
from virtualization.models import Cluster, ClusterType, VirtualDisk, VMInterface, VirtualMachine

from proxmoxer import ProxmoxAPI

from proxmox2netbox.choices import ProxmoxModeChoices, SyncTypeChoices
from proxmox2netbox.models import ProxmoxEndpoint, ProxmoxNodeTypeMapping
from proxmox2netbox.services._parse import (
    extract_interface_ips as _extract_interface_ips,
    extract_mac as _extract_mac,
    extract_vm_config_disks as _extract_vm_config_disks,
    extract_vm_config_networks as _extract_vm_config_networks,
    iface_description as _iface_description,
    status_from_proxmox as _status_from_proxmox,
)

logger = logging.getLogger(__name__)

MANAGED_TAG_SLUG = 'proxmox2netbox'
LEGACY_MANAGED_TAG_SLUGS = (
    'proxbox',
    'proxmox2netbox',
    'proxmox2netbox-plugin',
)


class ProxmoxSyncError(Exception):
    pass


@dataclass
class EndpointSession:
    endpoint: ProxmoxEndpoint
    client: Any
    host: str
    version: dict = field(default_factory=dict)

def _safe_add_tag(obj, tag):
    if obj.pk is None:
        return
    content_type = ContentType.objects.get_for_model(obj, for_concrete_model=False)
    legacy_slugs = [slug for slug in LEGACY_MANAGED_TAG_SLUGS if not slug == tag.slug]
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
    ).order_by('pk')
    first = qs.first()
    if first is not None:
        qs.exclude(pk=first.pk).delete()
        return
    TaggedItem.objects.create(content_type=content_type, object_id=obj.pk, tag=tag)


def _endpoint_hosts(endpoint):
    hosts = []
    if endpoint.domain:
        hosts.append(endpoint.domain.strip())
    if endpoint.ip_address:
        hosts.append(str(endpoint.ip_address.address).split('/')[0])
    return list(dict.fromkeys([h for h in hosts if h]))


def _auth_options(endpoint):
    options = []
    token_name = (endpoint.token_name or '').strip()
    token_value = (endpoint.token_value or '').strip()
    password = (endpoint.password or '').strip()
    if token_name and token_value:
        options.append(('token', {'token_name': token_name, 'token_value': token_value}))
    if password:
        options.append(('password', {'password': password}))
    if not options:
        raise ProxmoxSyncError(
            f'Endpoint {endpoint} has no usable credentials. Provide password or token name/value.'
        )
    return options

def connect_endpoint(endpoint):
    hosts = _endpoint_hosts(endpoint)
    if not hosts:
        raise ProxmoxSyncError(
            f'Endpoint {endpoint} has neither domain nor IP address configured.'
        )
    auth_options = _auth_options(endpoint)
    connection_errors = []
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
            except Exception as exc:
                connection_errors.append(f'{host} via {auth_type}: {exc}')
    raise ProxmoxSyncError(
        f'Unable to connect to endpoint {endpoint}. Attempts: {" | ".join(connection_errors)}'
    )


def _cluster_status_data(client):
    status_rows = client.cluster.status.get() or []
    nodes = [row for row in status_rows if row.get('type') == 'node']
    cluster_row = next((row for row in status_rows if row.get('type') == 'cluster'), None)
    if cluster_row:
        mode = ProxmoxModeChoices.PROXMOX_MODE_CLUSTER
        cluster_name = cluster_row.get('name')
    elif len(nodes) == 1:
        mode = ProxmoxModeChoices.PROXMOX_MODE_STANDALONE
        cluster_name = nodes[0].get('name')
    else:
        mode = ProxmoxModeChoices.PROXMOX_MODE_UNDEFINED
        cluster_name = None
    return mode, cluster_name, nodes

def _update_endpoint_metadata(session):
    endpoint = session.endpoint
    mode, cluster_name, nodes = _cluster_status_data(session.client)
    version = session.version or {}
    update_fields = []
    new_name = cluster_name or endpoint.name
    if not endpoint.name == new_name:
        endpoint.name = new_name
        update_fields.append('name')
    if not endpoint.mode == mode:
        endpoint.mode = mode
        update_fields.append('mode')
    if not endpoint.version == version.get('version'):
        endpoint.version = version.get('version')
        update_fields.append('version')
    if not endpoint.repoid == version.get('repoid'):
        endpoint.repoid = version.get('repoid')
        update_fields.append('repoid')
    if update_fields:
        endpoint.save(update_fields=update_fields)
    return {
        'mode': mode,
        'name': cluster_name or endpoint.name,
        'version': version.get('version'),
        'repoid': version.get('repoid'),
        'nodes': nodes,
    }

def _ensure_base_objects(mode, site=None, device_type=None):
    tag, _ = Tag.objects.get_or_create(
        slug=MANAGED_TAG_SLUG,
        defaults={
            'name': 'Proxmox2NetBox',
            'color': 'ff5722',
            'description': 'Objects managed by proxmox2netbox',
        },
    )
    manufacturer = None
    if device_type is None:
        manufacturer, _ = Manufacturer.objects.get_or_create(
            slug='proxmox',
            defaults={'name': 'Proxmox'},
        )
        device_type, _ = DeviceType.objects.get_or_create(
            slug='proxmox-node',
            defaults={'manufacturer': manufacturer, 'model': 'Proxmox Node'},
        )
    if site is None:
        site, _ = Site.objects.get_or_create(
            slug='proxmox2netbox',
            defaults={'name': 'Proxmox2NetBox'},
        )
    node_role, _ = DeviceRole.objects.get_or_create(
        slug='proxmox-node',
        defaults={'name': 'Proxmox Node', 'vm_role': False},
    )
    qemu_role, _ = DeviceRole.objects.get_or_create(
        slug='proxmox-vm-qemu',
        defaults={'name': 'Proxmox VM (QEMU)', 'vm_role': True},
    )
    lxc_role, _ = DeviceRole.objects.get_or_create(
        slug='proxmox-vm-lxc',
        defaults={'name': 'Proxmox Container (LXC)', 'vm_role': True},
    )
    cluster_type, _ = ClusterType.objects.get_or_create(
        slug='proxmox-' + mode,
        defaults={'name': 'Proxmox ' + mode.capitalize()},
    )
    return {
        'tag': tag,
        'manufacturer': manufacturer,
        'device_type': device_type,
        'site': site,
        'node_role': node_role,
        'qemu_role': qemu_role,
        'lxc_role': lxc_role,
        'cluster_type': cluster_type,
    }

def _upsert_cluster(cluster_name, cluster_type, tag, site=None):
    cluster = Cluster.objects.filter(name=cluster_name).order_by('pk').first()
    if cluster is None:
        create_kwargs = {'name': cluster_name, 'type': cluster_type}
        if site is not None:
            create_kwargs['scope'] = site
        cluster = Cluster.objects.create(**create_kwargs)
    else:
        update_fields = []
        if not cluster.type_id == cluster_type.id:
            cluster.type = cluster_type
            update_fields.append('type')
        if site is not None and not cluster.scope_id == site.id:
            cluster.scope = site
            update_fields.append('scope_type')
            update_fields.append('scope_id')
        if update_fields:
            cluster.save(update_fields=update_fields)
    _safe_add_tag(cluster, tag)
    return cluster


def _fetch_vm_config(client, node, vm_type, vmid):
    try:
        if vm_type == 'lxc':
            return client.nodes(node).lxc(vmid).config.get() or {}
        return client.nodes(node).qemu(vmid).config.get() or {}
    except Exception:
        logger.warning('Failed to fetch config for %s %s on node %s', vm_type, vmid, node)
        return {}

def _try_agent_ips_by_mac(client, node, vmid):
    """Return {MAC_UPPER: [ip_string, ...]} from the QEMU guest agent.

    Keying by MAC lets the caller match agent-reported interfaces to
    the correct Proxmox net<N> entry without relying on interface names
    (which differ between guest OS and Proxmox config).
    """
    try:
        ifaces = client.nodes(node).qemu(vmid).agent('network-get-interfaces').get()
        if not ifaces:
            return {}
        by_mac = {}
        for iface in (ifaces.get('result') or []):
            if (iface.get('name') or '').lower() in ('lo', 'loopback'):
                continue
            mac = (iface.get('hardware-address') or '').upper().strip()
            if not mac:
                continue
            ips = []
            for ip_info in (iface.get('ip-addresses') or []):
                addr = ip_info.get('ip-address', '')
                prefix_len = ip_info.get('prefix', '')
                if not addr or not prefix_len:
                    continue
                try:
                    net = _ipaddress.ip_interface(addr + '/' + str(prefix_len))
                    if net.is_link_local or net.is_loopback:
                        continue
                    ips.append(str(net))
                except ValueError:
                    pass
            if ips:
                by_mac[mac] = ips
        return by_mac
    except Exception:
        logger.debug('Guest agent not available for qemu %s on node %s', vmid, node)
        return {}


def _sync_iface_ips(vm, iface, ip_strings, vrf=None, tag=None):
    wanted = set()
    for s in ip_strings:
        try:
            net = _ipaddress.ip_interface(s)
            if net.is_link_local or net.is_loopback:
                continue
            wanted.add(str(net))
        except ValueError:
            pass
    content_type = ContentType.objects.get_for_model(VMInterface)
    existing = list(IPAddress.objects.filter(
        assigned_object_type=content_type,
        assigned_object_id=iface.pk,
    ))
    existing_by_addr = {str(ip.address): ip for ip in existing}
    for addr in wanted:
        if addr in existing_by_addr:
            ip = existing_by_addr[addr]
            if vrf is not None and not ip.vrf_id == vrf.pk:
                ip.vrf = vrf
                ip.save(update_fields=['vrf'])
            if tag is not None:
                _safe_add_tag(ip, tag)
            continue
        create_kwargs = {
            'address': addr,
            'assigned_object_type': content_type,
            'assigned_object_id': iface.pk,
        }
        if vrf is not None:
            create_kwargs['vrf'] = vrf
        ip = IPAddress.objects.create(**create_kwargs)
        if tag is not None:
            _safe_add_tag(ip, tag)
    if not wanted or tag is None:
        return
    ip_content_type = ContentType.objects.get_for_model(IPAddress, for_concrete_model=False)
    managed_ip_ids = set(TaggedItem.objects.filter(
        content_type=ip_content_type,
        object_id__in=[ip.pk for ip in existing if ip.pk is not None],
        tag__slug=tag.slug,
    ).values_list('object_id', flat=True))
    for addr, ip in existing_by_addr.items():
        if ip.pk in managed_ip_ids and addr not in wanted:
            ip.delete()


def _sync_iface_mac(iface, mac):
    if not mac:
        return
    iface_ct = ContentType.objects.get_for_model(VMInterface)
    existing = MACAddress.objects.filter(
        assigned_object_type=iface_ct,
        assigned_object_id=iface.pk,
    ).order_by('pk').first()
    if existing is None:
        mac_obj = MACAddress.objects.create(
            mac_address=mac,
            assigned_object_type=iface_ct,
            assigned_object_id=iface.pk,
        )
        iface.primary_mac_address = mac_obj
        iface.save(update_fields=['primary_mac_address'])
    elif not str(existing.mac_address).upper() == mac:
        existing.mac_address = mac
        existing.save(update_fields=['mac_address'])


def _upsert_vm_interfaces(vm, nets, tag, client=None, node=None, vmid=None, vm_type=None, config=None, vrf=None):
    # Per-interface IPs from Proxmox config (idx → [ip, ...])
    config_ips_by_idx = _extract_interface_ips(config or {}, vm_type or 'qemu')

    # Agent IPs fetched once lazily and keyed by MAC for correct matching
    agent_ips_by_mac = None

    existing = {iface.name: iface for iface in VMInterface.objects.filter(virtual_machine=vm)}
    seen_names = set()
    primary_ip_candidates = []
    for idx, key, net_value in nets:
        mac = _extract_mac(net_value)
        name = 'eth' + str(idx)
        desc = _iface_description(net_value)
        iface = existing.get(name)
        if iface is None:
            iface = VMInterface.objects.create(
                virtual_machine=vm,
                name=name,
                description=desc,
            )
        else:
            update_fields = []
            if not iface.description == desc:
                iface.description = desc
                update_fields.append('description')
            if update_fields:
                iface.save(update_fields=update_fields)
        _sync_iface_mac(iface, mac)
        _safe_add_tag(iface, tag)
        seen_names.add(name)

        # IPs for THIS interface from config
        ip_strs = config_ips_by_idx.get(idx, [])

        # Fallback: QEMU guest agent — match by MAC so IPs go to the right interface
        if not ip_strs and vm_type == 'qemu' and client and node and vmid and mac:
            if agent_ips_by_mac is None:
                agent_ips_by_mac = _try_agent_ips_by_mac(client, node, vmid)
            ip_strs = agent_ips_by_mac.get(mac, [])

        _sync_iface_ips(vm, iface, ip_strs, vrf=vrf, tag=tag)
        if ip_strs:
            primary_ip_candidates.extend(ip_strs)
    for name, iface in existing.items():
        if name not in seen_names:
            iface.delete()
    return primary_ip_candidates


def _sync_vm_disks(vm, disks, tag):
    existing = {d.name: d for d in VirtualDisk.objects.filter(virtual_machine=vm)}
    seen = set()
    for disk in disks:
        name = disk['key']
        size_mb = disk['size_mb']
        vd = existing.get(name)
        if vd is None:
            vd = VirtualDisk.objects.create(
                virtual_machine=vm,
                name=name,
                size=size_mb if size_mb is not None else 0,
            )
        else:
            if size_mb is not None and not vd.size == size_mb:
                vd.size = size_mb
                vd.save(update_fields=['size'])
        _safe_add_tag(vd, tag)
        seen.add(name)
    for name, vd in existing.items():
        if name not in seen:
            vd.delete()


def _set_vm_primary_ips(vm, ip_strings, vrf=None):
    v4 = None
    v6 = None
    for s in ip_strings:
        try:
            net = _ipaddress.ip_interface(s)
            if net.is_link_local or net.is_loopback:
                continue
            if net.version == 4 and v4 is None:
                vrf_filter = {'vrf': vrf} if vrf is not None else {'vrf__isnull': True}
                v4 = IPAddress.objects.filter(address=str(net), **vrf_filter).first()
            elif net.version == 6 and v6 is None:
                vrf_filter = {'vrf': vrf} if vrf is not None else {'vrf__isnull': True}
                v6 = IPAddress.objects.filter(address=str(net), **vrf_filter).first()
        except ValueError:
            pass
    update_fields = []
    if not vm.primary_ip4_id == (v4.pk if v4 else None):
        if v4 is not None:
            VirtualMachine.objects.filter(primary_ip4=v4).exclude(pk=vm.pk).update(primary_ip4=None)
            Device.objects.filter(primary_ip4=v4).update(primary_ip4=None)
        vm.primary_ip4 = v4
        update_fields.append('primary_ip4')
    if not vm.primary_ip6_id == (v6.pk if v6 else None):
        if v6 is not None:
            VirtualMachine.objects.filter(primary_ip6=v6).exclude(pk=vm.pk).update(primary_ip6=None)
            Device.objects.filter(primary_ip6=v6).update(primary_ip6=None)
        vm.primary_ip6 = v6
        update_fields.append('primary_ip6')
    if update_fields:
        vm.save(update_fields=update_fields)


def _sync_nodes(session, cluster, base):
    tag = base['tag']
    site = base['site']
    endpoint_device_type = base['device_type']
    node_role = base['node_role']

    # Build per-node override maps from the mapping table.
    node_mappings = {
        m.node_name: m
        for m in ProxmoxNodeTypeMapping.objects.filter(
            endpoint=session.endpoint
        ).select_related('device_type')
    }

    nodes_raw = session.client.nodes.get() or []
    seen_names = set()
    for node_data in nodes_raw:
        node_name = node_data.get('node', '')
        if not node_name:
            continue
        seen_names.add(node_name)
        raw_status = node_data.get('status', '')
        status = _status_from_proxmox(raw_status)

        # Explicit per-node mapping takes priority over the endpoint default.
        mapping = node_mappings.get(node_name)
        mapped_type = mapping.device_type if mapping else None
        device_name = (mapping.custom_name or node_name) if mapping else node_name

        # Look up by custom name first, fall back to node name for existing devices.
        device = Device.objects.filter(name=device_name, cluster=cluster).order_by('pk').first()
        if device is None and device_name != node_name:
            device = Device.objects.filter(name=node_name, cluster=cluster).order_by('pk').first()

        if device is None:
            # New node: use mapping if available, else endpoint default.
            device = Device.objects.create(
                name=device_name,
                cluster=cluster,
                site=site,
                device_type=mapped_type if mapped_type is not None else endpoint_device_type,
                role=node_role,
                status=status,
            )
        else:
            update_fields = []
            # Rename device if custom name is set and differs.
            if device.name != device_name:
                device.name = device_name
                update_fields.append('name')
            if not device.status == status:
                device.status = status
                update_fields.append('status')
            if not device.cluster_id == cluster.pk:
                device.cluster = cluster
                update_fields.append('cluster')
            if not device.role_id == node_role.pk:
                device.role = node_role
                update_fields.append('role')
            # Only update device_type when there is an explicit per-node mapping.
            # Without a mapping we leave whatever the user has set in NetBox.
            if mapped_type is not None and not device.device_type_id == mapped_type.pk:
                device.device_type = mapped_type
                update_fields.append('device_type')
            if update_fields:
                device.save(update_fields=update_fields)
        _safe_add_tag(device, tag)
    return seen_names


def _sync_vms(session, cluster, base):
    client = session.client
    tag = base['tag']
    qemu_role = base['qemu_role']
    lxc_role = base['lxc_role']
    site = base['site']
    vrf = getattr(session.endpoint, 'netbox_vrf', None)
    nodes_raw = client.nodes.get() or []
    for node_data in nodes_raw:
        node_name = node_data.get('node', '')
        if not node_name:
            continue
        for vm_type in ('qemu', 'lxc'):
            try:
                if vm_type == 'lxc':
                    vms_raw = client.nodes(node_name).lxc.get() or []
                else:
                    vms_raw = client.nodes(node_name).qemu.get() or []
            except Exception:
                logger.warning('Failed to fetch %s list from node %s', vm_type, node_name)
                continue
            for vm_data in vms_raw:
                vmid = vm_data.get('vmid')
                vm_name = vm_data.get('name', 'vm-' + str(vmid))
                raw_status = vm_data.get('status', '')
                status = _status_from_proxmox(raw_status)
                vcpus = vm_data.get('cpus') or vm_data.get('maxcpu')
                memory_mb = None
                raw_mem = vm_data.get('maxmem')
                if raw_mem:
                    memory_mb = int(raw_mem) // (1024 * 1024)
                role = qemu_role if vm_type == 'qemu' else lxc_role
                vm = VirtualMachine.objects.filter(name=vm_name, cluster=cluster).order_by('pk').first()
                if vm is None:
                    create_kwargs = {
                        'name': vm_name,
                        'cluster': cluster,
                        'status': status,
                        'role': role,
                    }
                    if site is not None:
                        create_kwargs['site'] = site
                    if vcpus is not None:
                        create_kwargs['vcpus'] = vcpus
                    if memory_mb is not None:
                        create_kwargs['memory'] = memory_mb
                    vm = VirtualMachine.objects.create(**create_kwargs)
                else:
                    update_fields = []
                    if not vm.status == status:
                        vm.status = status
                        update_fields.append('status')
                    if not vm.role_id == role.pk:
                        vm.role = role
                        update_fields.append('role')
                    if vcpus is not None and not vm.vcpus == vcpus:
                        vm.vcpus = vcpus
                        update_fields.append('vcpus')
                    if memory_mb is not None and not vm.memory == memory_mb:
                        vm.memory = memory_mb
                        update_fields.append('memory')
                    if update_fields:
                        vm.save(update_fields=update_fields)
                _safe_add_tag(vm, tag)
                config = _fetch_vm_config(client, node_name, vm_type, vmid)
                nets = _extract_vm_config_networks(config)
                primary_ip_candidates = _upsert_vm_interfaces(
                    vm, nets, tag,
                    client=client, node=node_name, vmid=vmid,
                    vm_type=vm_type, config=config, vrf=vrf,
                )
                disks = _extract_vm_config_disks(vm_type, config)
                _sync_vm_disks(vm, disks, tag)
                if primary_ip_candidates:
                    _set_vm_primary_ips(vm, primary_ip_candidates, vrf=vrf)


def _upsert_all_for_session(session, sync_type):
    endpoint = session.endpoint
    meta = _update_endpoint_metadata(session)
    mode = meta['mode']
    cluster_name = meta['name'] or str(endpoint)
    netbox_site = getattr(endpoint, 'netbox_site', None)
    netbox_device_type = getattr(endpoint, 'netbox_device_type', None)
    base = _ensure_base_objects(mode, site=netbox_site, device_type=netbox_device_type)
    cluster = _upsert_cluster(cluster_name, base['cluster_type'], base['tag'], site=base['site'] if netbox_site is None else netbox_site)
    if sync_type in (SyncTypeChoices.ALL, SyncTypeChoices.DEVICES):
        _sync_nodes(session, cluster, base)
    if sync_type in (SyncTypeChoices.ALL, SyncTypeChoices.VIRTUAL_MACHINES):
        _sync_vms(session, cluster, base)


def check_endpoint_connection(endpoint):
    try:
        session = connect_endpoint(endpoint)
        return {'ok': True, 'host': session.host, 'version': session.version}
    except ProxmoxSyncError as exc:
        return {'ok': False, 'error': str(exc)}


def get_endpoint_cluster_summary(endpoint):
    session = connect_endpoint(endpoint)
    meta = _update_endpoint_metadata(session)
    return meta


def sync_devices():
    endpoints = ProxmoxEndpoint.objects.all()
    errors = []
    for endpoint in endpoints:
        try:
            session = connect_endpoint(endpoint)
            _upsert_all_for_session(session, SyncTypeChoices.DEVICES)
        except Exception as exc:
            logger.exception('sync_devices failed for endpoint %s', endpoint)
            errors.append(str(exc))
    if errors:
        raise ProxmoxSyncError(f'sync_devices errors: {"; ".join(errors)}')


def sync_virtual_machines():
    endpoints = ProxmoxEndpoint.objects.all()
    errors = []
    for endpoint in endpoints:
        try:
            session = connect_endpoint(endpoint)
            _upsert_all_for_session(session, SyncTypeChoices.VIRTUAL_MACHINES)
        except Exception as exc:
            logger.exception('sync_virtual_machines failed for endpoint %s', endpoint)
            errors.append(str(exc))
    if errors:
        raise ProxmoxSyncError(f'sync_virtual_machines errors: {"; ".join(errors)}')


def sync_full_update():
    endpoints = ProxmoxEndpoint.objects.all()
    errors = []
    for endpoint in endpoints:
        try:
            session = connect_endpoint(endpoint)
            _upsert_all_for_session(session, SyncTypeChoices.ALL)
        except Exception as exc:
            logger.exception('sync_full_update failed for endpoint %s', endpoint)
            errors.append(str(exc))
    if errors:
        raise ProxmoxSyncError(f'sync_full_update errors: {"; ".join(errors)}')
