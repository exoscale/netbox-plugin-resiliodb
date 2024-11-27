from netbox.filtersets import NetBoxModelFilterSet
from dcim.models import Device, DeviceType
import django_filters
from .forms import DeviceResilioFilterForm

from django.contrib.contenttypes.models import ContentType
from .models import LCAParams

class DeviceResilioFilterSet(NetBoxModelFilterSet):
    has_lca_params = django_filters.BooleanFilter(
        method='filter_has_lca_params',
        label='Has LCA Parameters'
    )

    device_type_has_lca_params = django_filters.BooleanFilter(
        method='filter_device_type_has_lca_params',
        label='Device Type Has LCA Parameters'
    )

    lca_impact_status = django_filters.ChoiceFilter(
        method='filter_lca_impact_status',
        label='LCA Impact Data Status',
        choices=(
            ('yes', 'Current'),
            ('no', 'Missing'),
            ('outdated', 'Outdated')
        )
    )

    class Meta:
        model = Device
        fields = ['site', 'site_id', 'role', 'role_id']
        if hasattr(Device, 'region'):
            fields.extend(['region', 'region_id'])

    def filter_has_lca_params(self, queryset, name, value):
        content_type = ContentType.objects.get_for_model(Device)
        device_ids_with_params = LCAParams.objects.filter(
            content_type=content_type
        ).values_list('object_id', flat=True)

        if value:
            return queryset.filter(id__in=device_ids_with_params)
        return queryset.exclude(id__in=device_ids_with_params)

    def filter_device_type_has_lca_params(self, queryset, name, value):
        content_type = ContentType.objects.get_for_model(DeviceType)
        devicetype_ids_with_params = LCAParams.objects.filter(
            content_type=content_type
        ).values_list('object_id', flat=True)

        if value:
            return queryset.filter(device_type_id__in=devicetype_ids_with_params)
        return queryset.exclude(device_type_id__in=devicetype_ids_with_params)

    def filter_lca_impact_status(self, queryset, name, value):
        if value == 'no':
            return queryset.filter(lca_impact_data__isnull=True)
        elif value == 'yes':
            return queryset.filter(lca_impact_data__isnull=False).exclude(
                pk__in=[d.pk for d in queryset if d.get_lca_impact_status() is False]
            )
        elif value == 'outdated':
            return queryset.filter(lca_impact_data__isnull=False).filter(
                pk__in=[d.pk for d in queryset if d.get_lca_impact_status() is False]
            )
        return queryset
