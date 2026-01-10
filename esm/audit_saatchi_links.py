import json
import requests
import concurrent.futures

def check_url(url):
    try:
        # User-Agent to avoid 403 blocks often used by scraping protections
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        response = requests.head(url, headers=headers, timeout=5, allow_redirects=True)
        if response.status_code == 404:
            return url, 404
        return None
    except Exception:
        return url, "Error"

def audit_links():
    path = r"c:\sandbox\esm\artwork_data.json"
    print("Loading artwork data...")
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    urls = []
    for item in data:
        if 'saatchi_url' in item and item['saatchi_url']:
            urls.append(item['saatchi_url'])
            
    print(f"Found {len(urls)} Saatchi URLs. Checking status (this may take a moment)...")
    
    broken_links = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(check_url, url): url for url in urls}
        for future in concurrent.futures.as_completed(future_to_url):
            result = future.result()
            if result:
                broken_links.append(result)
                print(f"BROKEN: {result[0]} ({result[1]})")

    print(f"\nAudit Complete. Found {len(broken_links)} broken links.")

if __name__ == "__main__":
    audit_links()
