import taggit.managers
import utilities.json
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("proxmox2netbox", "0015_proxmox_node_type_mapping"),
        ("extras", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="proxmoxnodetypemapping",
            name="custom_field_data",
            field=models.JSONField(
                blank=True,
                default=dict,
                encoder=utilities.json.CustomFieldJSONEncoder,
            ),
        ),
        migrations.AddField(
            model_name="proxmoxnodetypemapping",
            name="tags",
            field=taggit.managers.TaggableManager(
                through="extras.TaggedItem",
                to="extras.Tag",
            ),
        ),
    ]
