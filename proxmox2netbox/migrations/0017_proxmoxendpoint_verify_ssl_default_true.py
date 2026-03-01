from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("proxmox2netbox", "0016_proxmoxnodetypemapping_fix"),
    ]

    operations = [
        migrations.AlterField(
            model_name="proxmoxendpoint",
            name="verify_ssl",
            field=models.BooleanField(
                default=True,
                help_text="Choose or not to verify SSL certificate of the Proxmox Endpoint",
                verbose_name="Verify SSL",
            ),
        ),
    ]
