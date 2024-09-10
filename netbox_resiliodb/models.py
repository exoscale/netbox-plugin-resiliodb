from django.db import models
from django.urls import reverse

from netbox.models import NetBoxModel
from utilities.choices import ChoiceSet
from dcim.models import DeviceType, ModuleType

class LCAData(NetBoxModel):
    device_type = models.OneToOneField(
        to=DeviceType,
        on_delete=models.CASCADE,
        related_name='lca_data',
        blank=True,
        null=True
    )
    module_type = models.OneToOneField(
        to=ModuleType,
        on_delete=models.CASCADE,
        related_name='lca_data',
        blank=True,
        null=True
    )
    lca_type = models.CharField(max_length=100)
    lca_spec = models.JSONField(blank=True, null=True)
    lca_pool = models.CharField(max_length=100, blank=True)
    lca_footprint = models.JSONField(blank=True, null=True)

    class Meta:
        verbose_name = "LCA Data"
        verbose_name_plural = "LCA Data"

    def __str__(self):
        return f"LCA Data for {self.device_type or self.module_type}"

    def get_absolute_url(self):
        return reverse('plugins:netbox_resiliodb:lcadata', args=[self.pk])
