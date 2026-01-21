import os
import logging
import json
from utils.hosting import HostingConfig, CPanelClient, WordPressManager, MaintenanceManager

class HostingBridge:
    def __init__(self):
        self.logger = logging.getLogger("hosting_bridge")
        self.config = HostingConfig()
        self.client = CPanelClient(self.config)
        self.wp_manager = WordPressManager(self.client)
        self.maintenance = MaintenanceManager(self.client)

    def get_hosting_status(self):
        """Fetches general hosting status (domains, storage)."""
        try:
            self.config.validate()
            # Construct a status summary like the CLI did
            domains = self.client.list_domains()
            quota = self.client.get_disk_usage()
            
            output = "Domains:\n"
            for d in domains:
                output += f"- {d.get('domain')} ({d.get('docroot')})\n"
            
            output += "\nStorage Info:\n"
            for q in quota:
                output += f"- {q.get('megabytes_used')}MB / {q.get('megabytes_limit')}MB\n"
            
            return {
                "status": "success", 
                "output": output,
                "domains": domains,
                "quota": quota
            }
        except Exception as e:
            self.logger.error(f"Failed to get hosting status: {e}")
            return {"status": "error", "error": str(e)}

    def list_wordpress_sites(self):
        """Lists WordPress installations."""
        try:
            self.config.validate()
            sites = self.wp_manager.list_sites()
            output = "WordPress Sites:\n"
            if not sites:
                output += "No WordPress sites found (or WP Toolkit not active)."
            for s in sites:
                output += f"- {s.get('domain')} ({s.get('path')})\n"
            return {
                "status": "success", 
                "output": output,
                "sites": sites
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def publish_to_wordpress(self, title, content, site_url=None):
        """
        Publishes content to a WordPress site.
        It first looks for a valid application password, then uses the REST API.
        """
        from agents.wordpress import WordPressAgent
        from database import get_platform_credentials
        import asyncio

        self.logger.info(f"Bridge: Publishing to WordPress: {title}")
        creds = get_platform_credentials('wordpress')
        
        if not creds:
            return {"status": "error", "error": "No WordPress credentials found in DB."}

        agent = WordPressAgent()
        meta = creds.get('meta_json', {})
        if isinstance(meta, str):
            try: meta = json.loads(meta)
            except: meta = {}
            
        url = meta.get('url') or "https://lev3.com"
        user = creds.get('username')
        pwd = creds.get('password')

        if not all([url, user, pwd]):
             return {"status": "error", "error": f"Incomplete WordPress credentials: {url}, {user}"}

        try:
             try:
                 loop = asyncio.get_event_loop()
             except RuntimeError:
                 loop = asyncio.new_event_loop()
                 asyncio.set_event_loop(loop)
             
             data = {"title": title, "content": content, "status": "publish"}
             res = loop.run_until_complete(agent.manage_content(url, user, pwd, "create_post", data))
             
             if "id" in res:
                 return {"status": "success", "url": res.get('link')}
             else:
                 return {"status": "error", "error": str(res)}
        except Exception as e:
             return {"status": "error", "error": str(e)}

hosting_bridge = HostingBridge()
