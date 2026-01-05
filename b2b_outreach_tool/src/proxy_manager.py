import aiohttp
import random
import asyncio
from config import config
import os
import subprocess
import yaml
import re
import sys
import time
import json
import argparse

class ProxyManager:
    def __init__(self):
        self.proxies = []
        self.bad_proxies = set()
        self.status_file = os.path.join(os.path.dirname(__file__), "proxy_status.json")
        self.config = config.get("proxies", {})
        self.enabled = self.config.get("enabled", False)
        self.source_url = self.config.get("source_url", "https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/http.txt")
        self.max_proxies = self.config.get("max_proxies", 50)
        self.verification_url = self.config.get("verification_url", "http://httpbin.org/ip")

    async def fetch_proxies(self, log_callback=None):
        """Fetches/Harvests proxies using the ProxyAgent."""
        if not self.enabled:
            return

        print(f"[{self.__class__.__name__}] Triggering Mass Harvest via ProxyAgent...")
        try:
            from agents.proxy_agent import ProxyAgent
            harvester = ProxyAgent()
            result = await harvester.run_mission(log_callback=log_callback)
            self.proxies = result.get("elite_proxies", [])
            print(f"[{self.__class__.__name__}] Harvest complete. {len(self.proxies)} working proxies loaded.")
        except Exception as e:
            print(f"Error harvesting proxies: {e}")
            # Fallback to simple fetch if agent fails
            await self._fallback_fetch()

    async def _fallback_fetch(self):
        print(f"Falling back to simple proxy fetch from {self.source_url}...")
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.source_url) as response:
                    if response.status == 200:
                        content = await response.text()
                        fetched = [line.strip() for line in content.splitlines() if line.strip()]
                        self.proxies = await self.verify_proxies(fetched[:self.max_proxies])
        except Exception as e:
            print(f"Fallback fetch failed: {e}")

    async def verify_proxies(self, proxy_list):
        """Verifies a list of proxies concurrently."""
        working_proxies = []
        semaphore = asyncio.Semaphore(20) # Limit concurrency

        async def check(proxy):
            async with semaphore:
                if await self.verify_proxy(proxy):
                    working_proxies.append(proxy)

        await asyncio.gather(*(check(p) for p in proxy_list))
        return working_proxies[:self.max_proxies]

    async def verify_proxy(self, proxy):
        """Checks if a proxy is working by making a request to the verification URL."""
        proxy_url = proxy if proxy.startswith("http") else f"http://{proxy}"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.verification_url, proxy=proxy_url, timeout=5) as response:
                    return response.status == 200
        except:
            return False

    def get_proxy(self):
        """Returns a random proxy from the available list."""
        if not self.enabled or not self.proxies:
            return None
        
        # If running low, we might want to trigger a background refresh in a real app
        # But for now, just return what we have
        proxy = random.choice(self.proxies)
        if not proxy.startswith("http"):
             return f"http://{proxy}"
        return proxy

    async def update_searxng_config(self):
        """Injects OR REMOVES proxies from SearXNG settings.yml based on self.enabled."""
        
        settings_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "searxng", "searxng", "settings.yml")
        docker_compose_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "searxng", "docker-compose.yaml")

        if not self.enabled:
            # We need to remove the proxies block
            print(f"[{self.__class__.__name__}] Cleaning up proxies from settings.yml (Disabled Mode)")
             # Reuse logic below but with empty list or specific removal
            pass 
        elif not self.proxies:
            print("No proxies to inject.")
            return False, "No proxies available to inject."

        settings_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "searxng", "searxng", "settings.yml")
        docker_compose_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "searxng", "docker-compose.yaml")
        
        if not os.path.exists(settings_path):
            return False, f"Settings file not found at {settings_path}"

        try:
            # 1. Read existing content
            with open(settings_path, "r", encoding="utf-8") as f:
                content = f.read()

            # 2. Format proxies for YAML
            # We want:
            # outgoing:
            #   proxies:
            #     all://:
            #       - http://ip:port
            
            proxy_list_yaml = "    all://:\n"
            if self.enabled:
                for p in self.proxies:
                    if not p.startswith("http"): p = f"http://{p}"
                    proxy_list_yaml += f"      - {p}\n"
            else:
                # If disabled, we effectively want an empty list or commented out.
                # Since SearXNG might expect a list if the key exists, let's just make the replacement string empty 
                # OR commented out.
                # But our replacement strategy below relies on finding the block.
                # Let's say we empty it.
                proxy_list_yaml = "    # Proxies disabled by user preference\n    # all://:\n"

            # 3. Regex Replacement to inject into 'outgoing' block safely-ish
            # We look for 'outgoing:' and try to find 'proxies:' inside it or append it.
            # This is tricky with regex. A simpler approach for the specific file structure:
            
            # Check if 'proxies:' already exists in 'outgoing:' section
            if "proxies:" in content and "all://:" in content:
                 # Replace existing block
                 pattern = r"(proxies:\s+all://:\s+(\s+-\s+http[s]?://.*\n?)+)"
                 replacement = f"proxies:\n{proxy_list_yaml}"
                 # This might be too aggressive if indentation differs. 
                 # Let's try a safer block replacement if we can find the exact indentation.
                 pass # Too complex to regex reliably without breaking comments.
            
            # Alternative: Load YAML, modify, Dump. BUT this destroys comments.
            # User likely wants comments preserved.
            
            # Simple Append/Replace strategy:
            # Find "outgoing:" key. 
            # Check if "proxies:" is indented under it.
            
            if "outgoing:" not in content:
                return False, "Could not find 'outgoing:' section in settings.yml"

            # We will construct a new proxies block
            new_proxies_block = "\n  proxies:\n" + proxy_list_yaml

            # Remove existing proxies block if it exists (naive removal)
            # We urge the user to have a clean file or we might duplicate.
            # Let's try to remove previous injection if we marked it? No markers.
            
            # Let's use string manipulation to find `outgoing:` and insert/replace `proxies:`
            # This is brittle but safer than full overwriting
            
            # SPLIT file by "outgoing:"
            parts = content.split("outgoing:", 1)
            pre_outgoing = parts[0] + "outgoing:"
            post_outgoing = parts[1]
            
            # Now in post_outgoing, we look for the next top-level key (no indentation) or end of file
            # to verify we are only editing the outgoing block.
            # Actually, settings.yml has deep nesting. 
            
            # LET'S JUST APPEND to the 'outgoing' section using specific known keys if possible, 
            # or just tell the user we are using a simplified approach that might duplicate if they edit manually.
            
            # BEST APPROACH FOR NOW: 
            # Just Replace the whole file content using a template isn't an option.
            # Let's try to find "proxies:" inside post_outgoing before the next top-level key.
            
            # Valid hack: explicit string replacement of a known placeholder or common config?
            # No.
            
            # Let's try `yaml` round trip for just that section? No, parser strips comments globally.
            
            # OK, we will just Append it to the end of the `outgoing:` block if it's not there,
            # or replace it if we find `proxies:`
            
            regex_proxies = r"(\s+proxies:\n\s+all://:\n(\s+-\s+.*)+)"
            
            if re.search(regex_proxies, post_outgoing, re.MULTILINE):
                 # Replace existing
                 post_outgoing = re.sub(regex_proxies, new_proxies_block, post_outgoing, count=1)
            else:
                 # Insert at start of outgoing block (safe bet)
                 post_outgoing = new_proxies_block + post_outgoing

            final_content = pre_outgoing + post_outgoing

            with open(settings_path, "w", encoding="utf-8") as f:
                f.write(final_content)

            print(f"[{self.__class__.__name__}] Updated settings.yml with {len(self.proxies)} proxies.")

            # 4. Restart Docker
            # docker compose -f ... restart searxng
            cmd = ["docker", "compose", "-f", docker_compose_path, "restart", "searxng"]
            print(f"Running: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                 return True, f"Successfully injected {len(self.proxies)} proxies and restarted SearXNG."
            else:
                 return False, f"Updated config but Docker restart failed: {result.stderr}"

        except Exception as e:
            return False, f"Error updating SearXNG config: {e}"

    async def import_proxies(self, raw_text: str):
        """Imports a list of proxies from a raw string (one per line or comma/space separated)."""
        # Regex to find IP:Port pattern
        # Supports: 1.1.1.1:8080, http://1.1.1.1:8080, etc.
        pattern = re.compile(r'(?:http[s]?://)?(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{2,5})')
        matches = pattern.findall(raw_text)
        
        imported_count = 0
        new_proxies = []
        
        for p in matches:
            # Clean up
            clean = p.replace("http://", "").replace("https://", "")
            if clean not in self.proxies and clean not in self.bad_proxies:
                self.proxies.append(clean)
                new_proxies.append(clean)
                imported_count += 1
                
        # Optional: Validate immediately? Usually better to let the user trigger validation.
        print(f"[{self.__class__.__name__}] Imported {imported_count} new proxies.")
        return imported_count, new_proxies

    def remove_proxy(self, proxy):
        """Removes a bad proxy from the list."""
        clean_proxy = proxy.replace("http://", "").replace("https://", "")
        if clean_proxy in self.proxies:
            self.proxies.remove(clean_proxy)
            self.bad_proxies.add(clean_proxy)
            print(f"Removed bad proxy: {clean_proxy}. Remaining: {len(self.proxies)}")

    async def enable_proxies(self):
        """Enables upstream proxies and triggers a fresh harvest if needed."""
        self.enabled = True
        print(f"[{self.__class__.__name__}] Enabling proxies...")
        
        # Logic fix: If we are enabling, we MUST inject.
        # If we have proxies in memory, inject them. 
        # If not, we must harvest regardless of 'freshness' timestamp because 
        # settings.yml might have been wiped by a previous Disable.
        
        if not self.proxies:
             print(f"[{self.__class__.__name__}] No proxies in memory. Forcing harvest...")
             await self.fetch_proxies()
        
        if self.proxies:
            success, msg = await self.update_searxng_config()
            self._save_status()
            return success, msg
        else:
            return False, "Failed to enable: Could not harvest any proxies."

    async def disable_proxies(self):
        """Disables upstream proxies and removes them from SearXNG config."""
        self.enabled = False
        print(f"[{self.__class__.__name__}] Disabling proxies...")
        
        # Remove from SearXNG
        success, msg = await self.update_searxng_config()
        self._save_status()
        
        if success:
            return True, "Proxies disabled and removed from configuration."
        return False, f"Failed to disable proxies: {msg}"

    async def ensure_fresh_proxies(self):
        """Checks if proxies are fresh (checked within 24h). If not, harvests and updates SearXNG."""
        if not self.enabled:
             print(f"[{self.__class__.__name__}] Proxies are DISABLED. Skipping startup check.")
             return

        print(f"[{self.__class__.__name__}] Checking proxy freshness...")
        
        is_fresh = self._check_status()
        if is_fresh:
            print(f"[{self.__class__.__name__}] Proxies are fresh. Skipping startup harvest.")
            return

        print(f"[{self.__class__.__name__}] Proxies are STALE or MISSING. Initiating fresh harvest...")
        
        # Harvest
        await self.fetch_proxies()
        
        if self.proxies:
            # Update SearXNG
            success, msg = await self.update_searxng_config()
            if success:
                print(f"[{self.__class__.__name__}] {msg}")
                self._save_status()
            else:
                print(f"[{self.__class__.__name__}] Warning: Failed to update SearXNG: {msg}")
        else:
            print(f"[{self.__class__.__name__}] Critical: Harvest yielded no proxies.")

    def _check_status(self, max_age_hours=24):
        """Returns True if valid status file exists and is recent."""
        if not os.path.exists(self.status_file):
            return False
            
        try:
            with open(self.status_file, 'r') as f:
                data = json.load(f)
                
            last_updated = data.get("last_updated", 0)
            if time.time() - last_updated < (max_age_hours * 3600):
                return True
                
            return False # Too old
        except Exception as e:
            print(f"Error reading status file: {e}")
            return False

    def _save_status(self):
        """Update the freshness timestamp."""
        try:
            with open(self.status_file, 'w') as f:
                json.dump({
                    "last_updated": time.time(),
                    "params": {"count": len(self.proxies), "enabled": self.enabled}
                }, f)
        except Exception as e:
            print(f"Error saving status file: {e}")

# Global instance
proxy_manager = ProxyManager()

if __name__ == "__main__":
    # Ensure we can import modules if run as script
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    parser = argparse.ArgumentParser(description="Proxy Manager CLI")
    parser.add_argument("--check", action="store_true", help="Check freshness and update if stale")
    args = parser.parse_args()
    
    if args.check:
        try:
            asyncio.run(proxy_manager.ensure_fresh_proxies())
        except Exception as e:
            print(f"Startup check failed: {e}")
            sys.exit(1)

