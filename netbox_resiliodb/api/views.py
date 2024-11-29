from netbox.api.viewsets import NetBoxModelViewSet
from rest_framework.decorators import action
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .. import models
from dcim.models import Device
from .serializers import (
    LCATypeSerializer,
    IndicatorSerializer,
    DeviceRoleLCATypeMappingSerializer,
    SiteCountryMappingSerializer,
    LCAParamsSerializer,
    PluginSettingsSerializer,
    DeviceSyncSerializer,
    LCAImpactDataSerializer,
    PoolMappingSerializer
)
from ..jobs import ResilioSyncJob

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
        from ..jobs import ResilioSyncJob
        running_jobs = ResilioSyncJob.get_jobs().filter(
            status__in=['running', 'pending']
        )
        print(running_jobs)
        ResilioSyncJob.cleanup_stale_jobs()
        running_jobs = ResilioSyncJob.get_jobs().filter(
            status__in=['running', 'pending']
        )
        print(running_jobs)
        return Response({"status": "success", "message": "Stale jobs cleaned up"})

from dcim.models import Device

class LCAImpactDataViewSet(NetBoxModelViewSet):
    queryset = models.LCAImpactData.objects.all()
    serializer_class = LCAParamsSerializer

    @action(detail=False, methods=['get'])
    def by_device(self, request):
        device_id = request.query_params.get('device_id')
        if not device_id:
            return Response(
                {"error": "device_id parameter is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        impact_data = get_object_or_404(models.LCAImpactData, device_id=device_id)
        serializer = LCAImpactDataSerializer(impact_data)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def inventory_export(self, request):
        from django.http import HttpResponse
        import csv
        from io import StringIO
        from ..filtersets import DeviceResilioFilterSet
        from dcim.models import Device
        from ..utils.lca_params import get_device_params
        from ..models import PluginSettings

        # Get devices based on selection or filters
        queryset = Device.objects.all()
        
        if request.query_params.get('select_all') == 'true':
            filters = {}
            filter_params = ['site', 'site_id', 'role', 'role_id', 'region', 'region_id']
            for param in filter_params:
                if request.query_params.get(param):
                    filters[param] = request.query_params.get(param)
            
            if filters:
                filterset = DeviceResilioFilterSet(filters, queryset)
                queryset = filterset.qs
        else:
            selected_devices = request.query_params.getlist('selected_devices[]')
            if not selected_devices:
                return Response(
                    {"error": "No devices selected"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            queryset = queryset.filter(pk__in=selected_devices)

        # Create CSV content
        output = StringIO()
        writer = csv.writer(output)
        
        # Write header
        header = ['id', 'pool_id', 'dc_id', 'power', 'lifespan', 'hdd_quantity', 
                 'hdd_unit_size', 'ssd_quantity', 'ssd_unit_size', 'ram_quantity', 
                 'ram_unit_size', 'gpu_quantity', 'gpu_model_name', 'fan_quantity', 
                 'psu_total_weight', 'load_rate', 'comment', 'quantity']
        writer.writerow(header)

        # Get default settings
        settings = PluginSettings.objects.first()
        default_power = settings.default_power_watts if settings else 100
        default_lifespan = (settings.default_usage_period_hours / (24 * 365)) if settings else 5

        # Write data for each device
        for device in queryset:
            device_params = get_device_params(device)
            params = device_params['params'] if device_params else {}
            
            # Get power and lifespan from usage parameters or defaults
            usage = params.get('usage', {})
            power = usage.get('power_watt', default_power)
            lifespan = usage.get('duration_of_use_hour', settings.default_usage_period_hours if settings else 43800)
            lifespan = lifespan / (24 * 365)  # Convert hours to years

            row = [
                device.name,  # id
                device.get_pool(),  # pool_id
                device.site.name if device.site else 'dc-generic-glo',  # dc_id
                power,  # power
                lifespan,  # lifespan
                '', '', '', '', '', '', '', '', '', '', '', '', 1  # Other fields + quantity
            ]
            writer.writerow(row)

        # Create the HTTP response with CSV content
        from datetime import datetime
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        response = HttpResponse(output.getvalue(), content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="devices_inventory_{timestamp}.csv"'
        return response

    @action(detail=False, methods=['get'])
    def csv_export(self, request):
        from django.http import HttpResponse
        import csv
        from io import StringIO
        from ..filtersets import DeviceResilioFilterSet
        from dcim.models import Device

        # Get devices based on selection or filters
        queryset = Device.objects.all()
        
        if request.query_params.get('select_all') == 'true':
            # Apply filters when select_all is true
            filters = {}
            filter_params = ['site', 'site_id', 'role', 'role_id', 'region', 'region_id', 'lca_impact_status']
            for param in filter_params:
                if request.query_params.get(param):
                    filters[param] = request.query_params.get(param)
            
            if filters:
                filterset = DeviceResilioFilterSet(filters, queryset)
                queryset = filterset.qs
        else:
            # Use selected devices
            selected_devices = request.query_params.getlist('selected_devices[]')
            if not selected_devices:
                return Response(
                    {"error": "No devices selected"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            queryset = queryset.filter(pk__in=selected_devices)

        # Get all impact data for filtered devices
        impact_data_list = models.LCAImpactData.objects.filter(
            device__in=queryset
        ).select_related('device').prefetch_related('indicator_values__indicator')

        if not impact_data_list:
            return Response(
                {"error": "No impact data found for the given filters"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Create CSV content
        output = StringIO()
        writer = csv.writer(output)
        
        # Write header
        header = ['hw_id', 'site', 'role', 'lc_step', 'ADPe', 'ADPf', 'AP', 'CTUe', 'CTUh_c', 'CTUh_nc', 
                 'Epf', 'Epm', 'Ept', 'GWP', 'GWPf', 'GWPlu', 'IR', 'LU', 'ODP', 'PM', 
                 'POCP', 'WU', 'TPE', 'GWPb']
        writer.writerow(header)
        
        # Define lifecycle steps
        steps = ['BLD', 'DIS', 'USE', 'EOL']
        step_names = {
            'BLD': 'manufacturing',
            'DIS': 'distribution',
            'USE': 'use',
            'EOL': 'end_of_life'
        }
        
        # Write data for each device and lifecycle step
        for impact_data in impact_data_list:
            device = impact_data.device
            indicator_values = impact_data.indicator_values.all()
            
            for step in steps:
                row_data = [
                    device.name,
                    device.site.name if device.site else '',
                    device.role.name if device.role else '',
                    step_names[step]
                ]
                # Add values for each indicator in order of header
                for indicator_code in header[4:]:  # Skip hw_id, site, role, and lc_step
                    value = 0
                    indicator_value = indicator_values.filter(indicator__code=indicator_code).first()
                    if indicator_value:
                        value = getattr(indicator_value, step, 0) or 0
                    row_data.append(str(value))
                writer.writerow(row_data)

        # Create the HTTP response with CSV content
        from datetime import datetime
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        response = HttpResponse(output.getvalue(), content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="devices_impact_{timestamp}.csv"'
        return response

class PoolMappingViewSet(NetBoxModelViewSet):
    queryset = models.PoolMapping.objects.all()
    serializer_class = PoolMappingSerializer

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
        running_jobs = ResilioSyncJob.get_jobs().filter(
            status__in=['running']
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
            job = ResilioSyncJob.enqueue_once(instance=device)
            with open('/tmp/netbox_api_debug.log', 'a') as f:
                f.write(f"Enqueued job for device {device.name}: {job}\n")
                f.flush()
        elif select_all:
            # All devices (with filters) from list view
            from ..filtersets import DeviceResilioFilterSet
            queryset = Device.objects.all()
            filterset = DeviceResilioFilterSet(filters, queryset)
            filtered_devices = filterset.qs
            # Enqueue each filtered device
            for device in filtered_devices:
                job = ResilioSyncJob.enqueue_once(instance=device)
                with open('/tmp/netbox_api_debug.log', 'a') as f:
                    f.write(f"Enqueued job for device {device.name}: {job}\n")
                    f.flush()
        elif selected_devices:
            # Selected devices from list view
            for device_id in selected_devices:
                device = Device.objects.get(id=device_id)
                job = ResilioSyncJob.enqueue_once(instance=device)
                with open('/tmp/netbox_api_debug.log', 'a') as f:
                    f.write(f"Enqueued job for device {device.name}: {job}\n")
                    f.flush()

        return Response({"status": "started"})

    @action(detail=False, methods=['get'])
    def status(self, request):
        # Check only for actually running jobs
        running_jobs = ResilioSyncJob.get_jobs().filter(
            status__in=['running']
        )
        return Response({
            "status": "running" if running_jobs else "idle"
        })
