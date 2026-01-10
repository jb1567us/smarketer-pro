import json
import requests
from concurrent.futures import ThreadPoolExecutor

def check_url(url, title):
    try:
        r = requests.head(url, timeout=5)
        if r.status_code != 200:
            return f"[BROKEN] {title}: {url} (Status: {r.status_code})"
    except Exception as e:
        return f"[ERROR] {title}: {url} ({e})"
    return None

def audit_images():
    with open('artwork_data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    missing_images = []
    urls_to_check = []

    print(f"Scanning {len(data)} artworks...")

    for item in data:
        title = item.get('title', 'Unknown Title')
        img_url = item.get('image_url')

        if not img_url:
            missing_images.append(title)
        else:
            urls_to_check.append((img_url, title))

    print(f"\nFound {len(missing_images)} artworks with NO image_url in JSON:")
    for m in missing_images:
        print(f" - {m}")

    print(f"\nChecking {len(urls_to_check)} image URLs for reachability...")
    
    broken_links = []
    with ThreadPoolExecutor(max_workers=20) as executor:
        futures = [executor.submit(check_url, u, t) for u, t in urls_to_check]
        for f in futures:
            result = f.result()
            if result:
                broken_links.append(result)

    if broken_links:
        print(f"\nFound {len(broken_links)} BROKEN image links:")
        for b in broken_links:
            print(b)
    else:
        print("\nAll image links are reachable.")

if __name__ == "__main__":
    audit_images()
