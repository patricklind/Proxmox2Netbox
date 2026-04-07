from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('proxmox2netbox', '0018_add_custom_name_to_node_mapping'),
    ]

    operations = [
        migrations.AddField(
            model_name='proxmoxendpoint',
            name='last_synced',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Last Synced'),
        ),
        migrations.AddField(
            model_name='proxmoxendpoint',
            name='last_sync_status',
            field=models.CharField(blank=True, default='', max_length=20, verbose_name='Last Sync Status'),
        ),
    ]
