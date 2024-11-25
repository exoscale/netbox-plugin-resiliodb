from netbox.jobs import JobRunner

class ResilioBulkSyncJob(JobRunner):
    class Meta:
        name = "ResilioDB Sync"
        description = "Synchronize device data with ResilioDB"

    @classmethod
    def cleanup_stale_jobs(cls):
        from django.utils import timezone
        from datetime import timedelta
        stale_jobs = cls.get_jobs().filter(
            status__in=['running', 'pending'],
            created__lt=timezone.now() - timedelta(hours=1)  # Jobs older than 1 hour
        )
        stale_jobs.update(status='failed', completed=timezone.now())

    def run(self, *args, **kwargs):
        # Clean up stale jobs before starting new one
        self.cleanup_stale_jobs()
        device = self.job.object

        if device:
            self.log_info(f"Starting ResilioDB sync for device {device.name}...")
            # Simulate single device sync
            import time
            time.sleep(2)
            self.log_success(f"ResilioDB sync completed for device {device.name}")
        else:
            self.log_info("Starting bulk ResilioDB sync...")
            # Simulate bulk sync
            import time
            time.sleep(5)
            self.log_success("Bulk ResilioDB sync completed")
