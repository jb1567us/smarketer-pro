from bs4 import BeautifulSoup
from typing import Dict, Optional

def parse_list_item(html_snippet: str) -> Dict[str, str]:
    """
    Parses a single Google Maps List View item (HTML snippet).
    Returns basic business info.
    """
    soup = BeautifulSoup(html_snippet, 'html.parser')
    
    # 1. Title & Link
    link_el = soup.find('a')
    href = link_el.get('href') if link_el else ""
    
    # Aria-label or inner text for Title
    title = link_el.get('aria-label') if link_el else None
    if not title:
        # Fallback to fontHeadlineSmall class (common in Maps)
        headline = soup.select_one('.fontHeadlineSmall')
        title = headline.get_text(strip=True) if headline else ""

    # 2. Website
    # Look for data-value="Website" button
    web_btn = soup.select_one('[data-value="Website"]')
    website = web_btn.get("href") if web_btn else ""

    return {
        "business_name": title,
        "maps_url": href,
        "website": website
    }

def parse_detail_page(html_content: str) -> Dict[str, str]:
    """
    Parses a Google Maps Detail Page (Full HTML).
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Title (h1)
    h1 = soup.find('h1')
    title = h1.get_text(strip=True) if h1 else ""
    
    # Website
    # Often in 'a[data-item-id="authority"]'
    web_btn = soup.select_one('a[data-item-id="authority"]')
    website = web_btn.get("href") if web_btn else ""
    
    # Phone
    # Often in 'button[data-item-id^="phone:"]'
    phone_btn = soup.select_one('button[data-item-id^="phone:"]')
    phone = phone_btn.get("aria-label") if phone_btn else ""
    
    if phone and phone.lower().startswith("phone:"):
        phone = phone.split(":", 1)[1].strip()

    return {
        "business_name": title,
        "website": website,
        "phone": phone
    }
