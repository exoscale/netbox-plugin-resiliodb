from django.contrib.contenttypes.models import ContentType

from .. import models
from ..cpu_data import CPUData


def get_module_type_params(module_type):
    """Get default parameters based on module type tags"""
    if not module_type.tags.all():
        return None

    for tag in module_type.tags.all():
        tag_name = tag.name.upper()
        if tag_name == "CPU":
            # Get CPU name from module type model name
            cpu_name = module_type.model
            cpu_specs = CPUData.get_cpu_specs(cpu_name)
            return {
                "name": cpu_name,
                "litho_nm": cpu_specs["litho_nm"],
                "die_surface_mm2": cpu_specs["die_surface_mm2"],
            }
        elif tag_name == "SSD":
            # Check for casing and technology tags
            casing = "casing_M2"  # Default casing
            technology = "TLC"  # Default technology

            for tech_tag in module_type.tags.all():
                tech_name = tech_tag.name.upper()
                # Check casing tags
                if tech_name in ["M2", "2.5INCH"]:
                    casing = f"casing_{tech_name}"
                # Check technology tags
                elif tech_name in ["SLC", "MLC", "TLC", "QLC"]:
                    technology = tech_name

            return {"casing": casing, "size_gb": 1920, "technology": technology}
        elif tag_name == "RAM":
            import re

            # Look for RAM size in module type name
            size_pattern = r"(\d+)\s*GB"
            match = re.search(size_pattern, module_type.model, re.IGNORECASE)
            if match:
                size_gb = int(match.group(1))
            else:
                size_gb = 8  # Default size if not found

            return {"size_gb": size_gb}
        elif tag_name == "GPU":
            return {"die_surface_mm2": 200, "litho_nm": 22}
    return None


def get_server_components(device):
    """Aggregate server component data from device modules"""
    cpus = []
    rams = []
    ssds = []
    gpus = []
    hdd_count = 0

    for module in device.modules.all():
        if not module.module_type:
            continue

        # Get module's LCA parameters
        module_params = models.LCAParams.objects.filter(
            content_type=ContentType.objects.get_for_model(module.module_type),
            object_id=module.module_type.pk,
        ).first()

        # Check module tags and aggregate parameters
        for tag in module.module_type.tags.all():
            tag_name = tag.name.upper()
            # Use module_params if available, otherwise get default params
            params = (
                module_params.parameters
                if module_params
                else get_module_type_params(module.module_type)
            )

            if tag_name == "CPU" and params:
                cpus.append(params)
            elif tag_name == "RAM" and params:
                rams.append(params)
            elif tag_name == "SSD" and params:
                ssds.append(params)
            elif tag_name == "GPU" and params:
                gpus.append(params)
            elif tag_name == "HDD":
                hdd_count += 1

    return {
        "cpus": cpus,
        "rams": rams,
        "ssd_disks": ssds,
        "dedicated_graphics_cards": gpus,
        "hdd_disks": {"quantity": hdd_count},
    }


def update_enclosure_params(device):
    return {
        "rack_unit": int(
            device.device_type.u_height
        )  # INFO not sure about proper way to handle 0.5 height device (ie half rack)
    }


def get_device_geography(device):
    """
    Get geography for a device by traversing the location hierarchy.
    Checks device bay -> rack -> site -> region for country mapping.
    """
    # Check device's own site
    if device.site:
        # Check site mapping
        site_mapping = models.SiteCountryMapping.objects.filter(
            site=device.site
        ).first()
        if site_mapping:
            return site_mapping.country
        # Check region mapping
        if device.site.region:
            region_mapping = models.SiteCountryMapping.objects.filter(
                region=device.site.region
            ).first()
            if region_mapping:
                return region_mapping.country

    return None


def get_device_params(device):
    """Get LCA parameters and type for a device"""
    if not device.role:
        return None

    # Look for a matching LCA type for the device role
    mapping = models.DeviceRoleLCATypeMapping.objects.filter(
        device_role=device.role
    ).first()

    if not mapping or not mapping.lca_type:
        return None

    # Get device-specific LCA params if they exist
    device_params = models.LCAParams.objects.filter(
        content_type=ContentType.objects.get_for_model(device), object_id=device.pk
    ).first()

    if device_params and device_params.parameters:
        return {
            "lca_type": mapping.lca_type.resilio_endpoint,
            "params": device_params.parameters,
        }

    # Get device type LCA params if they exist
    device_type_params = None
    if device.device_type:
        device_type_params = models.LCAParams.objects.filter(
            content_type=ContentType.objects.get_for_model(device.device_type),
            object_id=device.device_type.pk,
        ).first()

    if device_type_params and device_type_params.parameters:
        return {
            "lca_type": mapping.lca_type.resilio_endpoint,
            "params": device_type_params.parameters,
        }

    # Use default payload from LCA type
    params = mapping.lca_type.default_payload or {}

    # Check if device is a server/workstation/laptop based on endpoint
    endpoint = mapping.lca_type.resilio_endpoint
    if endpoint.endswith(("_server", "workstation", "laptop")):
        params.update(get_server_components(device))
    if endpoint == "blade_enclosure":
        params.update(update_enclosure_params(device))

    # Update geography in usage parameters if found
    geography = get_device_geography(device)
    if geography and "usage" in params:
        params["usage"]["geography"] = geography

    # Override usage duration with default from settings
    if "usage" in params:
        from ..models import PluginSettings

        settings = PluginSettings.objects.first()
        if settings:
            params["usage"]["duration_of_use_hour"] = (
                settings.default_usage_period_hours
            )

    return {"lca_type": mapping.lca_type.resilio_endpoint, "params": params}


def get_device_type_params(device_type):
    """Get LCA parameters for a device type"""
    # Find first device of this type that has a role with LCA mapping
    device = device_type.instances.first()
    if not device or not device.role:
        return None

    device_params = get_device_params(device)
    return device_params["params"] if device_params else None
