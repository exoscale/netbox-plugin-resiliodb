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
        if value:
            return queryset.filter(lcaparams__isnull=False)
        return queryset.filter(lcaparams__isnull=True)
