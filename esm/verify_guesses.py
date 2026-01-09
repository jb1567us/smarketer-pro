import requests

def check(url):
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        r = requests.head(url, headers=headers, timeout=5)
        print(f"[{r.status_code}] {url}")
    except:
        print(f"[ERR] {url}")

urls = [
    # Pieces of Red (Verify fix)
    "https://www.saatchiart.com/art/Collage-Pieces-of-Red/1295487/6583729/view",
    
    # Waves -> Blue Wave?
    "https://www.saatchiart.com/art/Painting-Blue-Wave/1295487/6105315/view",
    "https://www.saatchiart.com/art/Painting-blue-wave/1295487/6105315/view",
    
    # Blue Glacier
    "https://www.saatchiart.com/art/Painting-Blue-Glacier/1295487/6105345/view", # Original (Broken)
    "https://www.saatchiart.com/art/Painting-Blue-Glacier/1295487/6105345/view".lower(), # All lower (unlikely for Saatchi)
    "https://www.saatchiart.com/art/Painting-Blue-glacier/1295487/6105345/view", # Lower G 
]

check_urls = urls
for u in urls:
    check(u)
