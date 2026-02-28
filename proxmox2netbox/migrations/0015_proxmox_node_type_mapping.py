import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("proxmox2netbox", "0014_proxmoxendpoint_device_type"),
        ("dcim", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="ProxmoxNodeTypeMapping",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ("created", models.DateTimeField(auto_now_add=True, null=True)),
                ("last_updated", models.DateTimeField(auto_now=True, null=True)),
                (
                    "custom_field_data",
                    models.JSONField(blank=True, default=dict, encoder=None),
                ),
                (
                    "node_name",
                    models.CharField(
                        max_length=255,
                        verbose_name="Node Name",
                        help_text="Exact node name as reported by Proxmox (e.g. pve01).",
                    ),
                ),
                (
                    "endpoint",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="node_type_mappings",
                        to="proxmox2netbox.proxmoxendpoint",
                        verbose_name="Proxmox Endpoint",
                    ),
                ),
                (
                    "device_type",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="+",
                        to="dcim.devicetype",
                        verbose_name="Device Type",
                        help_text="Device type to assign to this node when syncing.",
                    ),
                ),
            ],
            options={
                "verbose_name": "Node Device Type Mapping",
                "verbose_name_plural": "Node Device Type Mappings",
                "ordering": ("endpoint", "node_name"),
                "unique_together": {("endpoint", "node_name")},
            },
        ),
    ]
