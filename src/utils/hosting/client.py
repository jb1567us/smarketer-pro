import requests
import urllib.parse
import logging
from .config import HostingConfig

class CPanelClient:
    def __init__(self, config: HostingConfig):
        self.config = config
        self.session = requests.Session()
        self.logger = logging.getLogger("hosting_client")
        
        # Authorization header for cPanel API Tokens
        if config.cpanel_token:
            self.session.headers.update({
                "Authorization": f"cpanel {config.cpanel_user}:{config.cpanel_token}"
            })

    def call_uapi(self, module: str, function: str, **kwargs):
        """
        Calls a cPanel UAPI function.
        """
        url = f"{self.config.cpanel_url}/execute/{module}/{function}"
        
        try:
            self.logger.debug(f"Calling UAPI: {module}/{function}")
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
        data = self.call_uapi("DomainInfo", "list_domains")
        
        if isinstance(data, dict):
            domains = []
            if "main_domain" in data and isinstance(data["main_domain"], dict):
                domains.append(data["main_domain"])
            for key in ["addon_domains", "parked_domains", "sub_domains"]:
                if key in data and isinstance(data[key], list):
                    domains.extend(data[key])
            return domains
        return data if isinstance(data, list) else []

    def get_disk_usage(self):
        """Get disk usage information."""
        data = self.call_uapi("Quota", "get_quota_info")
        if isinstance(data, list):
            return data
        if isinstance(data, dict):
            return [data]
        return []

    def list_wp_instances(self):
        """
        Attempts to list WordPress instances.
        """
        try:
            return self.call_uapi("WPToolkit", "get_instances")
        except Exception as e:
            self.logger.warning(f"WPToolkit not available or error: {e}")
            return []
