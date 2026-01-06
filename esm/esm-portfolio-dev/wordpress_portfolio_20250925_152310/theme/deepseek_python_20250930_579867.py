import requests
from bs4 import BeautifulSoup
import re

def comprehensive_art_view_scraper():
    """
    Comprehensive scraper for art view links with exact pattern matching
    """
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    urls = [
        "https://www.saatchiart.com/account/artworks/1295487",
        "https://www.saatchiart.com/account/artworks/1295487?page=2"
    ]
    
    all_art_links = set()
    
    # Exact pattern: /art/word-or-dash/numbers/numbers/view
    pattern = r'https://www\.saatchiart\.com/art/[a-zA-Z0-9-]+/\d+/\d+/view'
    
    for url in urls:
        try:
            print(f"🔍 Scanning: {url}")
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            # Convert to text for regex searching
            page_content = response.text
            
            # Find all matches in the entire page content
            matches = re.findall(pattern, page_content)
            all_art_links.update(matches)
            
            # Also search for relative URLs
            relative_pattern = r'/art/[a-zA-Z0-9-]+/\d+/\d+/view'
            relative_matches = re.findall(relative_pattern, page_content)
            for match in relative_matches:
                full_url = 'https://www.saatchiart.com' + match
                all_art_links.add(full_url)
            
            # Also parse with BeautifulSoup as backup
            soup = BeautifulSoup(response.content, 'html.parser')
            for element in soup.find_all(['a', 'link', 'script']):
                if element.has_attr('href'):
                    href = element['href']
                    if re.search(relative_pattern, href):
                        if href.startswith('/'):
                            href = 'https://www.saatchiart.com' + href
                        all_art_links.add(href)
            
            print(f"✅ Found {len(matches) + len(relative_matches)} pattern matches on this page")
            
        except Exception as e:
            print(f"❌ Error with {url}: {e}")
    
    # Convert to sorted list
    sorted_links = sorted(list(all_art_links))
    return sorted_links

print("🚀 Starting comprehensive art view link scraping...\n")
print("🎯 Target pattern: https://www.saatchiart.com/art/.*/.*/.*/view\n")

art_view_links = comprehensive_art_view_scraper()

print(f"\n🎉 SCRAPING COMPLETE!")
print(f"📊 Total unique art view links found: {len(art_view_links)}\n")

print("🔗 All art view links:")
for i, link in enumerate(art_view_links, 1):
    print(f"{i:2d}. {link}")

# Save to files
with open("art_view_links.txt", "w", encoding="utf-8") as f:
    for link in art_view_links:
        f.write(link + "\n")

with open("art_view_links_simple.txt", "w", encoding="utf-8") as f:
    for link in art_view_links:
        f.write(link + "\n")

print(f"\n💾 Links saved to:")
print("   - art_view_links.txt")
print("   - art_view_links_simple.txt (clean list for copying)")

print(f"\n📋 Simple list:")
for link in art_view_links:
    print(link)