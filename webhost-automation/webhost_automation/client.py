import requests
import urllib.parse
from .config import Config

class CPanelClient:
    def __init__(self, config: Config):
        self.config = config
        self.session = requests.Session()
        # Authorization header for cPanel API Tokens
        self.session.headers.update({
            "Authorization": f"cpanel {config.cpanel_user}:{config.cpanel_token}"
        })

    def call_uapi(self, module: str, function: str, **kwargs):
        """
        Calls a cPanel UAPI function.
        Docs: https://api.docs.cpanel.net/
        """
        # UAPI endpoint structure: https://hostname:2083/execute/Module/function
        url = f"{self.config.cpanel_url}/execute/{module}/{function}"
        
        try:
            response = self.session.get(url, params=kwargs, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            if data.get("status") == 0:
                errors = data.get("errors", ["Unknown error"])
                raise Exception(f"UAPI Execution Failed: {'; '.join(errors)}")
                
            return data.get("data")
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"Connection Error: {str(e)}")

    def list_domains(self):
        """List all domains associated with the account."""
        return self.call_uapi("DomainInfo", "list_domains")

    def get_disk_usage(self):
        """Get disk usage information."""
        # Using Email module as proxy or specific quota module might be needed depending on needs
        # FileInfo is robust.
        # But 'Quota' module is standard.
        return self.call_uapi("Quota", "get_quota_info")

    def list_wp_instances(self):
        """
        Attempts to list WordPress instances.
        Note: This relies on WP Toolkit (WPToolkit module) being available.
        """
        try:
            return self.call_uapi("WPToolkit", "get_instances")
        except Exception as e:
            print(f"Warning: WPToolkit might not be available or enabled. {e}")
            return []
