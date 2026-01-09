
from urllib.parse import urlparse

# Simulation of the logic I just added
def is_valid_url(url, platform):
    try:
        parsed = urlparse(url)
        hostname = parsed.hostname.lower() if parsed.hostname else ""
        
        # Strict Punycode Check
        if "xn--" in hostname:
            return False, "Punycode"
            
        allowed_hosts = {
            f"{platform}.com",
            f"www.{platform}.com",
            f"m.{platform}.com"
        }
        
        if platform in ["twitter", "x"]:
            allowed_hosts.update(["x.com", "www.x.com", "mobile.twitter.com"])
            
        if hostname not in allowed_hosts:
            return False, f"Bad Subdomain: {hostname}"
            
        path = parsed.path.lower()
        junk_paths = [
            "/reel/", "/p/", "/stories/", "/tags/", "/explore/", 
            "/help", "/about", "/legal", "/safety", "/guidelines", 
            "/developer", "/ads", "/newsroom"
        ]
        
        if any(jp in path for jp in junk_paths):
            return False, f"Junk Path: {path}"
            
        return True, "Valid"
    except:
        return False, "Exception"

def test_filtering_logic():
    print("Testing Strict Validation Logic...")
    
    cases = [
        ("https://www.tiktok.com/@user", "tiktok", True),
        ("https://ads.tiktok.com/dashboard", "tiktok", False),
        ("https://newsroom.tiktok.com/en-us", "tiktok", False),
        ("https://www.instagram.com/p/12345", "instagram", False),
        ("https://help.instagram.com/", "instagram", False),
        ("https://www.instagram.com/reel/123", "instagram", False),
        ("https://m.tiktok.com/v/123", "tiktok", True), # Assuming /v/ is okayish or caught elsewhere, logic allows m.
        ("https://www.instagram.xn--com-ls0a/", "instagram", False)
    ]
    
    failures = 0
    for url, plat, expected in cases:
        valid, reason = is_valid_url(url, plat)
        status = "PASS" if valid == expected else "FAIL"
        print(f"[{status}] {url} -> {valid} ({reason})")
        if status == "FAIL": failures += 1
        
    if failures == 0:
        print("SUCCESS: All validation cases passed.")
    else:
        print(f"FAILURE: {failures} cases failed.")

if __name__ == "__main__":
    test_filtering_logic()
