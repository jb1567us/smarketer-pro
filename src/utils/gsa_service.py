import aiohttp
import json

class GSAService:
    """
    Client for the GSAPI bridge or direct file-based integration with GSA Search Engine Ranker.
    """
    def __init__(self, bridge_url="http://127.0.0.1:9090"):
        self.bridge_url = bridge_url

    async def push_link_for_indexing(self, url, money_site=None):
        """
        Pushes a created backlink to GSA for indexing/boosting.
        Uses the gsapi endpoint if available.
        """
        endpoint = f"{self.bridge_url}/api/link/set_redirect"
        # In gsapi, the format might be /api/link/set_redirect/{project_id}/{encoded_url}
        # For simplicity, we assume a generic push endpoint or logging.
        
        payload = {
            "url": url,
            "money_site": money_site,
            "action": "boost"
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(f"{self.bridge_url}/api/boost", json=payload, timeout=5) as resp:
                    if resp.status == 200:
                        return {"status": "success", "message": "Link pushed to GSA bridge"}
                    else:
                        return {"status": "failed", "reason": f"Bridge returned HTTP {resp.status}"}
        except Exception as e:
            # Fallback: Log to a file that GSA can monitor
            return self._fallback_log_link(url)

    def _fallback_log_link(self, url):
        """Logs the link to a text file for GSA Auto-Import."""
        import os
        log_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "jobs", "gsa_import.txt")
        os.makedirs(os.path.dirname(log_path), exist_ok=True)
        with open(log_path, "a") as f:
            f.write(f"{url}\n")
        return {"status": "fallback", "message": f"Link logged to {log_path} for GSA import"}

    async def get_stats(self):
        """Fetches current GSA performance stats from the bridge."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.bridge_url}/api/stats", timeout=5) as resp:
                    if resp.status == 200:
                        return await resp.json()
        except:
            pass
        return {"status": "offline", "message": "GSA Bridge not reachable"}
