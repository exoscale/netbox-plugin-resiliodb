from netbox.api.viewsets import NetBoxModelViewSet
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

    @action(detail=False, methods=['post'])
    def cleanup_jobs(self, request):
        from ..jobs import ResilioBulkSyncJob
        ResilioBulkSyncJob.cleanup_stale_jobs()
        return Response({"status": "success", "message": "Stale jobs cleaned up"})

from dcim.models import Device

class DeviceSyncViewSet(NetBoxModelViewSet):
    queryset = Device.objects.all()
    serializer_class = DeviceSyncSerializer

    @action(detail=False, methods=['post'])
    def sync(self, request):
        device_id = request.data.get('device_id')
        # Check for running jobs with status "running" or "pending"
        running_jobs = ResilioBulkSyncJob.get_jobs().filter(
            status__in=['running', 'pending']
        )

        if running_jobs:
            return Response(
                {"status": "running"},
                status=status.HTTP_409_CONFLICT
            )

        # Start new sync job
        if device_id:
            device = Device.objects.get(id=device_id)
            ResilioBulkSyncJob.enqueue_once(instance=device)
        else:
            ResilioBulkSyncJob.enqueue_once()

        return Response({"status": "started"})

    @action(detail=False, methods=['get'])
    def status(self, request):
        # Check only for actually running jobs
        running_jobs = ResilioBulkSyncJob.get_jobs().filter(
            status__in=['running', 'pending']
        )
        return Response({
            "status": "running" if running_jobs else "idle"
        })
