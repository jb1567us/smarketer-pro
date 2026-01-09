import requests
import os

URLS = [
    ("Portal (JSON)", "https://elliotspencermorgan.com/wp-content/uploads/2025/11/PortalPainting.jpg"),
    ("Portal (User Hint)", "https://elliotspencermorgan.com/wp-content/uploads/2025/11-holdingspace-originals/PortalPainting.jpg"),
    ("Saatchi Link (Moon Dance)", "https://images.saatchiart.com/saatchi/1295487/art/6492627/5562305-HSC00001-7.jpg")
]

print("Testing Image Downloads...")
for name, url in URLS:
    try:
        print(f"\nChecking {name}: {url}")
        r = requests.head(url, timeout=5)
        print(f"HEAD Status: {r.status_code}")
        if r.status_code != 200:
            # try get
            r = requests.get(url, stream=True, timeout=5)
            print(f"GET Status: {r.status_code}")
        
        if r.status_code == 200:
            print("[OK] Success")
        else:
            print("[FAIL] Failed")
            
    except Exception as e:
        print(f"[ERR] Error: {e}")
