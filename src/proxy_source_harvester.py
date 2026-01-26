import script_context
import requests
import re
import time
import random
import json
import os
import ipaddress
from urllib.parse import urlparse
from database import add_proxy_source, get_proxy_sources

class ProxySourceHarvester:
    def __init__(self):
        self.dorks = []
        self._load_dorks()
        
        # Regex for IP:PORT (Supporting IPv4)
        # Handles 1.1.1.1:80, 1.1.1.1 80, 1.1.1.1\t80
        self.proxy_pattern = re.compile(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})[:\s\t]+(\d{2,5})')
        
    def _inject_known_sources(self):
        """Injects known high-quality massive proxy lists to ensure baseline performance."""
        known_sources = [
            "https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/http.txt",
            "https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/socks5.txt",
            "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/http.txt",
            "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/socks5.txt",
            "https://raw.githubusercontent.com/zloi-user/hideip.me/main/http.txt",
            "https://raw.githubusercontent.com/zloi-user/hideip.me/main/socks5.txt",
            "https://raw.githubusercontent.com/hookzof/socks5_list/master/proxy.txt",
            "https://raw.githubusercontent.com/rdavydov/proxy-list/main/proxies/http.txt",
            "https://raw.githubusercontent.com/rdavydov/proxy-list/main/proxies/socks5.txt",
            "https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/protocols/http/data.txt",
            "https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/protocols/socks5/data.txt",
        ]
        from database import add_proxy_source
        print(f"[Harvester] Injecting {len(known_sources)} known high-volume sources...")
        for url in known_sources:
             add_proxy_source(url, 'http') # Default to http, will detect later

    def _load_dorks(self):
        """Loads dorks from dorks.json"""
        json_path = os.path.join(os.path.dirname(__file__), "dorks.json")
        try:
            if os.path.exists(json_path):
                with open(json_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Flatten the dictionary values into a single list
                    for category in data.values():
                        if isinstance(category, list):
                            self.dorks.extend(category)
            else:
                print(f"[Harvester] Warning: {json_path} not found. Using fallbacks.")
                # Fallback
                self.dorks = [
                    "site:github.com intitle:proxy-list http.txt",
                    "raw proxy list txt 2026"
                ]
            
            print(f"[Harvester] Loaded {len(self.dorks)} dorks.")
        except Exception as e:
            print(f"[Harvester] Error loading dorks: {e}")
            self.dorks = ["inurl:proxylist.txt"]

    def is_public_ip(self, ip):
        """Checks if an IP is public (not private/local/reserved)."""
        try:
            ip_obj = ipaddress.ip_address(ip)
            return not (ip_obj.is_private or ip_obj.is_loopback or ip_obj.is_link_local or ip_obj.is_multicast or ip_obj.is_reserved)
        except ValueError:
            return False

    def search_for_sources(self):
        """
        Uses a public search engine (via DuckDuckGo HTML for simplicity/robustness without API keys)
        to find potential proxy lists.
        """
        potential_urls = set()
        
        # Use ALL dorks for maximum harvest (User Request: >41k context)
        dorks_to_use = self.dorks
        
        for dork in dorks_to_use:
            try:
                # Use DDG HTML (no JS needed)
                headers = {'User-Agent': 'Mozilla/5.0'}
                url = f"https://html.duckduckgo.com/html/?q={dork}"
                resp = requests.get(url, headers=headers, timeout=10)
                
                print(f"[Harvester] {dork} -> Status {resp.status_code}")
                
                # Extract results
                # Try generic link extraction if specific class fails
                links = re.findall(r'href="(https?://[^"]+)"', resp.text)
                
                if not links:
                     # Check if we got a captcha or weird page
                     if "captcha" in resp.text.lower():
                         print(f"[Harvester] CAPTCHA detected for {dork}. Skipping.")
                         continue
                     print(f"[Harvester] No links found for {dork}. HTML snippet: {resp.text[:200]}...")
                
                for link in links:
                    # Filter out obvious junk
                    if "duckduckgo" in link or "microsoft" in link: continue
                    if "google.com" in link or "yandex" in link: continue
                    
                    # Prefer raw links for github
                    if "github.com" in link and "/blob/" in link:
                        link = link.replace("/blob/", "/raw/")
                    
                    # Special handling for pastebin raw
                    if "pastebin.com" in link and "raw" not in link:
                         # Attempt to convert to raw if it looks like a paste
                         # e.g. pastebin.com/ABCD -> pastebin.com/raw/ABCD
                         parts = link.split("/")
                         if len(parts) > 3 and "raw" not in parts:
                             # simple heuristic
                             pass
                    
                    print(f"[Harvester] Found candidate: {link}")
                    potential_urls.add(link)
                    
                time.sleep(random.uniform(2, 5)) # Be polite
            except Exception as e:
                print(f"[Harvester] Error searching dork '{dork}': {e}")

        print(f"[Harvester] Found {len(potential_urls)} candidate URLs.")
        return list(potential_urls)

    def validate_and_add(self, url):
        """
        Fetches the URL and checks if it looks like a proxy list.
        """
        try:
            resp = requests.get(url, timeout=10)
            if resp.status_code != 200: 
                return False
                
            text = resp.text
            # Use regex to find potential matches
            matches = self.proxy_pattern.findall(text)
            
            # Filter and validate
            valid_proxies = []
            for ip, port in matches:
                if self.is_public_ip(ip):
                    valid_proxies.append(f"{ip}:{port}")
            
            # Heuristic: Must have at least 20 valid public proxies
            if len(valid_proxies) > 20:
                print(f"[Harvester] ✅ Valid source found ({len(valid_proxies)} proxies): {url}")
                add_proxy_source(url, 'http') # Default to http, auto-detect later
                return True
            else:
                return False
        except:
            return False

    def harvest(self):
        """
        Main method to find and harvest proxies.
        """
        print("[Harvester] 🌍 Searching for new proxy sources...")
        self._inject_known_sources()
        
        candidates = self.search_for_sources()
        new_count = 0
        for url in candidates:
            # Check if we already have it (simple optimization)
            existing = [s['url'] for s in get_proxy_sources(active_only=False)]
            if url in existing:
                continue
                
            if self.validate_and_add(url):
                new_count += 1
                
        print(f"[Harvester] Cycle complete. Added {new_count} new sources.")
        return new_count

if __name__ == "__main__":
    harvester = ProxySourceHarvester()
    harvester.harvest()
