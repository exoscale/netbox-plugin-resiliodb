from netbox.filtersets import NetBoxModelFilterSet
from dcim.models import Device
import django_filters
from .forms import DeviceResilioFilterForm

class DeviceResilioFilterSet(NetBoxModelFilterSet):
    has_lca_params = django_filters.BooleanFilter(
        method='filter_has_lca_params',
        label='Has LCA Parameters'
    )

    class Meta:
        model = Device
        fields = ['site', 'site_id', 'role', 'role_id']
        if hasattr(Device, 'region'):
            fields.extend(['region', 'region_id'])

    def filter_has_lca_params(self, queryset, name, value):
        from django.contrib.contenttypes.models import ContentType
        from .models import LCAParams
        
        content_type = ContentType.objects.get_for_model(Device)
        device_ids_with_params = LCAParams.objects.filter(
            content_type=content_type
        ).values_list('object_id', flat=True)
        
        if value:
            return queryset.filter(id__in=device_ids_with_params)
        return queryset.exclude(id__in=device_ids_with_params)
