import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("proxmox2netbox", "0012_cleanup_legacy_managed_tags"),
        ("dcim", "0001_initial"),
        ("ipam", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="proxmoxendpoint",
            name="netbox_site",
            field=models.ForeignKey(
                blank=True,
                null=True,
                help_text="NetBox site to assign synced objects to. If not set, a default site is used.",
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="+",
                to="dcim.site",
                verbose_name="NetBox Site",
            ),
        ),
        migrations.AddField(
            model_name="proxmoxendpoint",
            name="netbox_vrf",
            field=models.ForeignKey(
                blank=True,
                null=True,
                help_text="VRF to assign synced IP addresses to. If not set, the global routing table is used.",
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="+",
                to="ipam.vrf",
                verbose_name="NetBox VRF",
            ),
        ),
    ]
