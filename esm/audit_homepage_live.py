import requests
from bs4 import BeautifulSoup
import re

def audit_homepage():
    url = "https://elliotspencermorgan.com/"
    print(f"Fetching {url}...")
    
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        r = requests.get(url, headers=headers, verify=False, timeout=15)
        soup = BeautifulSoup(r.text, 'html.parser')
        
        # correct_urls map (Title -> URL) or just a set of Valid URLs?
        # Let's just look for what IS there vs what SHOULD be there for the broken ones.
        
        # Find all Saatchi links
        links = soup.find_all('a', href=re.compile(r'saatchiart\.com'))
        
        print(f"\nFound {len(links)} Saatchi links on homepage:")
        
        found_waves = False
        found_glacier = False
        found_red = False
        
        for link in links:
            href = link.get('href')
            parent = link.find_parent(class_='caviar-post-item') or link.find_parent('article')
            # Try to identify which artwork this is
            # Ideally we'd map this, but for now let's just grep the URL content
            
            status = "UNK"
            if "Painting-Waves/1295487/6364287" in href:
                status = "✅ CORRECT (Waves)"
                found_waves = True
            elif "Painting-Waves" in href:
                status = "❌ WRONG (Waves)"
                
            elif "Painting-Blue-Glacier/1295487/6446603" in href:
                status = "✅ CORRECT (Blue Glacier)"
                found_glacier = True
            elif "Painting-Blue-Glacier" in href:
                status = "❌ WRONG (Blue Glacier)"
                
            elif "Collage-Pieces-of-Red" in href:
                status = "✅ CORRECT (Pieces of Red)"
                found_red = True
            elif "Collage-Pieces-Of-Red" in href:
                status = "❌ WRONG (Pieces of Red - Casing)"
            
            print(f"[{status}] {href}")

        print("\n--- Summary ---")
        if found_waves: print("Waves: Fixed")
        else: print("Waves: BROKEN")
        
        if found_glacier: print("Blue Glacier: Fixed")
        else: print("Blue Glacier: BROKEN")
        
        if found_red: print("Pieces of Red: Fixed")
        else: print("Pieces of Red: BROKEN")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    audit_homepage()
