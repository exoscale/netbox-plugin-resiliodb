import logging

from netbox.jobs import JobRunner

logger = logging.getLogger(__name__)

__all__ = ["ResilioSyncJob"]


class ResilioSyncJob(JobRunner):
    class Meta:
        name = "ResilioDB Sync"
        description = "Synchronize device data with ResilioDB"

    @classmethod
    def cleanup_stale_jobs(cls):

        from django.utils import timezone

        stale_jobs = cls.get_jobs().filter(
            status__in=["running", "pending"],
            # created__lt=timezone.now() - timedelta(hours=1)  # Jobs older than 1 hour
        )
        stale_jobs.update(status="failed", completed=timezone.now())

    def run(self, *args, **kwargs):
        logger.info("Starting ResilioDB sync job")
        from dcim.models import Device

        device_id = kwargs.get("device_id")
        if not device_id:
            logger.error("No device_id provided in job kwargs")
            return

        try:
            device = Device.objects.get(id=device_id)
        except Device.DoesNotExist:
            logger.error(f"Device with id {device_id} not found")
            return

        logger.info(f"Processing device: {device.name} (ID: {device.id})")
        from .models import Indicator, LCAImpactData, LCAImpactIndicatorValue
        from .utils.lca_params import get_device_params
        from .utils.resilio_client import ResilioDBClient

        # Get device parameters
        device_params = get_device_params(device)
        if not device_params:
            logger.warning(f"No LCA type mapping found for device {device.name}")
            return

        # Prepare API request payload
        payload = {"assembly": False, "data": [device_params["params"]]}

        try:
            logger.debug("Initializing ResilioDB client")
            client = ResilioDBClient()
            logger.debug(f"Device parameters: {device_params}")
            response = client.get_footprint(device_params["lca_type"], payload)
            logger.debug(f"Got response from ResilioDB: {response}")

            # Get or create impact data record and assign cache entry
            try:
                logger.info(f"Processing impact data for device {device.id}")
                # First try to get existing record
                try:
                    impact_data = LCAImpactData.objects.get(device=device)
                    logger.debug(f"Found existing impact data record: {impact_data.id}")
                except LCAImpactData.DoesNotExist:
                    logger.debug("Creating new impact data record")
                    impact_data = LCAImpactData.objects.create(
                        device=device, cache_entry=response.get("_cache_entry")
                    )
                    logger.debug(f"Created new impact data record: {impact_data.id}")

                # Update cache entry
                impact_data.cache_entry = response.get("_cache_entry")
                impact_data.save()
                logger.info("Successfully saved impact data")

            except Exception as e:
                logger.error(f"Error creating/updating impact data: {str(e)}")
                logger.error(f"Device info: id={device.id}, name={device.name}")
                logger.error(f"Response cache entry: {response.get('_cache_entry')}")
                raise

            # Process results
            results = response["_cache_entry"].request_payload["results"]
            endpoint_results = results[device_params["lca_type"]]
            logger.debug("Processing indicator values")
            # Create/update indicator values
            for indicator_code, total_value in endpoint_results["total"].items():
                logger.debug(f"Processing indicator: {indicator_code}")
                indicator = Indicator.objects.filter(code=indicator_code).first()
                if not indicator:
                    continue

                # Get lifecycle step values
                bld = endpoint_results["per_lc_step"]["BLD"].get(indicator_code)
                dis = endpoint_results["per_lc_step"]["DIS"].get(indicator_code)
                use = endpoint_results["per_lc_step"]["USE"].get(indicator_code)
                eol = endpoint_results["per_lc_step"]["EOL"].get(indicator_code)

                # Update or create indicator value
                LCAImpactIndicatorValue.objects.update_or_create(
                    impact_data=impact_data,
                    indicator=indicator,
                    defaults={
                        "total_value": total_value,
                        "BLD": bld,
                        "DIS": dis,
                        "USE": use,
                        "EOL": eol,
                    },
                )
            logger.info(
                f"Successfully processed all indicators for device {device.name}"
            )

        except Exception as e:
            logger.error(f"Error processing device {device.name}: {str(e)}")
            raise
