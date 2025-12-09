import requests
from bs4 import BeautifulSoup
import re

def scrape_art_view_links():
    """
    Scrape all links matching pattern: https://www.saatchiart.com/art/.*/.*/.*/view
    """
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    urls = [
        "https://www.saatchiart.com/account/artworks/1295487",
        "https://www.saatchiart.com/account/artworks/1295487?page=2"
    ]
    
    all_art_links = []
    
    for url in urls:
        try:
            print(f"🔍 Scraping: {url}")
            
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find ALL links on the page
            all_links = soup.find_all('a', href=True)
            
            # Regex pattern for: /art/anything/anything/anything/view
            pattern = r'/art/[^/]+/[^/]+/[^/]+/view'
            
            for link in all_links:
                href = link['href']
                
                # Check if href matches our pattern
                if re.search(pattern, href):
                    # Convert to full URL if relative
                    if href.startswith('/'):
                        full_url = 'https://www.saatchiart.com' + href
                    else:
                        full_url = href
                    
                    all_art_links.append(full_url)
            
            print(f"✅ Found {len([l for l in all_art_links if url in str(l)])} art view links on this page")
            
        except Exception as e:
            print(f"❌ Error scraping {url}: {e}")
    
    # Remove duplicates while preserving order
    unique_links = []
    for link in all_art_links:
        if link not in unique_links:
            unique_links.append(link)
    
    return unique_links

print("🚀 Scraping art view links with pattern: /art/.*/.*/.*/view\n")

art_links = scrape_art_view_links()

print(f"\n🎉 COMPLETE!")
print(f"📊 Total unique art view links found: {len(art_links)}\n")

print("🔗 All art view links:")
for i, link in enumerate(art_links, 1):
    print(f"{i:2d}. {link}")

# Save to file
with open("art_view_links.txt", "w", encoding="utf-8") as f:
    for link in art_links:
        f.write(link + "\n")

print(f"\n💾 Links saved to 'art_view_links.txt'")