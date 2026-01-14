
import asyncio
import logging
from datetime import datetime
import os
import sys

# Add project root to path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.append(project_root)
sys.path.append(os.path.join(project_root, 'src'))

from src.agents.wordpress import WordPressAgent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/daily_health_check.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("WordPressHealthCheck")

class HealthChecker:
    def __init__(self, site_url, username, app_password):
        self.site_url = site_url.rstrip('/')
        self.username = username
        self.app_password = app_password
        self.agent = WordPressAgent()

    async def check_uptime(self):
        """Simple uptime check."""
        import requests
        try:
            response = requests.get(self.site_url, timeout=15)
            status = response.status_code
            if status == 200:
                logger.info(f"✅ Uptime: {self.site_url} is UP (200 OK)")
                return True
            else:
                logger.warning(f"⚠️ Uptime: {self.site_url} returned status {status}")
                return False
        except Exception as e:
            logger.error(f"❌ Uptime: {self.site_url} is DOWN or unreachable. Error: {str(e)}")
            return False

    async def check_minimum_viable_stack(self):
        """
        Check if the site adheres to the Minimum Viable Stack:
        1. Security (Wordfence/Limit Login)
        2. SEO (Rank Math/Yoast)
        3. Backups (UpdraftPlus)
        """
        logger.info("🔍 Auditing Plugin Stack...")
        
        result = await self.agent.manage_content(
            self.site_url, 
            self.username, 
            self.app_password, 
            "list_plugins"
        )
        
        if "error" in result:
            logger.error(f"Could not fetch plugin list: {result['error']}")
            return {"status": "UNKNOWN", "details": result['error']}
            
        # Standard WP REST API /plugins endpoint might return list of objects with 'name', 'status', 'version' 
        # (Note: Standard WP doesn't expose plugins publicly, this assumes admin auth + correct endpoint availability)
        # If result is a list, proceed.
        
        if isinstance(result, dict):
            if "error" in result:
                logger.error(f"Plugin API Error: {result['error']}")
                return {"status": "UNKNOWN", "details": result['error']}
            if "code" in result and "message" in result:
                logger.error(f"WP API Error: {result['code']} - {result['message']}")
                return {"status": "UNKNOWN", "details": f"{result['code']}: {result['message']}"}
            # Fallback debug
            logger.warning(f"Unexpected dict response structure. Keys: {list(result.keys())}")
            return {"status": "UNKNOWN", "details": "Unexpected API response format"}
            
        if not isinstance(result, list):
             logger.warning(f"Unexpected response type for plugins: {type(result)}")
             return {"status": "UNKNOWN", "details": "Invalid response type"}

        installed_plugins = [p.get('name', '').lower() for p in result]
        active_plugins = [p.get('name', '') for p in result if p.get('status') == 'active']
        
        # Define Essential Categories
        stack_check = {
            "Security": ["wordfence", "limit login attempts", "sucuri", "ithemes"],
            "SEO": ["rank math", "yoast", "seo framework", "all in one seo"],
            "Backups": ["updraftplus", "backupbuddy", "duplicator", "jetpack"]
        }
        
        missing_categories = []
        found_stack = {}
        
        for category, keywords in stack_check.items():
            found = None
            for p_name in installed_plugins:
                if any(k in p_name for k in keywords):
                    found = p_name
                    break
            
            if found:
                found_stack[category] = found
            else:
                missing_categories.append(category)

        status = "HEALTHY"
        if missing_categories:
            status = "AT_RISK"
            logger.warning(f"⚠️ Missing Essential Components: {', '.join(missing_categories)}")
        else:
            logger.info("✅ Minimum Viable Stack Verified.")
            
        return {
            "status": status,
            "found": found_stack,
            "missing": missing_categories,
            "total_plugins": len(installed_plugins)
        }

    async def run_all(self):
        logger.info(f"--- Starting Daily Health Check for {self.site_url} ---")
        
        uptime = await self.check_uptime()
        stack_audit = await self.check_minimum_viable_stack()
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "site": self.site_url,
            "uptime_ok": uptime,
            "stack_health": stack_audit,
            "status": "HEALTHY" if uptime and stack_audit['status'] == "HEALTHY" else "ATTENTION REQUIRED"
        }
        
        logger.info(f"Final Report: {report['status']}")
        return report

if __name__ == "__main__":
    # Example usage - Pulling from Env
    SITE_URL = os.getenv("WP_SITE_URL", "https://lookoverhere.xyz/dsr-test")
    USERNAME = os.getenv("WP_USER", "admin")
    APP_PASS = os.getenv("WP_APP_PASS", "OutreachAgent2026!") # Default for dev
    
    checker = HealthChecker(SITE_URL, USERNAME, APP_PASS)
    asyncio.run(checker.run_all())
