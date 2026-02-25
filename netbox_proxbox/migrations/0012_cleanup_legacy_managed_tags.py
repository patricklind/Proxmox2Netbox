from django.db import migrations
from django.db.models import Count, Min


MANAGED_TAG_SLUG = "proxmox2netbox"
LEGACY_TAG_SLUGS = (
    "proxbox",
    "netbox-proxbox",
    "proxmox2netbox-plugin",
)


def cleanup_legacy_managed_tags(apps, schema_editor):
    Tag = apps.get_model("extras", "Tag")
    TaggedItem = apps.get_model("extras", "TaggedItem")

    managed_tag, _ = Tag.objects.get_or_create(
        slug=MANAGED_TAG_SLUG,
        defaults={
            "name": "Proxmox2NetBox",
            "color": "ff5722",
            "description": "Objects managed by proxmox2netbox",
        },
    )

    managed_tag_changed = False
    if managed_tag.name != "Proxmox2NetBox":
        managed_tag.name = "Proxmox2NetBox"
        managed_tag_changed = True
    if managed_tag.color != "ff5722":
        managed_tag.color = "ff5722"
        managed_tag_changed = True
    if managed_tag.description != "Objects managed by proxmox2netbox":
        managed_tag.description = "Objects managed by proxmox2netbox"
        managed_tag_changed = True
    if managed_tag_changed:
        managed_tag.save(update_fields=["name", "color", "description"])

    for slug in LEGACY_TAG_SLUGS:
        if slug == MANAGED_TAG_SLUG:
            continue
        legacy_tag = Tag.objects.filter(slug=slug).first()
        if legacy_tag is None:
            continue

        TaggedItem.objects.filter(tag_id=legacy_tag.pk).update(tag_id=managed_tag.pk)

        if not TaggedItem.objects.filter(tag_id=legacy_tag.pk).exists():
            legacy_tag.delete()

    duplicate_groups = (
        TaggedItem.objects.filter(tag_id=managed_tag.pk)
        .values("content_type_id", "object_id")
        .annotate(min_pk=Min("pk"), total=Count("pk"))
        .filter(total__gt=1)
    )

    for group in duplicate_groups:
        TaggedItem.objects.filter(
            tag_id=managed_tag.pk,
            content_type_id=group["content_type_id"],
            object_id=group["object_id"],
        ).exclude(pk=group["min_pk"]).delete()


def noop_reverse(apps, schema_editor):
    return


class Migration(migrations.Migration):

    dependencies = [
        ("netbox_proxbox", "0011_alter_fastapiendpoint_name"),
    ]

    operations = [
        migrations.RunPython(cleanup_legacy_managed_tags, noop_reverse),
    ]
