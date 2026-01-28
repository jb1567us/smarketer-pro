import yaml
import os
import re
from config import config
from database import get_best_proxies
from utils.litedock_manager import litedock_manager

class SearXNGConfigEditor:
    def __init__(self, project_root):
        self.project_root = project_root
        self.settings_path = os.path.join(project_root, "searxng", "searxng", "settings.yml")

    def update_config(self, enabled=True, tor_available=False):
        """Updates SearXNG's settings.yml with current best proxies."""
        if not os.path.exists(self.settings_path):
            return False, f"Settings file not found at {self.settings_path}"

        try:
            with open(self.settings_path, "r", encoding="utf-8") as f:
                content = f.read()

            proxy_list_yaml = "    all://:\n"
            if enabled:
                # 1. Check Tor-Only Mode
                if config.get("proxies", {}).get("tor_only", False):
                     proxy_list_yaml += "      - socks5://app:9050\n"
                else:
                    total_limit = config.get("proxies", {}).get("max_proxies", 500)
                    elite_limit = int(total_limit * 0.4)
                    std_limit = total_limit - elite_limit
                    
                    elite_proxies = get_best_proxies(limit=elite_limit, min_anonymity='elite', min_success_count=1)
                    standard_proxies = get_best_proxies(limit=std_limit, min_anonymity='standard', min_success_count=1)
                    combined_pool = elite_proxies + standard_proxies
                    
                    # Tor Fallback Safety Net
                    if len(combined_pool) < 10 and tor_available:
                         proxy_list_yaml += "      - socks5://app:9050\n"

                    if combined_pool:
                        for p in combined_pool:
                            addr = p['address']
                            if not addr.startswith("http"): addr = f"http://{addr}"
                            proxy_list_yaml += f"      - {addr}\n"
                    elif tor_available:
                         proxy_list_yaml += "      - socks5://app:9050\n"
                    else:
                         proxy_list_yaml = "    # No premium proxies available\n"
            else:
                proxy_list_yaml = "    # Proxies disabled\n"

            # Section identification logic
            parts = content.split("outgoing:", 1)
            if len(parts) < 2: return False, "Could not find 'outgoing:' section"
                
            pre_outgoing = parts[0] + "outgoing:"
            post_outgoing = parts[1]
            regex_proxies = r"(\n  proxies:\n(?:    .*\n)*)"
            new_block = "\n  proxies:\n" + proxy_list_yaml
            
            if re.search(regex_proxies, post_outgoing, re.MULTILINE):
                 post_outgoing = re.sub(regex_proxies, "", post_outgoing, flags=re.MULTILINE)
            
            if not post_outgoing.startswith("\n"): post_outgoing = "\n" + post_outgoing
            post_outgoing = new_block + post_outgoing
            final_content = pre_outgoing + post_outgoing
            
            # Enhancements
            if "formats:" in final_content:
                 final_content = final_content.replace("formats:\n    - html", "formats:\n    - html\n    - json")
            if "limiter: true" in final_content:
                 final_content = final_content.replace("limiter: true", "limiter: false")
            if "- duckduckgo" in final_content and "- brave" not in final_content:
                final_content = final_content.replace("- duckduckgo", "- duckduckgo\n      - brave\n      - qwant")

            with open(self.settings_path, "w", encoding="utf-8") as f:
                f.write(final_content)

            # Restart SearXNG
            success = litedock_manager.restart_searxng()
            return success, "Updated and restarted SearXNG" if success else "Restart failed"
        except Exception as e:
            return False, str(e)
