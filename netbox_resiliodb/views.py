from django.db.models import Count

from netbox.views import generic
from dcim.models import DeviceType, ModuleType
from .models import LCAData
from .tables import LCADataTable

class LCAListView(generic.ObjectListView):
    queryset = LCAData.objects.all()
    filterset = None  # We'll add a filterset later
    table = LCADataTable
    template_name = 'netbox_resiliodb/lca_list.html'

    def get_queryset(self, request):
        return LCAData.objects.select_related('device_type', 'module_type').all()

    def get_extra_context(self, request):
        return {
            'device_types': DeviceType.objects.all(),
            'module_types': ModuleType.objects.all(),
        }
