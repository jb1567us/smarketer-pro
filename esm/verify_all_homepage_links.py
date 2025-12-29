import requests
from bs4 import BeautifulSoup
import concurrent.futures
import time

def check_url(url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        # Saatchi sometimes blocks HEAD, so using GET with stream=True to avoid downloading body
        r = requests.get(url, headers=headers, stream=True, timeout=10)
        r.close()
        return url, r.status_code
    except Exception as e:
        return url, str(e)

def verify_all_links():
    homepage = "https://elliotspencermorgan.com/"
    print(f"Fetching homepage: {homepage}...")
    
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        r = requests.get(homepage, headers=headers, verify=False, timeout=20)
        soup = BeautifulSoup(r.text, 'html.parser')
        
        links = []
        for a in soup.find_all('a', href=True):
            href = a['href']
            if 'saatchiart.com' in href:
                links.append(href)
        
        # Remove duplicates
        links = list(set(links))
        print(f"Found {len(links)} unique Saatchi links. Checking status codes...")
        
        broken = []
        working = []
        errors = []

        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            future_to_url = {executor.submit(check_url, url): url for url in links}
            completed = 0
            for future in concurrent.futures.as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    checked_url, status = future.result()
                    completed += 1
                    if completed % 10 == 0:
                        print(f"Checked {completed}/{len(links)}...")

                    if status == 200:
                        working.append(url)
                    elif status == 404:
                        print(f"❌ 404 BROKEN: {url}")
                        broken.append(url)
                    else:
                        print(f"⚠️ Status {status}: {url}")
                        errors.append((url, status))
                except Exception as exc:
                    print(f"💥 Exception for {url}: {exc}")
                    errors.append((url, str(exc)))

        print("\n--- STATUS REPORT ---")
        print(f"Total Links Checked: {len(links)}")
        print(f"✅ Working (200): {len(working)}")
        print(f"❌ Broken (404): {len(broken)}")
        print(f"⚠️ Other Errors: {len(errors)}")
        
        if broken:
            print("\n!!! BROKEN LINKS LIST !!!")
            for b in broken:
                print(b)
        else:
            print("\n🎉 All Saatchi links are valid!")

    except Exception as e:
        print(f"Homepage fetch failed: {e}")

if __name__ == "__main__":
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    verify_all_links()
