from .client import CPanelClient

class WordPressManager:
    def __init__(self, client: CPanelClient):
        self.client = client

    def list_sites(self):
        """Returns a list of WP sites managed by WPToolkit."""
        return self.client.list_wp_instances()

    def update_site(self, instance_id):
        """Updates a specific WP site."""
        return self.client.call_uapi("WPToolkit", "update", instance_id=instance_id)

    def backup_site(self, instance_id):
        """Creates a backup for a specific WP site."""
        return self.client.call_uapi("WPToolkit", "backup", instance_id=instance_id)

    def scan_security(self, instance_id):
        """Runs a security scan."""
        return self.client.call_uapi("WPToolkit", "scan", instance_id=instance_id)
