from django.db import migrations

def create_default_lca_types(apps, schema_editor):
    LCAType = apps.get_model('netbox_resiliodb', 'LCAType')

    default_types = [
        {
            'name': 'Blade Enclosure',
            'resilio_endpoint': 'blade_enclosure',
            'description': 'Chassis housing multiple blade servers, including power supplies and cooling',
            'default_payload': {
                "usage_percent": 1,
                "rack_unit": 5,
                "wanted_name": "blade_enclosure",
                "usage": {
                    "power_watt": 900,
                    "duration_of_use_hour": 43800,
                    "geography": "Switzerland"
                }
            }
        },
        {
            'name': 'Blade Server',
            'resilio_endpoint': 'blade_server',
            'description': 'High-density compute server designed for blade enclosures',
            'default_payload': {
                "usage_percent": 1,
                "wanted_name": "blade_server",
                "cpus": [{"name": "intel Intel Core i5", "die_surface_mm2": 126, "litho_nm": 14}],
                "rams": [{"size_gb": 8}, {"size_gb": 8}],
                "ssd_disks": [{"size_gb": 564, "technology": "TLC", "casing": "casing_M2"}],
                "hdd_disks": {"quantity": 1},
                "dedicated_graphics_cards": [{"die_surface_mm2": 200, "litho_nm": 22}],
                "usage": {"power_watt": 400, "duration_of_use_hour": 43800, "geography": "Switzerland"}
            }
        },
        {
            'name': 'Rack Server',
            'resilio_endpoint': 'rack_server',
            'description': 'Standard rack-mountable server',
            'default_payload': {
                "usage_percent": 1,
                "wanted_name": "rack_server",
                "rack_unit": 1,
                "cpus": [{"name": "intel Intel Core i5", "die_surface_mm2": 126, "litho_nm": 14}],
                "rams": [{"size_gb": 8}, {"size_gb": 8}],
                "ssd_disks": [{"size_gb": 564, "technology": "TLC", "casing": "casing_M2"}],
                "hdd_disks": {"quantity": 1},
                "dedicated_graphics_cards": [{"die_surface_mm2": 200, "litho_nm": 22}],
                "usage": {"power_watt": 400, "duration_of_use_hour": 43800, "geography": "Switzerland"}
            }
        },
        {
            'name': 'Tower Server',
            'resilio_endpoint': 'tower_server',
            'description': 'Standalone server in tower form factor',
            'default_payload': {
                "usage_percent": 1,
                "wanted_name": "tower_server",
                "cpus": [{"name": "intel Intel Core i5", "die_surface_mm2": 126, "litho_nm": 14}],
                "rams": [{"size_gb": 8}, {"size_gb": 8}],
                "ssd_disks": [{"size_gb": 564, "technology": "TLC", "casing": "casing_M2"}],
                "hdd_disks": {"quantity": 1},
                "dedicated_graphics_cards": [{"die_surface_mm2": 200, "litho_nm": 22}],
                "power_supplies": [{"power_watt": 100}],
                "usage": {"power_watt": 200, "duration_of_use_hour": 43800, "geography": "Switzerland"}
            }
        },
        {
            'name': 'Network Switch/Router',
            'resilio_endpoint': 'rack_switch_router',
            'description': 'Network switching and routing equipment',
            'default_payload': {
                "wanted_name": "switch",
                "port_number": 42,
                "rack_unit": 1,
                "usage": {"duration_of_use_hour": 43800, "geography": "Switzerland"}
            }
        },
        {
            'name': 'Laptop',
            'resilio_endpoint': 'laptop',
            'description': 'Portable computer system',
            'default_payload': {
                "name": "Lenovo IdeaPad 130-15",
                "usage_percent": 1,
                "wanted_name": "Lenovo 130-15",
                "cpus": [{"name": "intel Intel Core i5", "die_surface_mm2": 126, "litho_nm": 14}],
                "rams": [{"size_gb": 8}],
                "ssd_disks": [{"size_gb": 564, "technology": "TLC", "casing": "casing_M2"}],
                "integrated_graphics_cards": [{"die_surface_mm2": 200, "litho_nm": 22}],
                "screen_type": "LCD",
                "screen_size": 14.5,
                "usage": {"power_watt": 30, "geography": "Switzerland", "duration_of_use_hour": 43800}
            }
        },
        {
            'name': 'Storage System',
            'resilio_endpoint': 'storage_system',
            'description': 'Dedicated storage array or system',
            'default_payload': {
                "usage_percent": 1,
                "wanted_name": "storageSystem",
                "ssd_disks": [{"size_gb": 564, "technology": "TLC", "casing": "casing_M2"}],
                "hdd_disks": {"quantity": 1},
                "usage": {"power_watt": 900, "duration_of_use_hour": 43800, "geography": "Switzerland"}
            }
        },
        {
            'name': 'Computer Monitor',
            'resilio_endpoint': 'computer_monitor',
            'description': 'Display device for computers',
            'default_payload': {
                "usage_percent": 1,
                "wanted_name": "computerMonitor",
                "screen_size": 24,
                "screen_format": "16/9",
                "screen_type": "LCD",
                "usage": {"power_watt": 50, "duration_of_use_hour": 43800, "geography": "Switzerland"}
            }
        },
        {
            'name': 'Television',
            'resilio_endpoint': 'television',
            'description': 'Display device for video content',
            'default_payload': {
                "usage_percent": 1,
                "wanted_name": "television",
                "screen_size": 24,
                "screen_format": "16/9",
                "screen_type": "LCD",
                "usage": {"power_watt": 50, "duration_of_use_hour": 43800, "geography": "Switzerland"}
            }
        },
        {
            'name': 'Desktop Computer',
            'resilio_endpoint': 'desktop',
            'description': 'Standard desktop workstation',
            'default_payload': {
                "usage_percent": 1,
                "wanted_name": "desktop",
                "cpus": [{"name": "intel Intel Core i5", "die_surface_mm2": 126, "litho_nm": 14}],
                "rams": [{"size_gb": 8}, {"size_gb": 8}],
                "ssd_disks": [{"size_gb": 564, "technology": "TLC", "casing": "casing_M2"}],
                "hdd_disks": {"quantity": 1},
                "dedicated_graphics_cards": [{"die_surface_mm2": 200, "litho_nm": 22}],
                "usage": {"power_watt": 77, "duration_of_use_hour": 43800, "geography": "Switzerland"}
            }
        },
        {
            'name': 'Smartphone',
            'resilio_endpoint': 'smartphone',
            'description': 'Mobile phone device',
            'default_payload': {
                "wanted_name": "smartphone",
                "screen_size": 6,
                "cpu": {"die_surface_mm2": 101.66, "litho_nm": 8},
                "ram": {"size_gb": 7},
                "caseless_ssd_disk": {"size_gb": 160},
                "usage": {"power_watt": 5, "duration_of_use_hour": 43800, "geography": "Switzerland"}
            }
        },
        {
            'name': 'Tablet',
            'resilio_endpoint': 'tablet',
            'description': 'Tablet computing device',
            'default_payload': {
                "name": "Samsung Galaxy Tab A8",
                "usage": {"power_watt": 5, "geography": "Switzerland", "duration_of_use_hour": 43800}
            }
        },
    ]

    for type_data in default_types:
        LCAType.objects.create(**type_data)

def reverse_default_lca_types(apps, schema_editor):
    LCAType = apps.get_model('netbox_resiliodb', 'LCAType')
    LCAType.objects.all().delete()

class Migration(migrations.Migration):
    dependencies = [
        ('netbox_resiliodb', '0002_create_default_settings'),
    ]

    operations = [
        migrations.RunPython(
            create_default_lca_types,
            reverse_default_lca_types
        )
    ]
