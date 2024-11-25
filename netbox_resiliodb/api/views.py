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
    PluginSettingsSerializer
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

from dcim.models import Device

class DeviceSyncViewSet(NetBoxModelViewSet):
    queryset = Device.objects.all()
    serializer_class = DeviceSyncSerializer

    @action(detail=False, methods=['post'])
    def sync(self, request):
        device_id = request.data.get('device_id')
        
        # Check if a sync job is already running for this device/bulk
        job_filter = {'object_id': device_id} if device_id else {}
        running_jobs = ResilioBulkSyncJob.get_jobs(**job_filter)
        
        if running_jobs:
            return Response(
                {"message": "Sync already in progress", "job_id": running_jobs[0].id},
                status=status.HTTP_409_CONFLICT
            )
        
        # Start new sync job
        if device_id:
            device = Device.objects.get(id=device_id)
            job = ResilioBulkSyncJob.enqueue_once(instance=device)
        else:
            job = ResilioBulkSyncJob.enqueue_once()
            
        return Response({"message": "Sync started", "job_id": job.id})
