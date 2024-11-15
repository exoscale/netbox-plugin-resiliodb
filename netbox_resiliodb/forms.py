from django import forms
from netbox.forms import NetBoxModelForm
from utilities.forms.fields import DynamicModelChoiceField
from dcim.models import DeviceRole, Site, Region
from .models import LCAType, Indicator, DeviceRoleLCATypeMapping, SiteCountryMapping, PluginSettings

class LCATypeForm(NetBoxModelForm):
    class Meta:
        model = LCAType
        fields = ['name', 'resilio_endpoint', 'description', 'default_payload']
        widgets = {
            'default_payload': forms.Textarea,
        }

class IndicatorForm(NetBoxModelForm):
    class Meta:
        model = Indicator
        fields = ['code', 'name', 'unit', 'description']

class DeviceRoleLCATypeMappingForm(NetBoxModelForm):
    device_role = DynamicModelChoiceField(
        queryset=DeviceRole.objects.all()
    )
    lca_type = DynamicModelChoiceField(
        queryset=LCAType.objects.all(),
        context={
            'label': 'name',
            'description': 'description'
        }
    )

    class Meta:
        model = DeviceRoleLCATypeMapping
        fields = ['device_role', 'lca_type']

class SiteCountryMappingForm(NetBoxModelForm):
    site = DynamicModelChoiceField(
        queryset=Site.objects.all(),
        required=False
    )
    region = DynamicModelChoiceField(
        queryset=Region.objects.all(),
        required=False
    )

    class Meta:
        model = SiteCountryMapping
        fields = ['site', 'region', 'country']

class PluginSettingsForm(NetBoxModelForm):
    class Meta:
        model = PluginSettings
        fields = ['api_url', 'api_key', 'api_version', 'default_usage_period_hours',
                 'default_power_watts', 'resync_on_api_version_change']

class LCAParamsForm(NetBoxModelForm):
    class Meta:
        model = LCAParams
        fields = ['parameters']
        widgets = {
            'parameters': forms.Textarea,
        }
