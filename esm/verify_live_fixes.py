import json
import requests
import re

def verify_live():
    # 1. Get Slugs
    path = r"c:\sandbox\esm\artwork_data.json"
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    slugs = {}
    targets = ["Pieces of Red", "Waves", "Blue Glacier"]
    
    for item in data:
        title = item.get("title", "")
        for t in targets:
            if t in title:
                slugs[t] = item.get("slug")
    
    print("Found Slugs:", slugs)
    
    # 2. Fetch Pages and Check Links
    base_url = "https://elliotspencermorgan.com"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    
    # Check Logo on Homepage
    print(f"\nChecking Homepage: {base_url}")
    try:
        r = requests.get(base_url, headers=headers, verify=False, timeout=10)
        # Check Logo Width/Lazy
        if 'width="299"' in r.text and 'height="234"' in r.text:
            print("✅ Logo: Dimensions present")
        else:
            print("❌ Logo: Dimensions MISSING")
            
        if 'loading="eager"' in r.text:
            print("✅ Logo: loading=eager present")
        else:
            print("❌ Logo: loading=eager MISSING")
            
        if 'max-width: 550px' in r.text:
             print("✅ Header: max-width: 550px present")
        else:
             # It might be in inline style or css, check inline first
             if 'max-width: 550px' in r.text:
                 pass 
             else:
                 print("⚠️ Header: max-width 550px NOT found in HTML source (might be ok if computed)")

    except Exception as e:
        print(f"Homepage check failed: {e}")

    # Check Artworks
    for t, slug in slugs.items():
        if not slug:
            print(f"Skipping {t} (no slug)")
            continue
            
        url = f"{base_url}/{slug}/"
        print(f"\nChecking {t}: {url}")
        try:
            r = requests.get(url, headers=headers, verify=False, timeout=10)
            
            # Find Saatchi Link
            # Naive check: does the body contain the CORRECT Saatchi ID/String?
            if t == "Pieces of Red":
                if "Collage-Pieces-of-Red" in r.text:
                     print("✅ Pieces of Red: Correct URL found")
                elif "Collage-Pieces-Of-Red" in r.text:
                     print("❌ Pieces of Red: OLD URL found (Case fail)")
                else:
                     print("❌ Pieces of Red: Link NOT found")

            elif t == "Waves":
                # New ID: 6364287
                if "6364287" in r.text:
                    print("✅ Waves: Correct ID (6364287) found")
                else:
                    print("❌ Waves: Correct ID NOT found")

            elif "Blue Glacier" in t:
                 # New ID: 6446603
                if "6446603" in r.text:
                    print("✅ Blue Glacier: Correct ID (6446603) found")
                else:
                    print("❌ Blue Glacier: Correct ID NOT found")

        except Exception as e:
             print(f"Check failed for {t}: {e}")

if __name__ == "__main__":
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    verify_live()
