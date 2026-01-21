import os
import re
import urllib.request
import concurrent.futures
import time
import json
import random
import socket

# Target Settings File
user_profile = os.environ.get('USERPROFILE')
settings_path = os.path.join(user_profile, '.litedock', 'images', 'searxng_searxng_latest', 'usr', 'local', 'searxng', 'searx', 'settings.yml')

# Config
PROXY_SOURCE = "https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/http.txt"
# CRITICAL: We must check HTTPS support. HTTP-only proxies fail with "Proxy Error" on Google/DDG.
VERIFY_URL = "https://httpbin.org/get" 
MAX_PROXIES = 150 # Increased for high volume
CACHE_FILE = "valid_proxies.json"
CACHE_DURATION_SECONDS = 21600  # 6 Hours

def get_real_ip():
    try:
        with urllib.request.urlopen("http://httpbin.org/ip", timeout=5) as response:
             data = json.loads(response.read().decode())
             return data.get("origin", "").split(',')[0]
    except:
        return None

def get_raw_proxies():
    print(f"Fetching fresh proxies from {PROXY_SOURCE}...")
    try:
        with urllib.request.urlopen(PROXY_SOURCE, timeout=10) as response:
            content = response.read().decode('utf-8')
            lines = [line.strip() for line in content.splitlines() if line.strip()]
            random.shuffle(lines)
            return lines
    except Exception as e:
        print(f"Error fetching proxies: {e}")
        return []

def verify_elite_proxy(proxy, real_ip):
    """
    Verifies if a proxy is working AND is 'Elite' (High Anonymity).
    Elite = Remote server does not know it's a proxy (no Via/X-Forwarded-For headers)
    """
    proxy_url = f"http://{proxy}"
    proxy_handler = urllib.request.ProxyHandler({'http': proxy_url, 'https': proxy_url})
    opener = urllib.request.build_opener(proxy_handler)
    
    # Fake a standard browser user agent
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
    
    try:
        # Request HTTPS url. If proxy is HTTP-only, this throws error (CONNECT failed)
        req = urllib.request.Request(VERIFY_URL, headers=headers)
        with opener.open(req, timeout=5) as response:
             if response.getcode() == 200:
                 data = json.loads(response.read().decode())
                 returned_headers = data.get("headers", {})
                 origin = data.get("origin", "")

                 # 1. Check Transparency (Did it reveal our IP?)
                 if real_ip and real_ip in origin:
                     return None # Transparent (Bad)

                 # 2. Check Anonymity Headers (Did it admit it's a proxy?)
                 # Elite proxies do NOT send these headers.
                 proxy_headers = ["Via", "X-Forwarded-For", "Proxy-Connection", "X-Proxy-ID"]
                 for h in proxy_headers:
                     # Check case-insensitive
                     if any(k.lower() == h.lower() for k in returned_headers.keys()):
                         return None # Anonymous but not Elite (Bad for stealth)

                 return proxy
    except:
        pass
    return None

def load_cache():
    if not os.path.exists(CACHE_FILE):
        return None
    try:
        with open(CACHE_FILE, 'r') as f:
            data = json.load(f)
            timestamp = data.get('timestamp', 0)
            # Check for Elite HTTPS tag.
            if data.get('validation_level') != 'elite_https':
                print("Old validation cache detected (HTTP-only). Invalidating to ensure HTTPS support...")
                return None
                
            if time.time() - timestamp < CACHE_DURATION_SECONDS:
                proxies = data.get('proxies', [])
                if proxies:
                    print(f"Entries loaded from ELITE HTTPS cache ({len(proxies)} proxies, age: {(time.time() - timestamp)/60:.1f} min)")
                    return proxies
    except Exception as e:
        print(f"Cache load error: {e}")
    return None

def save_cache(proxies):
    try:
        with open(CACHE_FILE, 'w') as f:
            json.dump({
                'timestamp': time.time(),
                'validation_level': 'elite_https',
                'proxies': proxies
            }, f)
        print("Elite HTTPS Proxies saved to cache.")
    except Exception as e:
        print(f"Cache save error: {e}")

def get_valid_proxies(force_refresh=False):
    # 1. Try Cache (unless forced)
    if not force_refresh:
        cached = load_cache()
        if cached:
            return cached

    # 2. Get Real IP for comparison
    print("Determining real IP for anonymity checks...")
    real_ip = get_real_ip()
    if not real_ip:
        print("Warning: Could not determine real IP. Strict transparency check disabled.")

    # 3. Harvest & Verify
    raw_proxies = get_raw_proxies()
    # USER OPTIMIZATION: Increased scan limit to 1500 to ensure we find enough Elite proxies
    check_limit = min(len(raw_proxies), 1500) 
    print(f"Fetched {len(raw_proxies)} candidates. Scanning random sample of {check_limit} for ELITE proxies...")

    valid_proxies = []
    
    # Using 150 workers for faster scanning of larger batch
    with concurrent.futures.ThreadPoolExecutor(max_workers=150) as executor:
        futures = [executor.submit(verify_elite_proxy, p, real_ip) for p in raw_proxies[:check_limit]] 
        
        completed = 0
        for future in concurrent.futures.as_completed(futures):
            completed += 1
            result = future.result()
            if result:
                valid_proxies.append(result)
                print(f"[ELITE] {result} ({len(valid_proxies)}/{MAX_PROXIES})")
                if len(valid_proxies) >= MAX_PROXIES:
                    break
            
            if completed % 200 == 0:
                print(f"Scanned {completed}/{check_limit}...")

    # 4. Save Cache
    if valid_proxies:
        save_cache(valid_proxies)
        
    return valid_proxies

def inject_proxies(force_refresh=False):
    if not os.path.exists(settings_path):
        print(f"Error: settings.yml not found at {settings_path}")
        return False

    # Pass force_refresh to get_valid_proxies logic (requires update below)
    # Ideally we refactor get_valid_proxies to accept it
    valid_proxies = get_valid_proxies(force_refresh=force_refresh)
    
    if not valid_proxies:
        print("No working proxies found. Using Direct Connection (Safe for local use, but risky for Dorks).")
        # Return True so we don't abort, just run without proxies
        return True

    print(f"Injecting {len(valid_proxies)} proxies into SearXNG settings...")
    
    # Read existing settings
    with open(settings_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Create proxy block with increased timeouts
    # Free proxies need more time than default (which is usually 2-3s)
    proxy_lines = [
        "\noutgoing:", 
        "  request_timeout: 15.0",       # Waiting time for a response (Increased for free proxies)
        "  max_request_timeout: 25.0",   # Max time for a request
        "  pool_connections: 200",       # Higher concurrency
        "  pool_maxsize: 200",
        "  proxies:", 
        "    all://:"
    ]
    for p in valid_proxies:
        proxy_lines.append(f"      - http://{p}")
    
    new_block = "\n".join(proxy_lines) + "\n"

    marker_start = "### PROXY_INJECTION_START ###"
    marker_end = "### PROXY_INJECTION_END ###"
    
    # Remove old block
    if marker_start in content and marker_end in content:
        content = re.sub(f"{marker_start}.*?{marker_end}", "", content, flags=re.DOTALL)
    
    # Append new
    # Append new proxy block
    content_with_proxies = content + f"\n\n{marker_start}{new_block}{marker_end}\n"
    
    # FIX: Inject Secret Key if default
    # We look for "secret_key: ultrasecretkey" or just ensure it's set
    import secrets
    new_key = secrets.token_hex(16)
    
    # Regex to find existing secret key
    # server:
    #   secret_key: "ultrasecretkey"
    
    if "ultrasecretkey" in content_with_proxies:
        print("Default secret key found. Replacing with secure random key...")
        content_with_proxies = content_with_proxies.replace("ultrasecretkey", new_key)
    
    with open(settings_path, 'w', encoding='utf-8') as f:
        f.write(content_with_proxies)
        
    print("Success! Proxies and Secret Key injected.")
    return True

if __name__ == "__main__":
    inject_proxies()
