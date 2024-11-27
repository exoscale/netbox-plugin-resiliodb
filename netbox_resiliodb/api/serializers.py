from rest_framework import serializers

from netbox.api.serializers import NetBoxModelSerializer, WritableNestedSerializer
from dcim.api.nested_serializers import NestedDeviceRoleSerializer, NestedSiteSerializer, NestedRegionSerializer, NestedDeviceSerializer
from .. import models
from dcim.models import ModuleType, Device

class LCATypeSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='plugins-api:netbox_resiliodb-api:lcatype-detail'
    )

    class Meta:
        model = models.LCAType
        fields = ('id', 'url', 'name', 'resilio_endpoint', 'description', 'default_payload', 'created', 'last_updated')

class IndicatorSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='plugins-api:netbox_resiliodb-api:indicator-detail'
    )

    class Meta:
        model = models.Indicator
        fields = ('id', 'url', 'code', 'name', 'unit', 'description', 'created', 'last_updated')

class DeviceRoleLCATypeMappingSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='plugins-api:netbox_resiliodb-api:devicerolelcatypemapping-detail'
    )
    device_role = NestedDeviceRoleSerializer()
    lca_type = LCATypeSerializer()

    class Meta:
        model = models.DeviceRoleLCATypeMapping
        fields = ('id', 'url', 'device_role', 'lca_type', 'created', 'last_updated')

class SiteCountryMappingSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='plugins-api:netbox_resiliodb-api:sitecountrymapping-detail'
    )
    site = NestedSiteSerializer(required=False)
    region = NestedRegionSerializer(required=False)

    class Meta:
        model = models.SiteCountryMapping
        fields = ('id', 'url', 'site', 'region', 'country', 'created', 'last_updated')

class LCAParamsSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='plugins-api:netbox_resiliodb-api:lcaparams-detail'
    )

    class Meta:
        model = models.LCAParams
        fields = ('id', 'url', 'content_type', 'object_id', 'parameters', 'created', 'last_updated')

class PluginSettingsSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='plugins-api:netbox_resiliodb-api:pluginsettings-detail'
    )

    class Meta:
        model = models.PluginSettings
        fields = ('id', 'url', 'api_url', 'api_key', 'api_version', 'default_usage_period_hours',
                 'default_power_watts', 'resync_on_api_version_change', 'created', 'last_updated')

class LCAImpactDataSerializer(NetBoxModelSerializer):
    device = NestedDeviceSerializer()
    cache_payload = serializers.SerializerMethodField()

    class Meta:
        model = models.LCAImpactData
        fields = ('id', 'device', 'calculated_at', 'cache_payload')

    def get_cache_payload(self, obj):
        if obj.cache_entry:
            return obj.cache_entry.request_payload
        return None

class DeviceSyncSerializer(NetBoxModelSerializer):
    device_id = serializers.IntegerField(required=False)

    class Meta:
        model = Device
        fields = ('device_id',)
