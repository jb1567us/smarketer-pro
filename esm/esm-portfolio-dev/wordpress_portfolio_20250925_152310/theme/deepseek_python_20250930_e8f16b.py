import requests
from bs4 import BeautifulSoup
import re

def scrape_view_links():
    """
    Scrape all links ending with '/view' from the specified pages
    """
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
    }
    
    # The two pages you provided
    urls = [
        "https://www.saatchiart.com/account/artworks/1295487",
        "https://www.saatchiart.com/account/artworks/1295487?page=2"
    ]
    
    all_view_links = []
    
    for url in urls:
        try:
            print(f"🔍 Scraping: {url}")
            
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find ALL links on the page
            all_links = soup.find_all('a', href=True)
            
            # Filter for links ending with '/view'
            view_links = []
            for link in all_links:
                href = link['href']
                # Check if href ends with '/view'
                if href.endswith('/view'):
                    # Convert to full URL if relative
                    if href.startswith('/'):
                        href = 'https://www.saatchiart.com' + href
                    view_links.append(href)
            
            print(f"✅ Found {len(view_links)} '/view' links on this page")
            all_view_links.extend(view_links)
            
        except Exception as e:
            print(f"❌ Error scraping {url}: {e}")
    
    # Remove duplicates while preserving order
    unique_links = []
    for link in all_view_links:
        if link not in unique_links:
            unique_links.append(link)
    
    return unique_links

# Let's run it!
print("🚀 Scraping all '/view' links from both pages...\n")

view_links = scrape_view_links()

print(f"\n🎉 COMPLETE!")
print(f"📊 Total unique '/view' links found: {len(view_links)}\n")

print("🔗 All '/view' links:")
for i, link in enumerate(view_links, 1):
    print(f"{i:2d}. {link}")

# Save to file
with open("view_links.txt", "w", encoding="utf-8") as f:
    for link in view_links:
        f.write(link + "\n")

print(f"\n💾 Links saved to 'view_links.txt'")