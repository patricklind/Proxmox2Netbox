"""
Pure parsing utilities for Proxmox API data.

All functions in this module are side-effect free and have no Django/NetBox
dependencies so they can be unit-tested without a database or application setup.
"""
from __future__ import annotations

import re

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

#: NIC model names used as keys in Proxmox net<N> config values.
QEMU_NIC_MODELS: frozenset[str] = frozenset({
    'virtio', 'e1000', 'e1000e', 'rtl8139', 'vmxnet3',
    'ne2k_pci', 'ne2k_isa', 'pcnet', 'i82551', 'i82557b', 'i82559er',
})

# Pre-compiled regex patterns.
_RE_MAC = re.compile(r'^[0-9A-F]{2}(:[0-9A-F]{2}){5}$')
_RE_NET_KEY = re.compile(r'^net\d+$')
_RE_NET_CAPTURE = re.compile(r'^net(\d+)$')
_RE_IPCONFIG_KEY = re.compile(r'^ipconfig(\d+)$')
_RE_LXC_DISK = re.compile(r'^(rootfs|mp\d+)$')
_RE_QEMU_DISK = re.compile(r'^(virtio|scsi|sata|ide|efidisk|tpmstate)\d+$')
_RE_SIZE_TOKEN = re.compile(r'^(\d+(?:\.\d+)?)([KMGT]?)$')


# ---------------------------------------------------------------------------
# Proxmox status
# ---------------------------------------------------------------------------

def status_from_proxmox(raw_status: str) -> str:
    """Map a Proxmox resource status string to a NetBox status slug."""
    if raw_status == 'running':
        return 'active'
    if raw_status in ('stopped', 'paused'):
        return 'offline'
    return 'staged'


# ---------------------------------------------------------------------------
# Network interface parsing
# ---------------------------------------------------------------------------

def extract_mac(net_value: str) -> str | None:
    """Return the MAC address from a Proxmox net<N> config string, or None.

    The net<N> value looks like::

        virtio=AA:BB:CC:DD:EE:FF,bridge=vmbr0,tag=10

    The NIC model key (virtio, e1000, …) holds the MAC as its value.
    LXC uses ``hwaddr`` as the key instead.
    """
    for part in net_value.split(','):
        part = part.strip()
        if '=' not in part:
            continue
        k, v = part.split('=', 1)
        k_lower = k.lower()
        if k_lower in QEMU_NIC_MODELS or k_lower == 'hwaddr':
            mac = v.strip().upper()
            if _RE_MAC.match(mac):
                return mac
    return None


def iface_description(net_value: str) -> str:
    """Build a short human-readable description from a Proxmox net<N> value."""
    parts: list[str] = []
    model = None
    for token in net_value.split(','):
        token = token.strip()
        if not token or '=' not in token:
            continue
        k, v = token.split('=', 1)
        k_lower = k.lower()
        if k_lower == 'bridge':
            parts.append('bridge=' + v)
        elif k_lower == 'tag':
            parts.append('vlan=' + v)
        elif k_lower == 'rate':
            parts.append('rate=' + v + 'MB/s')
        elif k_lower in QEMU_NIC_MODELS:
            model = k_lower
    if model:
        parts.append(model)
    return ', '.join(parts) if parts else 'Proxmox network interface'


def extract_vm_config_networks(config: dict) -> list[tuple[int, str, str]]:
    """Return [(idx, key, value), …] for all net<N> entries in a VM config, sorted by index."""
    nets = []
    for key, value in config.items():
        if _RE_NET_KEY.match(key):
            idx = int(key[3:])
            nets.append((idx, key, str(value)))
    nets.sort(key=lambda x: x[0])
    return nets


# ---------------------------------------------------------------------------
# Disk parsing
# ---------------------------------------------------------------------------

def size_token_to_mb(token: str) -> int | None:
    """Convert a Proxmox size string (e.g. ``32G``, ``512M``, ``2T``) to MB.

    Returns ``None`` if the token cannot be parsed.
    """
    token = token.strip().upper()
    m = _RE_SIZE_TOKEN.match(token)
    if not m:
        return None
    num = float(m.group(1))
    unit = m.group(2)
    if unit in ('', 'G'):
        return int(num * 1024)
    if unit == 'M':
        return int(num)
    if unit == 'K':
        return max(1, int(num // 1024))
    if unit == 'T':
        return int(num * 1024 * 1024)
    return None


def extract_vm_config_disks(vm_type: str, config: dict) -> list[dict]:
    """Return a list of ``{'key': …, 'size_mb': …}`` dicts for all disk entries."""
    disks = []
    if vm_type == 'lxc':
        disk_keys = [k for k in config if _RE_LXC_DISK.match(k)]
    else:
        disk_keys = [k for k in config if _RE_QEMU_DISK.match(k)]
    for key in disk_keys:
        value = str(config[key])
        size_mb = None
        for token in value.split(','):
            token = token.strip()
            if token.lower().startswith('size='):
                size_mb = size_token_to_mb(token[5:])
                break
        if size_mb is None:
            first = value.split(',')[0].strip()
            if ':' in first:
                size_mb = size_token_to_mb(first.split(':')[1])
        disks.append({'key': key, 'size_mb': size_mb})
    return disks


# ---------------------------------------------------------------------------
# IP address parsing
# ---------------------------------------------------------------------------

def extract_interface_ips(config: dict, vm_type: str) -> dict[int, list[str]]:
    """Return ``{net_idx: [ip_string, …]}`` for all statically configured IPs.

    For LXC, IPs are embedded in ``net<N>`` values as ``ip=…`` tokens.
    For QEMU, IPs are in separate ``ipconfig<N>`` keys that map 1-to-1 to ``net<N>``.
    """
    result: dict[int, list[str]] = {}
    if vm_type == 'lxc':
        for key, value in config.items():
            m = _RE_NET_CAPTURE.match(key)
            if not m:
                continue
            idx = int(m.group(1))
            ips = []
            for token in str(value).split(','):
                token = token.strip()
                low = token.lower()
                if low.startswith('ip=') or low.startswith('ip6='):
                    addr = token.split('=', 1)[1].strip()
                    if addr and addr not in ('dhcp', 'auto', 'manual'):
                        ips.append(addr)
            if ips:
                result[idx] = ips
    else:
        for key, value in config.items():
            m = _RE_IPCONFIG_KEY.match(key)
            if not m:
                continue
            idx = int(m.group(1))
            ips = []
            for token in str(value).split(','):
                token = token.strip()
                low = token.lower()
                if low.startswith('ip=') or low.startswith('ip6='):
                    addr = token.split('=', 1)[1].strip()
                    if addr and addr not in ('dhcp', 'auto'):
                        ips.append(addr)
            if ips:
                result[idx] = ips
    return result
