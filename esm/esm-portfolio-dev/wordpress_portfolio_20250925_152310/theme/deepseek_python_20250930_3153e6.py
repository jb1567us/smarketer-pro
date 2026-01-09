import requests
from bs4 import BeautifulSoup
import re

def scrape_artwork_links():
    """
    Scrape all artwork links from the specified Saatchi Art pages
    """
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Referer': 'https://www.saatchiart.com/'
    }
    
    # The two pages you provided
    urls = [
        "https://www.saatchiart.com/account/artworks/1295487",
        "https://www.saatchiart.com/account/artworks/1295487?page=2"
    ]
    
    all_links = []
    
    for url in urls:
        try:
            print(f"🔍 Scraping page: {url}")
            
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for artwork links - these could be in various formats
            # Pattern 1: Full URLs with en-br
            full_links = soup.find_all('a', href=re.compile(r'https://www\.saatchiart\.com/en-br/account/artworks/\d+'))
            for link in full_links:
                all_links.append(link['href'])
            
            # Pattern 2: Relative links that might point to artworks
            relative_links = soup.find_all('a', href=re.compile(r'/en-br/account/artworks/\d+'))
            for link in relative_links:
                full_url = 'https://www.saatchiart.com' + link['href']
                all_links.append(full_url)
            
            # Pattern 3: Any links containing artwork patterns
            artwork_patterns = soup.find_all('a', href=re.compile(r'artworks/\d+'))
            for link in artwork_patterns:
                href = link['href']
                if href.startswith('/'):
                    href = 'https://www.saatchiart.com' + href
                if 'en-br' not in href and 'account/artworks' in href:
                    # Convert to the en-br version
                    href = href.replace('account/artworks', 'en-br/account/artworks')
                all_links.append(href)
            
            print(f"✅ Found {len([l for l in all_links if '1295487' in l])} links so far...")
            
        except Exception as e:
            print(f"❌ Error scraping {url}: {e}")
    
    # Clean up the links - ensure they all have the proper format
    cleaned_links = []
    for link in all_links:
        # Make sure it's the en-br version and a full URL
        if 'en-br/account/artworks' in link:
            if link.startswith('/'):
                link = 'https://www.saatchiart.com' + link
            cleaned_links.append(link)
    
    # Remove duplicates while preserving order
    unique_links = []
    for link in cleaned_links:
        if link not in unique_links:
            unique_links.append(link)
    
    return unique_links

# Let's run it!
print("🚀 Starting to scrape your friend's artwork links...\n")

artwork_links = scrape_artwork_links()

print(f"\n🎉 SCRAPING COMPLETE!")
print(f"📊 Total unique artwork links found: {len(artwork_links)}\n")

print("🔗 All artwork links:")
for i, link in enumerate(artwork_links, 1):
    print(f"{i:2d}. {link}")

# Save to a file
with open("artwork_links.txt", "w", encoding="utf-8") as f:
    for link in artwork_links:
        f.write(link + "\n")

print(f"\n💾 Links have been saved to 'artwork_links.txt'")