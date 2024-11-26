from netbox.jobs import JobRunner
import time
import logging

logger = logging.getLogger(__name__)

__all__ = ['ResilioSyncJob']

class ResilioSyncJob(JobRunner):
    class Meta:
        name = "ResilioDB Sync"
        description = "Synchronize device data with ResilioDB"

    @classmethod
    def cleanup_stale_jobs(cls):
        from django.utils import timezone
        from datetime import timedelta
        stale_jobs = cls.get_jobs().filter(
            status__in=['running', 'pending'],
            #created__lt=timezone.now() - timedelta(hours=1)  # Jobs older than 1 hour
        )
        stale_jobs.update(status='failed', completed=timezone.now())

    def run(self, *args, **kwargs):
        print("Running ResilioSyncJob")
        device = self.job.object
        if not device:
            print("Device not found.")
            return
        print(device)
        from .utils.lca_params import get_device_params
        from .utils.resilio_client import ResilioDBClient
        from .models import LCAImpactData, LCAImpactIndicatorValue, Indicator

        # Get device parameters
        device_params = get_device_params(device)
        if not device_params:
            #self.log_warning(f"No LCA type mapping found for device {device.name}")
            print(f"No LCA type mapping found for device {device.name}")
            return

        # Prepare API request payload
        payload = {
            "assembly": False,
            "data": [device_params['params']]
        }

        try:
            print("Init Client")
            # Initialize client and make request
            client = ResilioDBClient()
            print("Client is inited")
            print(device_params)
            response = client.get_footprint(
                device_params['lca_type'],
                payload
            )
            print(response)

            # Get or create impact data record and assign cache entry
            try:
                print(f"Attempting to get/create LCAImpactData for device {device.id}")
                # First try to get existing record
                try:
                    impact_data = LCAImpactData.objects.get(device=device)
                    print(f"Found existing impact data record: {impact_data.id}")
                except LCAImpactData.DoesNotExist:
                    print("No existing record found, creating new one")
                    impact_data = LCAImpactData.objects.create(
                        device=device,
                        cache_entry=response.get('_cache_entry')
                    )
                    print(f"Created new impact data record: {impact_data.id}")
                
                # Update cache entry
                impact_data.cache_entry = response.get('_cache_entry')
                impact_data.save()
                print("Successfully saved impact data")
                
            except Exception as e:
                print(f"Error creating/updating impact data: {str(e)}")
                print(f"Device info: id={device.id}, name={device.name}")
                print(f"Response cache entry: {response.get('_cache_entry')}")
                raise

            # Process results
            results = response['results']
            endpoint_results = results[device_params['lca_type']]
            print("coucouc")
            # Create/update indicator values
            for indicator_code, total_value in endpoint_results['total'].items():
                print(indicator_code)
                indicator = Indicator.objects.filter(code=indicator_code).first()
                if not indicator:
                    continue

                # Get lifecycle step values
                bld = endpoint_results['per_lc_step']['BLD'].get(indicator_code)
                dis = endpoint_results['per_lc_step']['DIS'].get(indicator_code)
                use = endpoint_results['per_lc_step']['USE'].get(indicator_code)
                eol = endpoint_results['per_lc_step']['EOL'].get(indicator_code)

                # Update or create indicator value
                LCAImpactIndicatorValue.objects.update_or_create(
                    impact_data=impact_data,
                    indicator=indicator,
                    defaults={
                        'total_value': total_value,
                        'BLD': bld,
                        'DIS': dis,
                        'USE': use,
                        'EOL': eol
                    }
                )
            print("Success")

        except Exception as e:
            print("error")
            print(e)
            raise
