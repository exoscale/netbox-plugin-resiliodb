import django_tables2 as tables
from netbox.tables import NetBoxTable, columns
from dcim.models import Device
from .models import LCAType, Indicator, DeviceRoleLCATypeMapping, SiteCountryMapping, PluginSettings

class LCATypeTable(NetBoxTable):
    name = tables.Column(linkify=True)
    resilio_endpoint = tables.Column()
    
    class Meta(NetBoxTable.Meta):
        model = LCAType
        fields = ('pk', 'id', 'name', 'resilio_endpoint', 'description', 'actions')
        default_columns = ('name', 'resilio_endpoint', 'description')

class IndicatorTable(NetBoxTable):
    code = tables.Column(linkify=True)
    
    class Meta(NetBoxTable.Meta):
        model = Indicator
        fields = ('pk', 'id', 'code', 'name', 'unit', 'description', 'actions')
        default_columns = ('code', 'name', 'unit', 'description')

class DeviceRoleLCATypeMappingTable(NetBoxTable):
    device_role = tables.Column(linkify=True)
    lca_type = tables.Column(linkify=True)
    
    class Meta(NetBoxTable.Meta):
        model = DeviceRoleLCATypeMapping
        fields = ('pk', 'id', 'device_role', 'lca_type', 'actions')
        default_columns = ('device_role', 'lca_type')

class SiteCountryMappingTable(NetBoxTable):
    site = tables.Column(linkify=True)
    region = tables.Column(linkify=True)
    
    class Meta(NetBoxTable.Meta):
        model = SiteCountryMapping
        fields = ('pk', 'id', 'site', 'region', 'country', 'actions')
        default_columns = ('site', 'region', 'country')

class PluginSettingsTable(NetBoxTable):
    api_url = tables.Column(linkify=True)
    
    class Meta(NetBoxTable.Meta):
        model = PluginSettings
        fields = ('pk', 'id', 'api_url', 'api_version', 'default_usage_period_hours', 
                 'default_power_watts', 'resync_on_api_version_change', 'actions')
        default_columns = ('api_url', 'api_version', 'default_usage_period_hours', 
                         'default_power_watts')

class DeviceResilioTable(NetBoxTable):
    name = tables.Column(
        linkify=True
    )
    device_role = tables.Column(
        linkify=True
    )
    def get_resilio_type(self, record):
        mapping = DeviceRoleLCATypeMapping.objects.filter(
            device_role=record.device_role
        ).first()
        return mapping.lca_type if mapping else None

    resilio_type = tables.Column(
        accessor='device_role',
        verbose_name='Resilio Type',
        linkify=False,
        order_by='device_role__name'
    )
    site = tables.Column(
        linkify=True
    )
    def get_region(self, record):
        return record.site.region if record.site else None

    region = tables.Column(
        accessor='site__region',
        linkify=True
    )
    has_lca_params = tables.BooleanColumn()

    class Meta(NetBoxTable.Meta):
        model = Device
        fields = ('pk', 'id', 'name', 'device_role', 'resilio_type', 'site', 
                 'region', 'has_lca_params')
        default_columns = ('name', 'device_role', 'resilio_type', 'site', 
                         'region', 'has_lca_params')
