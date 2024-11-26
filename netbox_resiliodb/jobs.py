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

        if device:
            msg = f"Starting ResilioDB sync for device {device.name}..."
            print(msg)
            # Simulate single device sync
            time.sleep(5)
            success_msg = f"ResilioDB sync completed for device {device.name}"
            print(success_msg)
