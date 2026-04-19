from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("proxmox2netbox", "0019_proxmoxendpoint_last_sync_fields"),
    ]

    operations = [
        migrations.AddField(
            model_name="proxmoxendpoint",
            name="sync_enabled",
            field=models.BooleanField(
                default=True,
                help_text="Include this endpoint in manual and scheduled sync runs.",
                verbose_name="Sync Enabled",
            ),
        ),
        migrations.AddField(
            model_name="proxmoxendpoint",
            name="sync_nodes",
            field=models.BooleanField(
                default=True,
                help_text="Create and update Proxmox nodes as NetBox devices.",
                verbose_name="Sync Nodes",
            ),
        ),
        migrations.AddField(
            model_name="proxmoxendpoint",
            name="sync_qemu_vms",
            field=models.BooleanField(
                default=True,
                help_text="Create and update QEMU virtual machines.",
                verbose_name="Sync QEMU VMs",
            ),
        ),
        migrations.AddField(
            model_name="proxmoxendpoint",
            name="sync_lxc_containers",
            field=models.BooleanField(
                default=True,
                help_text="Create and update LXC containers as NetBox virtual machines.",
                verbose_name="Sync LXC Containers",
            ),
        ),
        migrations.AddField(
            model_name="proxmoxendpoint",
            name="sync_vm_interfaces",
            field=models.BooleanField(
                default=True,
                help_text="Create and update VM interfaces from Proxmox network configuration.",
                verbose_name="Sync VM Interfaces",
            ),
        ),
        migrations.AddField(
            model_name="proxmoxendpoint",
            name="sync_vm_ips",
            field=models.BooleanField(
                default=True,
                help_text="Assign VM interface IP addresses from Proxmox config and guest-agent data.",
                verbose_name="Sync VM IP Addresses",
            ),
        ),
        migrations.AddField(
            model_name="proxmoxendpoint",
            name="sync_guest_agent_ips",
            field=models.BooleanField(
                default=True,
                help_text="Use QEMU guest-agent network data when Proxmox static config has no IPs.",
                verbose_name="Use Guest Agent IPs",
            ),
        ),
        migrations.AddField(
            model_name="proxmoxendpoint",
            name="sync_vm_disks",
            field=models.BooleanField(
                default=True,
                help_text="Create and update NetBox virtual disks from Proxmox VM disk config.",
                verbose_name="Sync VM Disks",
            ),
        ),
        migrations.AddField(
            model_name="proxmoxendpoint",
            name="prune_stale_vm_interfaces",
            field=models.BooleanField(
                default=True,
                help_text="Delete plugin-managed VM interfaces that no longer exist in Proxmox config.",
                verbose_name="Prune Stale VM Interfaces",
            ),
        ),
        migrations.AddField(
            model_name="proxmoxendpoint",
            name="prune_stale_vm_ips",
            field=models.BooleanField(
                default=True,
                help_text="Delete plugin-managed interface IPs that no longer exist in Proxmox config.",
                verbose_name="Prune Stale VM IPs",
            ),
        ),
        migrations.AddField(
            model_name="proxmoxendpoint",
            name="prune_stale_vm_disks",
            field=models.BooleanField(
                default=True,
                help_text="Delete plugin-managed virtual disks that no longer exist in Proxmox config.",
                verbose_name="Prune Stale VM Disks",
            ),
        ),
    ]
