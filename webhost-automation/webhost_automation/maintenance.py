from .client import CPanelClient

class MaintenanceManager:
    def __init__(self, client: CPanelClient):
        self.client = client

    def check_disk_usage(self, threshold_percent=80):
        """Checks if any filesystem is above the threshold."""
        quotas = self.client.get_disk_usage()
        # Parse quota info (structure varies, usually list of hashes)
        alerts = []
        if not quotas:
            return alerts
            
        # Example structure handling
        # Note: UAPI Quota::get_quota_info returns detailed bytes used/limit
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
        dest_type: homedir, ftp, scp, etc.
        """
        # Backup::fullbackup_to_homedir is a UAPI 2 (cPanel API 2) call, 
        # but UAPI (API 3) usually preferred. 
        # Check Backup::fullbackup_to_homedir availability in UAPI.
        # If not, we might need a wrapper or older API call. UAPI 'Backup' module exists.
        return self.client.call_uapi("Backup", "fullbackup_to_homedir")
