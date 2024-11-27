import logging
from django.db import models
from django.urls import reverse
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

from netbox.models import NetBoxModel
from utilities.choices import ChoiceSet
from dcim.models import DeviceType, ModuleType, DeviceRole, Site, Region, Device

from django.core.exceptions import ObjectDoesNotExist

logger = logging.getLogger(__name__)

class LCAType(NetBoxModel):
    """
    Represents different Life Cycle Assessment (LCA) types corresponding to ResilioDB endpoints.
    """
    name = models.CharField(max_length=100)
    resilio_endpoint = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    default_payload = models.JSONField(blank=True, null=True)

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('plugins:netbox_resiliodb:lcatype', args=[self.pk])

class Indicator(NetBoxModel):
    """
    Represents environmental impact indicators used in the assessment.
    """
    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100)
    unit = models.CharField(max_length=20)
    description = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ('code',)

    def __str__(self):
        return f'{self.code} ({self.unit})'

    def get_absolute_url(self):
        return reverse('plugins:netbox_resiliodb:indicator', args=[self.pk])

class DeviceRoleLCATypeMapping(NetBoxModel):
    """
    Maps NetBox Device Roles to LCA Types.
    """
    device_role = models.ForeignKey(DeviceRole, on_delete=models.CASCADE, related_name='lca_mappings')
    lca_type = models.ForeignKey(LCAType, on_delete=models.CASCADE)

    class Meta:
        ordering = ('device_role', 'lca_type')
        verbose_name = "Device Role LCA Type Mapping"

    def __str__(self):
        return f'{self.device_role.name} mapped to {self.lca_type.name}'

    def get_absolute_url(self):
        return reverse('plugins:netbox_resiliodb:devicerolelcatypemapping', args=[self.pk])

class SiteCountryMapping(NetBoxModel):
    """
    Maps NetBox Sites or Regions to countries for geography information.
    """
    site = models.ForeignKey(Site, on_delete=models.CASCADE, null=True, blank=True)
    region = models.ForeignKey(Region, on_delete=models.CASCADE, null=True, blank=True)
    country = models.CharField(max_length=100)

    class Meta:
        ordering = ('country',)
        constraints = [
            models.CheckConstraint(
                check=(
                    models.Q(site__isnull=False, region__isnull=True) |
                    models.Q(site__isnull=True, region__isnull=False)
                ),
                name='site_or_region_must_be_set'
            )
        ]

    def __str__(self):
        if self.site:
            return f'{self.site.name} mapped to {self.country}'
        return f'{self.region.name} mapped to {self.country}'

    def get_absolute_url(self):
        return reverse('plugins:netbox_resiliodb:sitecountrymapping', args=[self.pk])

class LCAParams(NetBoxModel):
    """
    Stores LCA parameters at the DeviceType or Device level.
    """
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    parameters = models.JSONField(blank=True, null=True)

    class Meta:
        ordering = ('content_type', 'object_id')
        constraints = [
            models.UniqueConstraint(
                fields=['content_type', 'object_id'],
                name='unique_lcaparams_per_object',
                violation_error_message="LCA Parameters already exist for this object"
            )
        ]
        verbose_name = "LCA Parameters"
        verbose_name_plural = "LCA Parameters"

    def __str__(self):
        return f'LCA Params for {self.content_object}'

    def get_absolute_url(self):
        return reverse('plugins:netbox_resiliodb:lcaparams', args=[self.pk])

class LCACache(NetBoxModel):
    """
    Caches request payloads to avoid redundant API calls.
    """
    hash = models.CharField(max_length=64, unique=True)
    request_payload = models.JSONField()

    class Meta:
        ordering = ('hash',)
        verbose_name = "LCA Cache"
        verbose_name_plural = "LCA Caches"

    def __str__(self):
        return self.hash

    def get_absolute_url(self):
        return reverse('plugins:netbox_resiliodb:lcacache', args=[self.pk])

class LCAImpactData(NetBoxModel):
    """
    Stores environmental impact data for devices.
    """
    device = models.OneToOneField(
        to=Device,
        on_delete=models.CASCADE,
        related_name='lca_impact_data'
    )
    cache_entry = models.ForeignKey(
        to=LCACache,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='impact_data'
    )

    class Meta:
        ordering = ('device',)
        verbose_name = "LCA Impact Data"
        verbose_name_plural = "LCA Impact Data"

    def __str__(self):
        return f'Impact Data for {self.device.name}'

    def get_absolute_url(self):
        return reverse('plugins:netbox_resiliodb:lcaimpactdata', args=[self.pk])

    def is_outdated(self):
        """Check if the impact data is outdated by comparing cache hashes"""
        from .utils.lca_params import get_device_params
        from .utils.resilio_client import ResilioDBClient
        import logging

        if not self.cache_entry:
            return True

        device_params = get_device_params(self.device)
        if not device_params or not device_params.get('lca_type'):
            return True

        try:
            client = ResilioDBClient()
            payload = {"assembly": False, "data": [device_params['params']]}
            current_hash = client._compute_hash(
                device_params['lca_type'],
                payload
            )
            return current_hash != self.cache_entry.hash
        except Exception as e:
            logger.error(f"Error computing hash: {str(e)}")
            raise

class LCAImpactIndicatorValue(NetBoxModel):
    """
    Stores indicator values per device, including per life cycle step.
    """
    impact_data = models.ForeignKey(LCAImpactData, on_delete=models.CASCADE, related_name='indicator_values')
    indicator = models.ForeignKey(Indicator, on_delete=models.CASCADE)
    total_value = models.FloatField()
    BLD = models.FloatField(null=True, blank=True)
    DIS = models.FloatField(null=True, blank=True)
    USE = models.FloatField(null=True, blank=True)
    EOL = models.FloatField(null=True, blank=True)

    class Meta:
        ordering = ('impact_data', 'indicator')
        verbose_name = "LCA Impact Indicator Value"
        verbose_name_plural = "LCA Impact Indicator Values"

    def __str__(self):
        return f'{self.indicator.code} for {self.impact_data.device.name}'

    def get_absolute_url(self):
        return reverse('plugins:netbox_resiliodb:lcaimpactindicatorvalue', args=[self.pk])

class PluginSettings(NetBoxModel):
    """
    Stores global settings for the plugin.
    Single instance model - only one record with id=1 is allowed.
    """
    id = models.AutoField(primary_key=True)
    api_url = models.URLField()

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if self.pk == 1:
            return  # Prevent deletion of the only instance
        super().delete(*args, **kwargs)
    api_key = models.CharField(max_length=255)
    api_version = models.CharField(max_length=20)
    default_usage_period_hours = models.FloatField(default=43800)
    default_power_watts = models.FloatField(default=100)
    resync_on_api_version_change = models.BooleanField(default=True)
    access_token = models.CharField(max_length=255, blank=True, null=True)
    access_token_expiry = models.DateTimeField(blank=True, null=True)

    class Meta:
        verbose_name = "Plugin Settings"
        verbose_name_plural = "Plugin Settings"

    def __str__(self):
        return 'ResilioDB Plugin Settings'

    def get_absolute_url(self):
        return reverse('plugins:netbox_resiliodb:pluginsettings', args=[self.pk])


# Mokey Patching Zone
#
def get_lca_type(self):
    try:
        mapping = DeviceRoleLCATypeMapping.objects.get(device_role=self.role)
        return mapping.lca_type
    except ObjectDoesNotExist:
        return None

Device.get_lca_type = get_lca_type

def has_lca_params(self):
    content_type = ContentType.objects.get_for_model(self)
    return LCAParams.objects.filter(
        content_type=content_type,
        object_id=self.pk
    ).exists()

def get_lca_impact_status(self):
    """
    Returns the status of LCA impact data
    """
    try:
        impact_data = self.lca_impact_data
        if not impact_data or not impact_data.cache_entry:
            return "Data Missing"
            
        try:
            if impact_data.is_outdated():
                return "Outdated"
        except Exception:
            return "Error"
            
        return "Current"
    except ObjectDoesNotExist:
        return "Missing"

Device.has_lca_params = has_lca_params
Device.get_lca_impact_status = get_lca_impact_status
DeviceType.has_lca_params = has_lca_params
