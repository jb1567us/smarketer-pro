#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WordPress Portfolio Generator (SaatchiArt) — corrected & hardened

Key fixes vs your original:
- Added a real fetch_page() to request HTML and build BeautifulSoup soup.
- Fixed extract_artwork_data() to accept (soup, url) and to be called correctly.
- Removed unsupported CSS ":contains()" selectors (not supported by bs4).
- Added JSON-LD parsing (application/ld+json) to robustly get title/artist/price/medium/dimensions when possible.
- Avoided ET.CDATA (not supported in xml.etree). We post-process with minidom to insert CDATA for content:encoded & excerpt:encoded.
- Added a minimal WordPress theme including header.php/footer.php to avoid get_header/get_footer errors.
- Removed reference to non-existent /css/custom.css in functions.php.
- Improved sanitize_filename, stable post_id assignment, and safer image-path building.
- Added simple politeness options and basic error handling.
- NOTE: Many SaatchiArt pages are rendered by JS. If requests can’t see the data, consider Playwright/Selenium.
"""
import requests
from bs4 import BeautifulSoup
import os
import time
from urllib.parse import urljoin, urlparse
import json
import re
from datetime import datetime
import csv
import xml.etree.ElementTree as ET
from xml.dom import minidom

WXR_NS = {
    "excerpt": "http://wordpress.org/export/1.2/excerpt/",
    "content": "http://purl.org/rss/1.0/modules/content/",
    "wfw": "http://wellformedweb.org/CommentAPI/",
    "dc": "http://purl.org/dc/elements/1.1/",
    "wp": "http://wordpress.org/export/1.2/",
}

class WordPressPortfolioGenerator:
    def __init__(self, delay_seconds=2.0, timeout=30):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        })
        self.artworks = []
        self.delay_seconds = delay_seconds
        self.timeout = timeout
        self.post_id_counter = 1

    def create_directory_structure(self):
        """Create directories for WordPress export"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.base_dir = f"wordpress_portfolio_{timestamp}"
        self.wp_content = os.path.join(self.base_dir, "wp-content")
        # Freeze upload year/month based on "now" at directory creation time
        self.upload_year = datetime.now().strftime("%Y")
        self.upload_month = datetime.now().strftime("%m")
        self.uploads_dir = os.path.join(self.wp_content, "uploads", self.upload_year, self.upload_month)
        self.export_dir = os.path.join(self.base_dir, "export")
        self.theme_dir = os.path.join(self.base_dir, "theme")

        for directory in [self.base_dir, self.wp_content, self.uploads_dir, self.export_dir, self.theme_dir]:
            os.makedirs(directory, exist_ok=True)

    # ------------------- Fetch + URL list -------------------
    def get_artwork_urls(self):
        """Return the list of artwork URLs (unchanged list from user's code)."""
        return [
            "https://www.saatchiart.com/art/Painting-Caviar/1295487/12292979/view",
            "https://www.saatchiart.com/art/Painting-Convergence/1295487/8754060/view",
            "https://www.saatchiart.com/art/Painting-Meeting-In-The-Middle/1295487/8754042/view",
            "https://www.saatchiart.com/art/Painting-Finger-Print/1295487/8754025/view",
            "https://www.saatchiart.com/art/Painting-Sheet-Music/1295487/8146759/view",
            "https://www.saatchiart.com/art/Painting-Puzzled/1295487/8146584/view",
            "https://www.saatchiart.com/art/Painting-Heart-Work/1295487/8146572/view",
            "https://www.saatchiart.com/art/Painting-Portal-2/1295487/8146546/view",
            "https://www.saatchiart.com/art/Painting-Portal-1/1295487/8146533/view",
            "https://www.saatchiart.com/art/Painting-Self-Portrait-1/1295487/8125469/view",
            "https://www.saatchiart.com/art/Painting-Morning-Joe/1295487/8125458/view",
            "https://www.saatchiart.com/art/Painting-Unity/1295487/8125409/view",
            "https://www.saatchiart.com/art/Painting-Dog-On-A-Bike/1295487/8125271/view",
            "https://www.saatchiart.com/art/Painting-Water-People/1295487/7363373/view",
            "https://www.saatchiart.com/art/Painting-Towers/1295487/7363345/view",
            "https://www.saatchiart.com/art/Painting-Granular/1295487/7363339/view",
            "https://www.saatchiart.com/art/Painting-Puzzle-2/1295487/7363331/view",
            "https://www.saatchiart.com/art/Painting-Puzzle-1/1295487/7363317/view",
            "https://www.saatchiart.com/art/Painting-Trichome/1295487/7363313/view",
            "https://www.saatchiart.com/art/Painting-Trichomes/1295487/7363299/view",
            "https://www.saatchiart.com/art/Painting-Grill/1295487/6783253/view",
            "https://www.saatchiart.com/art/Painting-Quilted/1295487/6783247/view",
            "https://www.saatchiart.com/art/Painting-Interactions/1295487/6783239/view",
            "https://www.saatchiart.com/art/Painting-Rush/1295487/6783231/view",
            "https://www.saatchiart.com/art/Painting-Yorkie/1295487/6783225/view",
            "https://www.saatchiart.com/art/Painting-Night-Sky/1295487/6783211/view",
            "https://www.saatchiart.com/art/Painting-Bold/1295487/6783203/view",
            "https://www.saatchiart.com/art/Painting-Climbing/1295487/6783197/view",
            "https://www.saatchiart.com/art/Painting-Dance/1295487/6783193/view",
            "https://www.saatchiart.com/art/Painting-Smoke/1295487/6783181/view",
            "https://www.saatchiart.com/art/Painting-Motion/1295487/6783137/view",
            "https://www.saatchiart.com/art/Painting-Listening/1295487/6783125/view",
            "https://www.saatchiart.com/art/Painting-Synapses/1295487/6783101/view",
            "https://www.saatchiart.com/art/Painting-Microscope-7/1295487/6782897/view",
            "https://www.saatchiart.com/art/Painting-Microscope-6/1295487/6782859/view",
            "https://www.saatchiart.com/art/Painting-Microscope-5/1295487/6782839/view",
            "https://www.saatchiart.com/art/Painting-Microscope-4/1295487/6782817/view",
            "https://www.saatchiart.com/art/Painting-Microscope-3/1295487/6782785/view",
            "https://www.saatchiart.com/art/Painting-Microscope-2/1295487/6782755/view",
            "https://www.saatchiart.com/art/Painting-Microscope-1/1295487/6782739/view",
            "https://www.saatchiart.com/art/Sculpture-Floating-6-Rabbit/1295487/6627463/view",
            "https://www.saatchiart.com/art/Sculpture-Floating-5-Moth/1295487/6627457/view",
            "https://www.saatchiart.com/art/Sculpture-Floating-4-Vines/1295487/6627447/view",
            "https://www.saatchiart.com/art/Sculpture-Floating-3-Tree/1295487/6627443/view",
            "https://www.saatchiart.com/art/Sculpture-Floating-2-Butterfly/1295487/6627437/view",
            "https://www.saatchiart.com/art/Sculpture-Floating-1-Cicada/1295487/6627409/view",
            "https://www.saatchiart.com/art/Collage-Purple-Night-Mulch-Series/1295487/6583797/view",
            "https://www.saatchiart.com/art/Collage-City-At-Night-Mulch-Series/1295487/6583787/view",
            "https://www.saatchiart.com/art/Collage-Purple-1-Mulch-Series/1295487/6583781/view",
            "https://www.saatchiart.com/art/Collage-Close-Up-Mulch-Series/1295487/6583777/view",
            "https://www.saatchiart.com/art/Collage-Society-Mulch-Series/1295487/6583753/view",
            "https://www.saatchiart.com/art/Collage-Pieces-Of-Red/1295487/6583729/view",
            "https://www.saatchiart.com/art/Collage-Red-And-Black-Mulch-Series/1295487/6583709/view",
            "https://www.saatchiart.com/art/Collage-Paper-Peace/1295487/6583693/view",
            "https://www.saatchiart.com/art/Collage-Honeycomb-Mulch-Series/1295487/6583683/view",
            "https://www.saatchiart.com/art/Collage-Wild-Zebra-2-Mulch-Series/1295487/6583651/view",
            "https://www.saatchiart.com/art/Collage-Wild-Zebra-1-Mulch-Series/1295487/6583633/view",
            "https://www.saatchiart.com/art/Collage-Work-Party-Mulch-Series/1295487/6583609/view",
            "https://www.saatchiart.com/art/Collage-Business-Mulch/1295487/6583595/view",
            "https://www.saatchiart.com/art/Collage-Office-Work-Mulch/1295487/6583581/view",
            "https://www.saatchiart.com/art/Sculpture-Jaguar/1295487/6513325/view",
            "https://www.saatchiart.com/art/Sculpture-Megapixels/1295487/6513307/view",
            "https://www.saatchiart.com/art/Sculpture-Oyster-Mushrooms/1295487/6513293/view",
            "https://www.saatchiart.com/art/Sculpture-Esm-S17/1295487/6513257/view",
            "https://www.saatchiart.com/art/Painting-Fire-Flow/1295487/6513221/view",
            "https://www.saatchiart.com/art/Painting-Owls-In-Fall/1295487/6513209/view",
            "https://www.saatchiart.com/art/Painting-Connectivity/1295487/6513163/view",
            "https://www.saatchiart.com/art/Painting-Atomic-Flow/1295487/6513149/view",
            "https://www.saatchiart.com/art/Painting-Trees/1295487/6513127/view",
            "https://www.saatchiart.com/art/Painting-Animal-Kingdom/1295487/6513109/view",
            "https://www.saatchiart.com/art/Painting-Clean-Hands/1295487/6513085/view",
            "https://www.saatchiart.com/art/Painting-Reflection/1295487/6513075/view",
            "https://www.saatchiart.com/art/Painting-Eggs-And-Eyes/1295487/6492629/view",
            "https://www.saatchiart.com/art/Painting-Moon-Dance/1295487/6492627/view",
            "https://www.saatchiart.com/art/Painting-Floating-Leaves/1295487/6492617/view",
            "https://www.saatchiart.com/art/Painting-Arrowheads/1295487/6492613/view",
            "https://www.saatchiart.com/art/Painting-Campground/1295487/6492597/view",
            "https://www.saatchiart.com/art/Painting-Puzzle/1295487/6492595/view",
            "https://www.saatchiart.com/art/Painting-Streams-And-Ponds/1295487/6492583/view",
            "https://www.saatchiart.com/art/Painting-Cluster-Of-Caps/1295487/6492577/view",
            "https://www.saatchiart.com/art/Painting-Duck-Pond/1295487/6492573/view",
            "https://www.saatchiart.com/art/Painting-Creek-Bottom/1295487/6492497/view",
            "https://www.saatchiart.com/art/Painting-Organic-Mushrooms/1295487/6492491/view",
            "https://www.saatchiart.com/art/Painting-Stones/1295487/6492487/view",
            "https://www.saatchiart.com/art/Painting-Cubes/1295487/6492481/view",
            "https://www.saatchiart.com/art/Painting-Seed-Pods/1295487/6492463/view",
            "https://www.saatchiart.com/art/Painting-Excited-Bird/1295487/6492447/view",
            "https://www.saatchiart.com/art/Painting-Mushroom-Exclamation/1295487/6492441/view",
            "https://www.saatchiart.com/art/Painting-Snake-And-Rocks/1295487/6492431/view",
            "https://www.saatchiart.com/art/Painting-Shapeshifter/1295487/6492415/view",
            "https://www.saatchiart.com/art/Painting-Coiled-Snake/1295487/6492413/view",
            "https://www.saatchiart.com/art/Painting-Avacado-Snack/1295487/6492407/view",
            "https://www.saatchiart.com/art/Painting-Gold-Shapes/1295487/6492375/view",
            "https://www.saatchiart.com/art/Painting-Musical-Embrace/1295487/6492355/view",
            "https://www.saatchiart.com/art/Painting-Organic-Food/1295487/6492337/view",
            "https://www.saatchiart.com/art/Painting-Snake-Eggs/1295487/6492325/view",
            "https://www.saatchiart.com/art/Painting-Brush-Strokes/1295487/6492323/view",
            "https://www.saatchiart.com/art/Painting-Blanket/1295487/6492319/view",
            "https://www.saatchiart.com/art/Painting-Dance/1295487/6492311/view",
            "https://www.saatchiart.com/art/Painting-Bloom/1295487/6492303/view",
            "https://www.saatchiart.com/art/Painting-Organic-Shapes/1295487/6492289/view",
            "https://www.saatchiart.com/art/Painting-Silver/1295487/6483881/view",
            "https://www.saatchiart.com/art/Painting-Fortune/1295487/6483865/view",
            "https://www.saatchiart.com/art/Painting-Transformation/1295487/6483815/view",
            "https://www.saatchiart.com/art/Painting-Golden-Nugget/1295487/6483777/view",
            "https://www.saatchiart.com/art/Painting-Golden-Rule/1295487/6483759/view",
            "https://www.saatchiart.com/art/Painting-Portal/1295487/6483753/view",
            "https://www.saatchiart.com/art/Painting-Feather-Trees/1295487/6447005/view",
            "https://www.saatchiart.com/art/Painting-Magic-Carpet/1295487/6446995/view",
            "https://www.saatchiart.com/art/Painting-Screen/1295487/6446983/view",
            "https://www.saatchiart.com/art/Painting-Spring-Blooms/1295487/6446977/view",
            "https://www.saatchiart.com/art/Painting-Celebrate/1295487/6446967/view",
            "https://www.saatchiart.com/art/Painting-Anemones/1295487/6446959/view",
            "https://www.saatchiart.com/art/Painting-Coral/1295487/6446941/view",
            "https://www.saatchiart.com/art/Painting-Existance/1295487/6446929/view",
            "https://www.saatchiart.com/art/Painting-Fireworks/1295487/6446913/view",
            "https://www.saatchiart.com/art/Painting-Synapse/1295487/6446909/view",
            "https://www.saatchiart.com/art/Painting-Stick-Men/1295487/6446901/view",
            "https://www.saatchiart.com/art/Painting-Descending/1295487/6446893/view",
            "https://www.saatchiart.com/art/Painting-Lifeforce/1295487/6446799/view",
            "https://www.saatchiart.com/art/Painting-Turquoise-And-Peppers/1295487/6446775/view",
            "https://www.saatchiart.com/art/Painting-Turquoise-Blend/1295487/6446755/view",
            "https://www.saatchiart.com/art/Painting-Turquoise-Stretch/1295487/6446705/view",
            "https://www.saatchiart.com/art/Painting-Turquoise-Circuit-Board/1295487/6446693/view",
            "https://www.saatchiart.com/art/Painting-Blast-Of-Blue-On-Red/1295487/6446665/view",
            "https://www.saatchiart.com/art/Painting-Blue-Gold/1295487/6446651/view",
            "https://www.saatchiart.com/art/Painting-Blue-Glacier/1295487/6446603/view",
            "https://www.saatchiart.com/art/Painting-Blue-Wave/1295487/6446583/view",
            "https://www.saatchiart.com/art/Painting-Blue-Mesh/1295487/6446557/view",
            "https://www.saatchiart.com/art/Painting-Cold-Blue/1295487/6446543/view",
            "https://www.saatchiart.com/art/Painting-Blue-Storm/1295487/6446503/view",
            "https://www.saatchiart.com/art/Printmaking-No-Public-Shrooms-Limited-Edition-Of-1/1295487/6444945/view",
            "https://www.saatchiart.com/art/Printmaking-No-Public-Shrooms-Limited-Edition-Of-1/1295487/6444917/view",
            "https://www.saatchiart.com/art/Printmaking-Start-Sign-Limited-Edition-Of-1/1295487/6444891/view",
            "https://www.saatchiart.com/art/Printmaking-Right-Way-Limited-Edition-Of-1/1295487/6444853/view",
            "https://www.saatchiart.com/art/Installation-No-Porking/1295487/6444805/view",
            "https://www.saatchiart.com/art/Painting-Gold-Series-006/1295487/6412863/view",
            "https://www.saatchiart.com/art/Painting-Gold-Series-005/1295487/6412831/view",
            "https://www.saatchiart.com/art/Painting-Gold-Series-004/1295487/6412815/view",
            "https://www.saatchiart.com/art/Painting-Gold-Series-003/1295487/6412813/view",
            "https://www.saatchiart.com/art/Painting-Gold-Series-002/1295487/6412799/view",
            "https://www.saatchiart.com/art/Painting-Gold-Series-001/1295487/6412791/view",
            "https://www.saatchiart.com/art/Painting-Waves/1295487/6364287/view"
        ]

    def fetch_page(self, url):
        """Fetch a page and return BeautifulSoup object (or None)."""
        try:
            resp = self.session.get(url, timeout=self.timeout)
            resp.raise_for_status()
            return BeautifulSoup(resp.text, "html.parser")
        except Exception as e:
            print(f"❌ Fetch failed: {url} ({e})")
            return None

    # ------------------- Extraction helpers -------------------
    def extract_artwork_data(self, soup, url):
        """Extract detailed artwork information from Saatchi Art page"""
        if soup is None:
            return None

        print(f"📄 Scraping: {url}")

        # Try JSON-LD first (often most reliable for title/artist/price/dimensions)
        ld = self.parse_json_ld(soup)

        data = {
            'url': url,
            'title': ld.get('name') or self.extract_text(soup, ['h1', '[data-testid*="title"]', '.artwork-title']) or "Untitled Artwork",
            'artist': ld.get('artist') or self.extract_text(soup, ['a[href*="/artist/"]', '.artist-name']) or "Unknown Artist",
            'price': ld.get('price') or self.extract_price(soup),
            'medium': ld.get('material') or self.extract_medium(soup),
            'dimensions': ld.get('dimensions') or self.extract_dimensions(soup),
            'description': ld.get('description') or self.extract_description(soup),
            'year_created': ld.get('year') or self.extract_year(soup),
            'subject': self.extract_subject(soup),
            'styles': self.extract_styles(soup),
            'rarity': self.extract_rarity(soup),
            'ready_to_hang': self.extract_ready_to_hang(soup),
            'framing': self.extract_framing(soup),
            'authenticity': self.extract_authenticity(soup),
            'packaging': self.extract_packaging(soup),
            'images': self.extract_images(soup),
            'scraped_at': datetime.now().isoformat()
        }
        return data

    def parse_json_ld(self, soup):
        """Parse application/ld+json for structured data if present."""
        out = {}
        try:
            for tag in soup.find_all("script", type="application/ld+json"):
                try:
                    obj = json.loads(tag.get_text(strip=True))
                except Exception:
                    continue

                # Handle either a dict or a list of dicts
                candidates = obj if isinstance(obj, list) else [obj]
                for item in candidates:
                    # Often @type Product/VisualArtwork
                    name = item.get("name")
                    description = item.get("description")
                    brand = item.get("brand", {})
                    if isinstance(brand, dict):
                        artist_name = brand.get("name")
                    else:
                        artist_name = None

                    # Offers / price
                    price = None
                    offers = item.get("offers")
                    if isinstance(offers, dict):
                        price = offers.get("priceCurrency", "") + " " + str(offers.get("price")) if offers.get("price") else None

                    # Material / medium and dimensions
                    material = item.get("material")
                    width = item.get("width", {})
                    height = item.get("height", {})
                    depth = item.get("depth", {})

                    def dim_to_text(d):
                        if isinstance(d, dict):
                            val = d.get("value")
                            unit = d.get("unitText") or d.get("unitCode") or ""
                            if val is not None:
                                return f"{val} {unit}".strip()
                        return None

                    dims = []
                    for d in (width, height, depth):
                        t = dim_to_text(d)
                        if t:
                            dims.append(t)
                    dimensions = " × ".join(dims) if dims else None

                    # Year (sometimes in productionDate or dateCreated)
                    year = None
                    for k in ("productionDate", "dateCreated"):
                        if item.get(k):
                            ymatch = re.search(r"\b(19|20)\d{2}\b", str(item.get(k)))
                            if ymatch:
                                year = ymatch.group(0)
                                break

                    # Populate if we have at least a name or description
                    if name or description:
                        out.setdefault("name", name)
                        out.setdefault("description", description)
                        out.setdefault("artist", artist_name)
                        out.setdefault("price", price)
                        out.setdefault("material", material)
                        out.setdefault("dimensions", dimensions)
                        out.setdefault("year", year)
        except Exception:
            pass
        return out

    def extract_price(self, soup):
        """Extract price information (fallback)."""
        # Try meta tags
        for prop in ("product:price:amount", "og:price:amount", "twitter:data1"):
            meta = soup.find("meta", attrs={"property": prop}) or soup.find("meta", attrs={"name": prop})
            if meta and meta.get("content"):
                return meta["content"]

        # Fallback: look for currency symbols in plain text
        text = soup.get_text(" ", strip=True)
        m = re.search(r"(\$|USD)\s?\d[\d,]*(\.\d{2})?", text)
        return m.group(0) if m else "Price not available"

    def extract_medium(self, soup):
        """Extract medium information (very heuristic)."""
        details = self.extract_details_section(soup)
        for line in details:
            if "medium" in line.lower():
                return line.split(":", 1)[1].strip() if ":" in line else line.strip()
        # Try to infer from description
        desc = self.extract_description(soup).lower()
        for kw in ["acrylic", "oil", "watercolor", "ink", "collage", "mixed media", "sculpture", "wood", "metal"]:
            if kw in desc:
                return kw.title()
        return "Medium not specified"

    def extract_dimensions(self, soup):
        """Extract dimensions (heuristic)."""
        text = soup.get_text(" ", strip=True)
        # Look for WxH or WxHxD patterns
        m = re.search(r"\d+\.?\d*\s*[×x]\s*\d+\.?\d*(?:\s*[×x]\s*\d+\.?\d*)?\s*(in|cm)\b", text, re.I)
        if m:
            return m.group(0)
        # Try separate width/height if present
        m2 = re.search(r"(width|w)\s*[:\-]?\s*\d+\.?\d*\s*(cm|in).*(height|h)\s*[:\-]?\s*\d+\.?\d*\s*(cm|in)", text, re.I)
        if m2:
            return m2.group(0)
        return "Dimensions not specified"

    def extract_description(self, soup):
        """Extract artwork description."""
        # Try common containers
        candidates = [
            {"name": "div", "attrs": {"data-testid": "artwork-description"}},
            {"name": "div", "class_": "artwork-description"},
            {"name": "section", "class_": re.compile("description", re.I)},
        ]
        for c in candidates:
            el = soup.find(c.get("name"), attrs=c.get("attrs")) or soup.find(c.get("name"), class_=c.get("class_"))
            if el:
                txt = el.get_text(" ", strip=True)
                if txt:
                    return txt

        # Fallback to meta description
        meta = soup.find("meta", attrs={"name": "description"})
        if meta and meta.get("content"):
            return meta["content"]
        return "No description available"

    def extract_year(self, soup):
        """Extract year created (heuristic)."""
        text = soup.get_text(" ", strip=True)
        m = re.search(r"(year\s*created|created)\s*[:\-]?\s*(\b(19|20)\d{2}\b)", text, re.I)
        return m.group(2) if m else "Year not specified"

    def extract_subject(self, soup):
        text = soup.get_text(" ", strip=True)
        m = re.search(r"Subject\s*[:\-]?\s*(.+?)(?:\s{2,}|$)", text, re.I)
        return m.group(1).strip() if m else "Subject not specified"

    def extract_styles(self, soup):
        text = soup.get_text(" ", strip=True)
        m = re.search(r"Styles\s*[:\-]?\s*(.+?)(?:\s{2,}|$)", text, re.I)
        return m.group(1).strip() if m else "Styles not specified"

    def extract_rarity(self, soup):
        text = soup.get_text(" ", strip=True)
        m = re.search(r"Rarity\s*[:\-]?\s*(.+?)(?:\s{2,}|$)", text, re.I)
        return m.group(1).strip() if m else "Rarity not specified"

    def extract_ready_to_hang(self, soup):
        text = soup.get_text(" ", strip=True)
        m = re.search(r"Ready\s*To\s*Hang\s*[:\-]?\s*(.+?)(?:\s{2,}|$)", text, re.I)
        return m.group(1).strip() if m else "Not specified"

    def extract_framing(self, soup):
        text = soup.get_text(" ", strip=True)
        m = re.search(r"(Frame|Framing)\s*[:\-]?\s*(.+?)(?:\s{2,}|$)", text, re.I)
        return (m.group(2) if m and m.lastindex and m.lastindex >= 2 else m.group(1)).strip() if m else "Not specified"

    def extract_authenticity(self, soup):
        text = soup.get_text(" ", strip=True)
        m = re.search(r"Authenticity\s*[:\-]?\s*(.+?)(?:\s{2,}|$)", text, re.I)
        return m.group(1).strip() if m else "Not specified"

    def extract_packaging(self, soup):
        text = soup.get_text(" ", strip=True)
        m = re.search(r"Packaging\s*[:\-]?\s*(.+?)(?:\s{2,}|$)", text, re.I)
        return m.group(1).strip() if m else "Not specified"

    def extract_details_section(self, soup):
        """Extract text lines from a likely 'details' area (best-effort)."""
        candidates = []
        for sel in [
            ("div", {"data-testid": re.compile("detail", re.I)}),
            ("section", {"class": re.compile("detail", re.I)}),
            ("div", {"class": re.compile("artwork-details|details-section", re.I)}),
        ]:
            el = soup.find(sel[0], attrs=sel[1])
            if el:
                candidates.append(el.get_text("\n"))

        for block in candidates:
            lines = [ln.strip() for ln in block.split("\n") if ln.strip()]
            if lines:
                return lines
        return []

    def extract_text(self, soup, selectors):
        """Extract text using multiple simple selectors (no :contains)."""
        for selector in selectors:
            try:
                for el in soup.select(selector):
                    txt = el.get_text(" ", strip=True)
                    if txt:
                        return txt
            except Exception:
                continue
        return ""

    def extract_images(self, soup):
        """Extract image URLs (og:image, twitter:image, and in-page <img>)."""
        images = set()
        for meta in soup.find_all('meta', attrs={'property': ['og:image', 'twitter:image']}):
            if meta.get('content'):
                images.add(meta['content'])
        for meta in soup.find_all('meta', attrs={'name': ['og:image', 'twitter:image']}):
            if meta.get('content'):
                images.add(meta['content'])
        for img in soup.find_all('img'):
            for attr in ['src', 'data-src', 'data-large', 'data-original']:
                val = img.get(attr)
                if val and any(x in val.lower() for x in ['.jpg', '.jpeg', '.png', '.webp']):
                    images.add(val)
        return list(images)

    def download_images(self, artwork):
        """Download images for an artwork (limit to first 5)."""
        image_paths = []
        for i, img_url in enumerate(artwork['images'][:5]):
            try:
                if img_url.startswith('//'):
                    img_url = 'https:' + img_url
                # make absolute if needed (not always possible without base url, so skip)
                # Just fetch the url as-is
                r = self.session.get(img_url, stream=True, timeout=self.timeout)
                r.raise_for_status()
                ext = os.path.splitext(urlparse(img_url).path)[1] or '.jpg'
                filename = f"{self.sanitize_filename(artwork['title'])}_{i}{ext}"
                filepath = os.path.join(self.uploads_dir, filename)
                with open(filepath, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
                image_paths.append({
                    'url': f"/wp-content/uploads/{self.upload_year}/{self.upload_month}/{filename}",
                    'filepath': filepath,
                    'filename': filename
                })
                print(f"✅ Downloaded: {filename}")
            except Exception as e:
                print(f"❌ Failed to download image: {e}")
        return image_paths

    def sanitize_filename(self, filename):
        """Sanitize filename for WordPress slugs/files."""
        # Lowercase, replace spaces with dashes, strip bad chars
        slug = re.sub(r'\s+', '-', filename.strip().lower())
        slug = re.sub(r'[^a-z0-9\-_.]', '', slug)
        return slug.strip('-_.') or "artwork"

    # ------------------- WordPress export -------------------
    def generate_wordpress_xml(self):
        """Generate WordPress WXR export file with detailed artwork information"""
        ET.register_namespace("excerpt", WXR_NS["excerpt"])
        ET.register_namespace("content", WXR_NS["content"])
        ET.register_namespace("wfw", WXR_NS["wfw"])
        ET.register_namespace("dc", WXR_NS["dc"])
        ET.register_namespace("wp", WXR_NS["wp"])

        root = ET.Element("rss", version="2.0")
        for prefix, uri in WXR_NS.items():
            root.set(f"xmlns:{prefix}", uri)

        channel = ET.SubElement(root, "channel")
        ET.SubElement(channel, "title").text = "Art Portfolio"
        ET.SubElement(channel, "link").text = "https://yourportfolio.com"
        ET.SubElement(channel, "description").text = "Artwork Portfolio"
        ET.SubElement(channel, "language").text = "en-US"

        # Terms (basic categories)
        terms = self.generate_terms()
        for term in terms:
            channel.append(term)

        # Posts
        for artwork in self.artworks:
            if artwork.get('images'):
                post = self.create_post_element(artwork)
                channel.append(post)

        xml_str = ET.tostring(root, encoding='utf-8')
        # Pretty + add CDATA for content and excerpt
        doc = minidom.parseString(xml_str)

        # Wrap content:encoded and excerpt:encoded in CDATA
        def wrap_cdata(tag_name):
            for node in doc.getElementsByTagName(tag_name):
                if node.firstChild:
                    text = node.firstChild.data
                    # Replace child with CDATA
                    while node.firstChild:
                        node.removeChild(node.firstChild)
                    cdata = doc.createCDATASection(text)
                    node.appendChild(cdata)

        wrap_cdata("content:encoded")
        wrap_cdata("excerpt:encoded")

        pretty_xml = doc.toprettyxml(indent="  ", encoding="utf-8")

        xml_path = os.path.join(self.export_dir, "portfolio-export.xml")
        with open(xml_path, 'wb') as f:
            f.write(pretty_xml)

        print(f"✅ WordPress export file created: {xml_path}")

    def create_post_element(self, artwork):
        """Create WordPress post element with detailed artwork information"""
        post = ET.Element("item")

        ET.SubElement(post, "title").text = artwork['title']
        ET.SubElement(post, "link").text = f"https://yourportfolio.com/artwork/{self.sanitize_filename(artwork['title'])}"
        ET.SubElement(post, "pubDate").text = datetime.now().strftime("%a, %d %b %Y %H:%M:%S +0000")
        ET.SubElement(post, "{%s}creator" % WXR_NS["dc"]).text = "admin"

        # Content + Excerpt
        content_el = ET.SubElement(post, "{%s}encoded" % WXR_NS["content"])
        content_el.text = self.generate_wordpress_content(artwork)
        excerpt_el = ET.SubElement(post, "{%s}encoded" % WXR_NS["excerpt"])
        excerpt_el.text = (artwork['description'][:200] + "...") if artwork['description'] and len(artwork['description']) > 200 else (artwork['description'] or "")

        # Post meta for custom fields
        self.add_custom_fields(post, artwork)

        # Post info
        ET.SubElement(post, "{%s}post_id" % WXR_NS["wp"]).text = str(self.post_id_counter); self.post_id_counter += 1
        ET.SubElement(post, "{%s}post_date" % WXR_NS["wp"]).text = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ET.SubElement(post, "{%s}post_type" % WXR_NS["wp"]).text = "post"
        ET.SubElement(post, "{%s}status" % WXR_NS["wp"]).text = "publish"
        ET.SubElement(post, "{%s}post_parent" % WXR_NS["wp"]).text = "0"
        ET.SubElement(post, "{%s}menu_order" % WXR_NS["wp"]).text = "0"

        # Category based on medium
        category = self.determine_category(artwork['medium'])
        cat_elem = ET.SubElement(post, "category", attrib={"domain": "category", "nicename": category.lower()})
        cat_elem.append(ET.Comment("Category term"))
        cat_elem.text = category

        return post

    def generate_wordpress_content(self, artwork):
        """Generate WordPress-formatted content with artwork details"""
        parts = []
        parts.append(f"<h2>{self.html_escape(artwork['title'])}</h2>")
        parts.append(f"<p><strong>Artist:</strong> {self.html_escape(artwork['artist'])}</p>")
        parts.append(f"<p><strong>Price:</strong> {self.html_escape(artwork['price'])}</p>")
        parts.append(f"<p><strong>Medium:</strong> {self.html_escape(artwork['medium'])}</p>")
        parts.append(f"<p><strong>Dimensions:</strong> {self.html_escape(artwork['dimensions'])}</p>")
        parts.append("<h3>About the Artwork</h3>")
        parts.append(f"<p>{self.html_escape(artwork['description'])}</p>")
        parts.append("<h3>Details</h3>")
        details = [
            ("Year Created", artwork['year_created']),
            ("Subject", artwork['subject']),
            ("Styles", artwork['styles']),
            ("Rarity", artwork['rarity']),
            ("Ready to Hang", artwork['ready_to_hang']),
            ("Framing", artwork['framing']),
            ("Authenticity", artwork['authenticity']),
            ("Packaging", artwork['packaging']),
        ]
        parts.append("<ul>")
        for label, value in details:
            parts.append(f"<li><strong>{self.html_escape(label)}:</strong> {self.html_escape(value)}</li>")
        parts.append("</ul>")

        # Add images
        for img in artwork.get('wordpress_images', []):
            parts.append(f'<p><img src="{self.html_escape(img["url"])}" alt="{self.html_escape(artwork["title"])}" style="max-width:100%;height:auto;margin:20px 0;" /></p>')

        return "\n".join(parts)

    def html_escape(self, s):
        if s is None:
            return ""
        return (
            str(s)
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
        )

    def add_custom_fields(self, post, artwork):
        """Add custom fields for artwork metadata"""
        custom_fields = {
            'artwork_price': artwork['price'],
            'artwork_medium': artwork['medium'],
            'artwork_dimensions': artwork['dimensions'],
            'artwork_year': artwork['year_created'],
            'artwork_subject': artwork['subject'],
            'artwork_styles': artwork['styles'],
            'artwork_rarity': artwork['rarity'],
            'artwork_ready_to_hang': artwork['ready_to_hang'],
            'artwork_framing': artwork['framing'],
            'artwork_authenticity': artwork['authenticity'],
            'artwork_packaging': artwork['packaging']
        }
        for key, value in custom_fields.items():
            pm = ET.SubElement(post, "{%s}postmeta" % WXR_NS["wp"])
            ET.SubElement(pm, "{%s}meta_key" % WXR_NS["wp"]).text = key
            ET.SubElement(pm, "{%s}meta_value" % WXR_NS["wp"]).text = str(value or "")

    def determine_category(self, medium):
        """Determine category based on medium"""
        medium_lower = (medium or "").lower()
        if any(x in medium_lower for x in ['painting', 'ink', 'acrylic', 'oil', 'watercolor']):
            return "Painting"
        elif any(x in medium_lower for x in ['sculpture', '3d', 'wood', 'metal']):
            return "Sculpture"
        elif any(x in medium_lower for x in ['print', 'edition']):
            return "Printmaking"
        elif 'collage' in medium_lower:
            return "Collage"
        elif 'installation' in medium_lower:
            return "Installation"
        else:
            return "Artwork"

    def generate_terms(self):
        """Generate categories for WordPress"""
        terms = []
        categories = ['Painting', 'Sculpture', 'Collage', 'Printmaking', 'Installation', 'Artwork']
        tid = 1
        for cat in categories:
            term = ET.Element("{%s}term" % WXR_NS["wp"])
            ET.SubElement(term, "{%s}term_id" % WXR_NS["wp"]).text = str(tid); tid += 1
            ET.SubElement(term, "{%s}term_taxonomy" % WXR_NS["wp"]).text = "category"
            ET.SubElement(term, "{%s}term_slug" % WXR_NS["wp"]).text = cat.lower()
            ET.SubElement(term, "{%s}term_parent" % WXR_NS["wp"]).text = ""
            ET.SubElement(term, "{%s}term_name" % WXR_NS["wp"]).text = cat
            terms.append(term)
        return terms

    def generate_csv_export(self):
        """Generate CSV file with all artwork data"""
        csv_path = os.path.join(self.export_dir, "artwork-data.csv")
        with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = [
                'Title', 'Artist', 'Price', 'Medium', 'Dimensions', 'Description',
                'Year_Created', 'Subject', 'Styles', 'Rarity', 'Ready_To_Hang',
                'Framing', 'Authenticity', 'Packaging', 'URL'
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for art in self.artworks:
                writer.writerow({
                    'Title': art['title'],
                    'Artist': art['artist'],
                    'Price': art['price'],
                    'Medium': art['medium'],
                    'Dimensions': art['dimensions'],
                    'Description': art['description'],
                    'Year_Created': art['year_created'],
                    'Subject': art['subject'],
                    'Styles': art['styles'],
                    'Rarity': art['rarity'],
                    'Ready_To_Hang': art['ready_to_hang'],
                    'Framing': art['framing'],
                    'Authenticity': art['authenticity'],
                    'Packaging': art['packaging'],
                    'URL': art['url']
                })
        print(f"✅ CSV export created: {csv_path}")

    def generate_theme_files(self):
        """Generate WordPress theme files optimized for artwork display"""
        # style.css
        style_content = """
/*
Theme Name: Art Portfolio
Theme URI: https://yourportfolio.com
Author: Your Name
Description: Custom theme for art portfolio with detailed artwork display
Version: 1.0
*/

/* Basic reset */
* { box-sizing: border-box; }

/* Artwork Grid Layout */
.artwork-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 2rem;
  padding: 2rem;
  max-width: 1400px;
  margin: 0 auto;
}

.artwork-item {
  background: #fff;
  padding: 1.5rem;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.1);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}
.artwork-item:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 30px rgba(0,0,0,0.15);
}

.artwork-item img {
  width: 100%;
  height: 300px;
  object-fit: cover;
  border-radius: 8px;
  margin-bottom: 1rem;
}

.artwork-title {
  font-size: 1.4rem;
  font-weight: 600;
  margin: 0 0 0.5rem 0;
  color: #2c3e50;
}

.artwork-price {
  font-size: 1.2rem;
  font-weight: 700;
  color: #e74c3c;
  margin: 0 0 0.5rem 0;
}

.artwork-medium { color: #7f8c8d; margin: 0 0 0.5rem 0; font-style: italic; }
.artwork-dimensions { color: #95a5a6; margin: 0 0 1rem 0; }

/* Single Artwork Page */
.artwork-detail {
  max-width: 1200px;
  margin: 2rem auto;
  padding: 2rem;
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.1);
}

.artwork-gallery { margin-bottom: 2rem; }
.artwork-gallery img { max-width: 100%; height: auto; border-radius: 8px; margin-bottom: 1rem; }

.artwork-info { margin-bottom: 2rem; }

.artwork-details-list { list-style: none; padding: 0; }
.artwork-details-list li { padding: 0.5rem 0; border-bottom: 1px solid #ecf0f1; }
.artwork-details-list li:last-child { border-bottom: none; }

.detail-label { font-weight: 600; color: #2c3e50; display: inline-block; width: 140px; }

/* Header/Footer */
.site-header, .site-footer { padding: 1rem 2rem; background: #fafafa; border-bottom: 1px solid #eee; }
.site-footer { border-top: 1px solid #eee; border-bottom: 0; text-align: center; color: #666; }

/* Responsive Design */
@media (max-width: 768px) {
  .artwork-grid { grid-template-columns: 1fr; padding: 1rem; }
  .artwork-detail { padding: 1rem; margin: 1rem; }
}
        """.strip()

        functions_content = """
<?php
function art_portfolio_setup() {
  add_theme_support('post-thumbnails');
  add_theme_support('title-tag');
  add_theme_support('html5', array('search-form','gallery','caption'));
  add_image_size('artwork-thumbnail', 400, 300, true);
  add_image_size('artwork-large', 1200, 800, false);
}
add_action('after_setup_theme', 'art_portfolio_setup');

function art_portfolio_scripts() {
  wp_enqueue_style('art-portfolio-style', get_stylesheet_uri());
}
add_action('wp_enqueue_scripts', 'art_portfolio_scripts');
?>
        """.strip()

        header_php = """
<!doctype html>
<html <?php language_attributes(); ?>>
<head>
  <meta charset="<?php bloginfo('charset'); ?>">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <?php wp_head(); ?>
</head>
<body <?php body_class(); ?>>
<header class="site-header">
  <h1><a href="<?php echo esc_url(home_url('/')); ?>" style="text-decoration:none;color:#333;"><?php bloginfo('name'); ?></a></h1>
  <p style="margin:0;color:#666;"><?php bloginfo('description'); ?></p>
</header>
<main class="site-main">
        """.strip()

        footer_php = """
</main>
<footer class="site-footer">
  <p>&copy; <?php echo date('Y'); ?> Art Portfolio</p>
</footer>
<?php wp_footer(); ?>
</body>
</html>
        """.strip()

        single_php = """
<?php get_header(); ?>
<div class="artwork-detail">
  <?php if (have_posts()) : while (have_posts()) : the_post(); ?>
    <article id="post-<?php the_ID(); ?>" <?php post_class(); ?>>
      <div class="artwork-gallery">
        <?php if (has_post_thumbnail()) : the_post_thumbnail('artwork-large'); endif; ?>
      </div>
      <div class="artwork-info">
        <h1 class="artwork-title"><?php the_title(); ?></h1>
        <div class="artwork-price"><?php echo esc_html(get_post_meta(get_the_ID(), 'artwork_price', true)); ?></div>
        <div class="artwork-medium"><?php echo esc_html(get_post_meta(get_the_ID(), 'artwork_medium', true)); ?></div>
        <div class="artwork-dimensions"><?php echo esc_html(get_post_meta(get_the_ID(), 'artwork_dimensions', true)); ?></div>
        <div class="entry-content"><?php the_content(); ?></div>
        <h3>Artwork Details</h3>
        <ul class="artwork-details-list">
          <li><span class="detail-label">Year Created:</span> <?php echo esc_html(get_post_meta(get_the_ID(), 'artwork_year', true)); ?></li>
          <li><span class="detail-label">Subject:</span> <?php echo esc_html(get_post_meta(get_the_ID(), 'artwork_subject', true)); ?></li>
          <li><span class="detail-label">Styles:</span> <?php echo esc_html(get_post_meta(get_the_ID(), 'artwork_styles', true)); ?></li>
          <li><span class="detail-label">Rarity:</span> <?php echo esc_html(get_post_meta(get_the_ID(), 'artwork_rarity', true)); ?></li>
          <li><span class="detail-label">Ready to Hang:</span> <?php echo esc_html(get_post_meta(get_the_ID(), 'artwork_ready_to_hang', true)); ?></li>
          <li><span class="detail-label">Framing:</span> <?php echo esc_html(get_post_meta(get_the_ID(), 'artwork_framing', true)); ?></li>
          <li><span class="detail-label">Authenticity:</span> <?php echo esc_html(get_post_meta(get_the_ID(), 'artwork_authenticity', true)); ?></li>
          <li><span class="detail-label">Packaging:</span> <?php echo esc_html(get_post_meta(get_the_ID(), 'artwork_packaging', true)); ?></li>
        </ul>
      </div>
    </article>
  <?php endwhile; endif; ?>
</div>
<?php get_footer(); ?>
        """.strip()

        index_php = """
<?php get_header(); ?>
<div class="artwork-grid">
  <?php if (have_posts()) : while (have_posts()) : the_post(); ?>
    <article class="artwork-item">
      <a href="<?php the_permalink(); ?>">
        <?php if (has_post_thumbnail()) : the_post_thumbnail('artwork-thumbnail'); endif; ?>
        <h2 class="artwork-title"><?php the_title(); ?></h2>
        <div class="artwork-price"><?php echo esc_html(get_post_meta(get_the_ID(), 'artwork_price', true)); ?></div>
        <div class="artwork-medium"><?php echo esc_html(get_post_meta(get_the_ID(), 'artwork_medium', true)); ?></div>
        <div class="artwork-dimensions"><?php echo esc_html(get_post_meta(get_the_ID(), 'artwork_dimensions', true)); ?></div>
      </a>
    </article>
  <?php endwhile; endif; ?>
</div>
<?php get_footer(); ?>
        """.strip()

        with open(os.path.join(self.theme_dir, "style.css"), 'w', encoding='utf-8') as f:
            f.write(style_content)
        with open(os.path.join(self.theme_dir, "functions.php"), 'w', encoding='utf-8') as f:
            f.write(functions_content)
        with open(os.path.join(self.theme_dir, "header.php"), 'w', encoding='utf-8') as f:
            f.write(header_php)
        with open(os.path.join(self.theme_dir, "footer.php"), 'w', encoding='utf-8') as f:
            f.write(footer_php)
        with open(os.path.join(self.theme_dir, "single.php"), 'w', encoding='utf-8') as f:
            f.write(single_php)
        with open(os.path.join(self.theme_dir, "index.php"), 'w', encoding='utf-8') as f:
            f.write(index_php)

        print(f"✅ Theme files created in: {self.theme_dir}")

    def generate_import_instructions(self):
        """Generate detailed import instructions"""
        instructions = f"""
# WordPress Portfolio Import Instructions

## Files Generated
1. `export/portfolio-export.xml` — WXR file with posts & metadata
2. `export/artwork-data.csv` — CSV backup
3. `wp-content/uploads/{self.upload_year}/{self.upload_month}/` — downloaded images (if any)
4. `theme/` — custom WordPress theme with header/footer/index/single

## Import Steps
1) Install WordPress (local or server).
2) Upload the **theme**:
   - Zip the `theme/` folder and upload via Appearance → Themes → Add New → Upload.
   - Activate **Art Portfolio**.
3) Import content:
   - Tools → Import → WordPress → install the importer if needed.
   - Import `export/portfolio-export.xml`.
   - Check “Download and import file attachments”.
   - Assign posts to your user.
4) Images
   - If some images don’t import automatically (common when using local paths), copy the `wp-content/uploads/` folder from this bundle into your site’s `/wp-content/uploads/` directory.
5) Permalinks: Settings → Permalinks → “Post name” → Save.

## Notes
- SaatchiArt pages often render details via JavaScript; `requests` may not see everything. If some fields are empty, consider swapping the fetch to **Playwright** or **Selenium** to render JS, or add an API/CSV seed.
- Be mindful of SaatchiArt’s Terms of Service and robots.txt when scraping.
- To add e‑commerce later, install WooCommerce and map custom fields.

## Troubleshooting
- **Theme errors like `get_header()`**: This bundle includes `header.php` and `footer.php`. Make sure the theme is active.
- **Missing images**: Verify the uploads path and file permissions. Then regenerate thumbnails (e.g., via “Regenerate Thumbnails” plugin).
- **Import timeouts**: Split the WXR into smaller files, or increase PHP limits.
"""
        with open(os.path.join(self.base_dir, "IMPORT_INSTRUCTIONS.md"), 'w', encoding='utf-8') as f:
            f.write(instructions)
        print("✅ Import instructions created")

    def run(self):
        """Main function to generate WordPress portfolio"""
        print("🚀 Generating WordPress Portfolio...")
        self.create_directory_structure()

        artwork_urls = self.get_artwork_urls()
        total = len(artwork_urls)
        print(f"🎨 Processing {total} artworks...")

        for i, url in enumerate(artwork_urls, 1):
            print(f"\n📄 Processing {i}/{total}: {url}")
            soup = self.fetch_page(url)
            data = self.extract_artwork_data(soup, url)
            if data:
                # Download images
                image_paths = self.download_images(data)
                data['wordpress_images'] = image_paths
                self.artworks.append(data)
                print(f"✅ Added: {data['title']}")
            time.sleep(self.delay_seconds)

        print("\n🛠️  Generating WordPress export files...")
        self.generate_wordpress_xml()
        self.generate_csv_export()
        self.generate_theme_files()
        self.generate_import_instructions()

        print("\n🎉 WordPress Portfolio Generation Complete!")
        print(f"📁 Output directory: {self.base_dir}")
        print(f"🖼️  Artworks processed: {len(self.artworks)}")
        print(f"📄 Export file: {self.export_dir}/portfolio-export.xml")
        print(f"🎨 Theme files: {self.theme_dir}/")
        print(f"📖 Instructions: {self.base_dir}/IMPORT_INSTRUCTIONS.md")

def main():
    try:
        generator = WordPressPortfolioGenerator()
        # Comment the next line if you only want to build the theme/structure without scraping
        generator.run()
    except KeyboardInterrupt:
        print("\n⏹️  Process interrupted by user")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
