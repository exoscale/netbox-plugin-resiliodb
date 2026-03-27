from dcim.models import Device
from django.shortcuts import get_object_or_404
from netbox.api.viewsets import NetBoxModelViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
import csv
from io import StringIO

from django.http import HttpResponse

from ..filtersets import DeviceResilioFilterSet
from ..models import PluginSettings
from ..utils.lca_params import get_device_params


from .. import models
from ..jobs import ResilioSyncJob
from .serializers import (
    DeviceRoleLCATypeMappingSerializer,
    DeviceSyncSerializer,
    IndicatorSerializer,
    LCAImpactDataSerializer,
    LCAImpactIndicatorValueSerializer,
    LCAParamsSerializer,
    LCATypeSerializer,
    PluginSettingsSerializer,
    SiteCountryMappingSerializer,
)


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

    @action(detail=False, methods=["post"], url_path="cleanup-jobs")
    def cleanup_jobs(self, request):
        from ..jobs import ResilioSyncJob

        running_jobs = ResilioSyncJob.get_jobs().filter(
            status__in=["running", "pending"]
        )
        print(running_jobs)
        ResilioSyncJob.cleanup_stale_jobs()
        running_jobs = ResilioSyncJob.get_jobs().filter(
            status__in=["running", "pending"]
        )
        print(running_jobs)
        return Response({"status": "success", "message": "Stale jobs cleaned up"})


class LCAImpactIndicatorValueViewSet(NetBoxModelViewSet):
    queryset = models.LCAImpactIndicatorValue.objects.all()
    serializer_class = LCAImpactIndicatorValueSerializer


class LCAImpactDataViewSet(NetBoxModelViewSet):
    queryset = models.LCAImpactData.objects.all()
    serializer_class = LCAImpactDataSerializer

    @action(detail=False, methods=["get"])
    def by_device(self, request):
        device_id = request.query_params.get("device_id")
        if not device_id:
            return Response(
                {"error": "device_id parameter is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        impact_data = get_object_or_404(models.LCAImpactData, device_id=device_id)
        serializer = LCAImpactDataSerializer(impact_data)
        return Response(serializer.data)


class DeviceSyncViewSet(NetBoxModelViewSet):
    queryset = Device.objects.all()
    serializer_class = DeviceSyncSerializer

    @action(detail=False, methods=["post"])
    def sync(self, request):
        device_id = request.data.get("device_id")
        selected_devices = request.data.get("selected_devices", [])
        select_all = request.data.get("select_all", False)
        filters = request.data.get("filters", {})

        # Check for running jobs with status "running" or "pending"
        running_jobs = ResilioSyncJob.get_jobs().filter(status__in=["running"])

        if running_jobs:
            return Response({"status": "running"}, status=status.HTTP_409_CONFLICT)

        # Start new sync job based on context
        if device_id:
            # Single device from detail view
            device = Device.objects.get(id=device_id)
            ResilioSyncJob.enqueue(device_id=device.id)
        elif select_all:
            # All devices (with filters) from list view
            from ..filtersets import DeviceResilioFilterSet

            queryset = Device.objects.all()
            filterset = DeviceResilioFilterSet(filters, queryset)
            filtered_devices = filterset.qs
            for device in filtered_devices:
                ResilioSyncJob.enqueue(device_id=device.id)
        elif selected_devices:
            # Selected devices from list view
            for did in selected_devices:
                ResilioSyncJob.enqueue(device_id=did)

        return Response({"status": "started"})

    @action(detail=False, methods=["get"])
    def status(self, request):
        # Check only for actually running jobs
        running_jobs = ResilioSyncJob.get_jobs().filter(status__in=["running"])
        return Response({"status": "running" if running_jobs else "idle"})
