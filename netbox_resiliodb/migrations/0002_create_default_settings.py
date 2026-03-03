from django.db import migrations


def create_default_settings(apps, schema_editor):
    PluginSettings = apps.get_model("netbox_resiliodb", "PluginSettings")
    if not PluginSettings.objects.filter(pk=1).exists():
        PluginSettings.objects.create(
            pk=1,
            api_url="https://db.resilio.tech",
            api_version="2024.1",
            api_key="default-key-please-change",
        )


def reverse_default_settings(apps, schema_editor):
    PluginSettings = apps.get_model("netbox_resiliodb", "PluginSettings")
    PluginSettings.objects.filter(pk=1).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("netbox_resiliodb", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(create_default_settings, reverse_default_settings)
    ]
