"""Unit tests for proxmox2netbox.services._parse.

These tests cover all pure parsing utility functions.
No Django/NetBox setup required — _parse.py has no side effects or ORM imports.
The module is loaded directly via importlib to avoid the package __init__.py
import chain which requires a live Django environment.
"""
import importlib.util
import os

# Load _parse.py directly, bypassing the proxmox2netbox package init chain.
_PARSE_PATH = os.path.normpath(
    os.path.join(os.path.dirname(__file__), '..', 'proxmox2netbox', 'services', '_parse.py')
)
_spec = importlib.util.spec_from_file_location('proxmox2netbox.services._parse', _PARSE_PATH)
_parse_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_parse_mod)

QEMU_NIC_MODELS = _parse_mod.QEMU_NIC_MODELS
extract_interface_ips = _parse_mod.extract_interface_ips
extract_mac = _parse_mod.extract_mac
extract_vm_config_disks = _parse_mod.extract_vm_config_disks
extract_vm_config_networks = _parse_mod.extract_vm_config_networks
iface_description = _parse_mod.iface_description
size_token_to_mb = _parse_mod.size_token_to_mb
status_from_proxmox = _parse_mod.status_from_proxmox


# ---------------------------------------------------------------------------
# status_from_proxmox
# ---------------------------------------------------------------------------

class TestStatusFromProxmox:
    def test_running_maps_to_active(self):
        assert status_from_proxmox('running') == 'active'

    def test_online_maps_to_active(self):
        """Proxmox nodes report 'online' instead of 'running'."""
        assert status_from_proxmox('online') == 'active'

    def test_stopped_maps_to_offline(self):
        assert status_from_proxmox('stopped') == 'offline'

    def test_paused_maps_to_offline(self):
        assert status_from_proxmox('paused') == 'offline'

    def test_offline_maps_to_offline(self):
        """Proxmox nodes report 'offline' instead of 'stopped'."""
        assert status_from_proxmox('offline') == 'offline'

    def test_unknown_maps_to_staged(self):
        assert status_from_proxmox('unknown') == 'staged'
        assert status_from_proxmox('') == 'staged'
        assert status_from_proxmox('migrating') == 'staged'


# ---------------------------------------------------------------------------
# extract_mac
# ---------------------------------------------------------------------------

class TestExtractMac:
    def test_virtio_nic(self):
        assert extract_mac('virtio=AA:BB:CC:DD:EE:FF,bridge=vmbr0') == 'AA:BB:CC:DD:EE:FF'

    def test_e1000_nic(self):
        assert extract_mac('e1000=11:22:33:44:55:66,bridge=vmbr1,tag=10') == '11:22:33:44:55:66'

    def test_hwaddr_lxc(self):
        assert extract_mac('name=eth0,hwaddr=DE:AD:BE:EF:00:01,bridge=vmbr0') == 'DE:AD:BE:EF:00:01'

    def test_lowercases_input_normalised_to_upper(self):
        # Raw Proxmox output can have mixed case
        assert extract_mac('virtio=aa:bb:cc:dd:ee:ff') == 'AA:BB:CC:DD:EE:FF'

    def test_returns_none_when_no_nic_key(self):
        assert extract_mac('bridge=vmbr0,tag=10') is None

    def test_returns_none_for_malformed_mac(self):
        assert extract_mac('virtio=ZZ:ZZ:ZZ:ZZ:ZZ:ZZ') is None

    def test_returns_none_for_empty_string(self):
        assert extract_mac('') is None

    def test_extra_whitespace_tolerated(self):
        assert extract_mac(' virtio=AA:BB:CC:DD:EE:FF , bridge=vmbr0 ') == 'AA:BB:CC:DD:EE:FF'


# ---------------------------------------------------------------------------
# iface_description
# ---------------------------------------------------------------------------

class TestIfaceDescription:
    def test_bridge_and_vlan(self):
        desc = iface_description('virtio=AA:BB:CC:DD:EE:FF,bridge=vmbr0,tag=20')
        assert 'bridge=vmbr0' in desc
        assert 'vlan=20' in desc

    def test_rate_included(self):
        desc = iface_description('virtio=AA:BB:CC:DD:EE:FF,rate=100')
        assert 'rate=100MB/s' in desc

    def test_model_appended(self):
        desc = iface_description('virtio=AA:BB:CC:DD:EE:FF,bridge=vmbr0')
        assert 'virtio' in desc

    def test_fallback_when_no_tokens(self):
        assert iface_description('') == 'Proxmox network interface'

    def test_fallback_when_only_mac(self):
        assert iface_description('virtio=AA:BB:CC:DD:EE:FF') == 'virtio'


# ---------------------------------------------------------------------------
# extract_vm_config_networks
# ---------------------------------------------------------------------------

class TestExtractVmConfigNetworks:
    def test_single_interface(self):
        config = {'net0': 'virtio=AA:BB:CC:DD:EE:FF,bridge=vmbr0', 'cores': 2}
        nets = extract_vm_config_networks(config)
        assert len(nets) == 1
        idx, key, value = nets[0]
        assert idx == 0
        assert key == 'net0'

    def test_sorted_by_index(self):
        config = {'net2': 'e1000=...', 'net0': 'virtio=...', 'net1': 'rtl8139=...'}
        nets = extract_vm_config_networks(config)
        assert [n[0] for n in nets] == [0, 1, 2]

    def test_non_net_keys_excluded(self):
        config = {'net0': 'virtio=...', 'ipconfig0': 'ip=10.0.0.1/24', 'memory': 2048}
        nets = extract_vm_config_networks(config)
        assert len(nets) == 1

    def test_empty_config(self):
        assert extract_vm_config_networks({}) == []


# ---------------------------------------------------------------------------
# size_token_to_mb
# ---------------------------------------------------------------------------

class TestSizeTokenToMb:
    def test_gigabytes(self):
        assert size_token_to_mb('32G') == 32 * 1024

    def test_gigabytes_no_suffix_treated_as_gb(self):
        assert size_token_to_mb('10') == 10 * 1024

    def test_megabytes(self):
        assert size_token_to_mb('512M') == 512

    def test_kilobytes(self):
        assert size_token_to_mb('2048K') == 2  # 2048 // 1024 == 2

    def test_terabytes(self):
        assert size_token_to_mb('1T') == 1024 * 1024

    def test_decimal(self):
        assert size_token_to_mb('1.5G') == int(1.5 * 1024)

    def test_lowercase(self):
        assert size_token_to_mb('32g') == 32 * 1024

    def test_invalid_returns_none(self):
        assert size_token_to_mb('abc') is None
        assert size_token_to_mb('') is None

    def test_kilobytes_less_than_1mb_clamps_to_1(self):
        assert size_token_to_mb('512K') == 1


# ---------------------------------------------------------------------------
# extract_vm_config_disks
# ---------------------------------------------------------------------------

class TestExtractVmConfigDisks:
    def test_qemu_virtio_disk(self):
        config = {'virtio0': 'local-lvm:vm-100-disk-0,size=32G', 'net0': 'virtio=...'}
        disks = extract_vm_config_disks('qemu', config)
        assert len(disks) == 1
        assert disks[0]['key'] == 'virtio0'
        assert disks[0]['size_mb'] == 32 * 1024

    def test_qemu_scsi_disk(self):
        config = {'scsi0': 'local-lvm:vm-100-disk-0,size=100G'}
        disks = extract_vm_config_disks('qemu', config)
        assert disks[0]['size_mb'] == 100 * 1024

    def test_lxc_rootfs(self):
        config = {'rootfs': 'local-lvm:vm-101-disk-0,size=8G', 'net0': 'name=eth0,...'}
        disks = extract_vm_config_disks('lxc', config)
        assert len(disks) == 1
        assert disks[0]['key'] == 'rootfs'
        assert disks[0]['size_mb'] == 8 * 1024

    def test_lxc_mp(self):
        config = {'mp0': 'local:101/vm-101-mp0.raw,mp=/data,size=50G'}
        disks = extract_vm_config_disks('lxc', config)
        assert disks[0]['size_mb'] == 50 * 1024

    def test_size_from_inline_token(self):
        config = {'virtio0': 'local-lvm:disk-0,size=16G,discard=on'}
        disks = extract_vm_config_disks('qemu', config)
        assert disks[0]['size_mb'] == 16 * 1024

    def test_no_size_returns_none(self):
        config = {'virtio0': 'local-lvm:disk-0'}
        disks = extract_vm_config_disks('qemu', config)
        assert disks[0]['size_mb'] is None

    def test_empty_config(self):
        assert extract_vm_config_disks('qemu', {}) == []


# ---------------------------------------------------------------------------
# extract_interface_ips
# ---------------------------------------------------------------------------

class TestExtractInterfaceIps:
    def test_qemu_static_ip(self):
        config = {'ipconfig0': 'ip=10.0.0.5/24,gw=10.0.0.1'}
        result = extract_interface_ips(config, 'qemu')
        assert result == {0: ['10.0.0.5/24']}

    def test_qemu_dhcp_excluded(self):
        config = {'ipconfig0': 'ip=dhcp'}
        assert extract_interface_ips(config, 'qemu') == {}

    def test_qemu_multiple_interfaces(self):
        config = {
            'ipconfig0': 'ip=10.0.0.5/24',
            'ipconfig1': 'ip=192.168.1.10/24',
        }
        result = extract_interface_ips(config, 'qemu')
        assert len(result) == 2
        assert result[0] == ['10.0.0.5/24']
        assert result[1] == ['192.168.1.10/24']

    def test_qemu_ipv6(self):
        config = {'ipconfig0': 'ip6=2001:db8::1/64'}
        result = extract_interface_ips(config, 'qemu')
        assert result == {0: ['2001:db8::1/64']}

    def test_lxc_static_ip_inline(self):
        config = {'net0': 'name=eth0,hwaddr=AA:BB:CC:DD:EE:FF,bridge=vmbr0,ip=10.0.0.10/24'}
        result = extract_interface_ips(config, 'lxc')
        assert result == {0: ['10.0.0.10/24']}

    def test_lxc_dhcp_excluded(self):
        config = {'net0': 'name=eth0,bridge=vmbr0,ip=dhcp'}
        assert extract_interface_ips(config, 'lxc') == {}

    def test_lxc_manual_excluded(self):
        config = {'net0': 'name=eth0,bridge=vmbr0,ip=manual'}
        assert extract_interface_ips(config, 'lxc') == {}

    def test_empty_config(self):
        assert extract_interface_ips({}, 'qemu') == {}
        assert extract_interface_ips({}, 'lxc') == {}
