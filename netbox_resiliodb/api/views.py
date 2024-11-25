from netbox.api.viewsets import NetBoxModelViewSet
from rest_framework.decorators import action
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from .. import models
from dcim.models import Device
from .serializers import (
    LCATypeSerializer,
    IndicatorSerializer,
    DeviceRoleLCATypeMappingSerializer,
    SiteCountryMappingSerializer,
    LCAParamsSerializer,
    PluginSettingsSerializer,
    DeviceSyncSerializer
)
from ..jobs import ResilioBulkSyncJob

class LCATypeViewSet(NetBoxModelViewSet):
    queryset = models.LCAType.objects.all()
    serializer_class = LCATypeSerializer

class IndicatorViewSet(NetBoxModelViewSet):
    queryset = models.Indicator.objects.all()
    serializer_class = IndicatorSerializer

class DeviceRoleLCATypeMappingViewSet(NetBoxModelViewSet):
    queryset = models.DeviceRoleLCATypeMapping.objects.all()
    serializer_class = DeviceRoleLCATypeMappingSerializer

class SiteCountryMappingViewSet(NetBoxModelViewSet):
    queryset = models.SiteCountryMapping.objects.all()
    serializer_class = SiteCountryMappingSerializer

class LCAParamsViewSet(NetBoxModelViewSet):
    queryset = models.LCAParams.objects.all()
    serializer_class = LCAParamsSerializer

class PluginSettingsViewSet(NetBoxModelViewSet):
    queryset = models.PluginSettings.objects.all()
    serializer_class = PluginSettingsSerializer

    @action(detail=False, methods=['post'], url_path='cleanup-jobs')
    def cleanup_jobs(self, request):
        from ..jobs import ResilioBulkSyncJob
        running_jobs = ResilioBulkSyncJob.get_jobs().filter(
            status__in=['running', 'pending']
        )
        print(running_jobs)
        ResilioBulkSyncJob.cleanup_stale_jobs()
        running_jobs = ResilioBulkSyncJob.get_jobs().filter(
            status__in=['running', 'pending']
        )
        print(running_jobs)
        return Response({"status": "success", "message": "Stale jobs cleaned up"})

from dcim.models import Device

class DeviceSyncViewSet(NetBoxModelViewSet):
    queryset = Device.objects.all()
    serializer_class = DeviceSyncSerializer

    @action(detail=False, methods=['post'])
    def sync(self, request):
        device_id = request.data.get('device_id')
        selected_devices = request.data.get('selected_devices', [])
        select_all = request.data.get('select_all', False)
        filters = request.data.get('filters', {})
        
        # Check for running jobs with status "running" or "pending"
        running_jobs = ResilioBulkSyncJob.get_jobs().filter(
            status__in=['running', 'pending']
        )

        if running_jobs:
            return Response(
                {"status": "running"},
                status=status.HTTP_409_CONFLICT
            )

        # Start new sync job based on context
        if device_id:
            # Single device from detail view
            device = Device.objects.get(id=device_id)
            ResilioBulkSyncJob.enqueue_once(instance=device)
        elif selected_devices:
            # Selected devices from list view
            for device_id in selected_devices:
                device = Device.objects.get(id=device_id)
                ResilioBulkSyncJob.enqueue_once(instance=device)
        elif select_all:
            # All devices (with filters) from list view
            from ..filtersets import DeviceResilioFilterSet
            queryset = Device.objects.all()
            filterset = DeviceResilioFilterSet(filters, queryset)
            filtered_devices = filterset.qs
            
            # Enqueue each filtered device
            for device in filtered_devices:
                ResilioBulkSyncJob.enqueue_once(instance=device)

        return Response({"status": "started"})

    @action(detail=False, methods=['get'])
    def status(self, request):
        # Check only for actually running jobs
        running_jobs = ResilioBulkSyncJob.get_jobs().filter(
            status__in=['running', 'pending']
        )
        print(running_jobs)
        return Response({
            "status": "running" if running_jobs else "idle"
        })
