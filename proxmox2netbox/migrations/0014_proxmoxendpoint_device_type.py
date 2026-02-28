import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("proxmox2netbox", "0013_proxmoxendpoint_site_vrf"),
        ("dcim", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="proxmoxendpoint",
            name="netbox_device_type",
            field=models.ForeignKey(
                blank=True,
                null=True,
                help_text='Device type to assign to synced Proxmox nodes. If not set, one is auto-detected from the node\'s CPU model or a generic "Proxmox Node" type is used.',
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="+",
                to="dcim.devicetype",
                verbose_name="Node Device Type",
            ),
        ),
    ]
