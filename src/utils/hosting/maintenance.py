from .client import CPanelClient

class MaintenanceManager:
    def __init__(self, client: CPanelClient):
        self.client = client

    def check_disk_usage(self, threshold_percent=80):
        """Checks if any filesystem is above the threshold."""
        quotas = self.client.get_disk_usage()
        alerts = []
        if not quotas:
            return alerts
            
        for q in quotas:
            limit = int(q.get('megabytes_limit', 0))
            used = int(q.get('megabytes_used', 0))
            if limit > 0:
                percent = (used / limit) * 100
                if percent >= threshold_percent:
                    alerts.append(f"Storage alert: {used}MB/{limit}MB ({percent:.1f}%) used.")
        return alerts

    def trigger_full_backup(self, dest_type="homedir"):
        """
        Triggers a full account backup.
        """
        # Note: Backup logic can be specialized based on provider
        return self.client.call_uapi("Backup", "fullbackup_to_homedir")
