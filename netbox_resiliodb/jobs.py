from netbox.jobs import JobRunner
import time

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
        device = self.job.object
        if not device:
            return

        from .utils.lca_params import get_device_params
        from .utils.resilio_client import ResilioDBClient
        from .models import LCAImpactData, LCAImpactIndicatorValue, Indicator

        # Get device parameters
        device_params = get_device_params(device)
        if not device_params:
            self.log_warning(f"No LCA type mapping found for device {device.name}")
            return

        # Prepare API request payload
        payload = {
            "assembly": False,
            "data": [device_params['params']]
        }

        try:
            # Initialize client and make request
            client = ResilioDBClient()
            response = client.get_footprint(
                device_params['lca_type'],
                payload
            )

            # Get or create impact data record
            impact_data, _ = LCAImpactData.objects.get_or_create(device=device)
            impact_data.cache_entry = client.get_cache_entry() # TOFIX: get footprint should return the lca cache object and we should assign it to the impact data object.
            impact_data.save()

            # Process results
            results = response['results']
            endpoint_results = results[device_params['lca_type']]

            # Create/update indicator values
            for indicator_code, total_value in endpoint_results['total'].items():
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

            self.log_success(f"Successfully synced impact data for device {device.name}")

        except Exception as e:
            self.log_failure(f"Failed to sync impact data for device {device.name}: {str(e)}")
            raise
