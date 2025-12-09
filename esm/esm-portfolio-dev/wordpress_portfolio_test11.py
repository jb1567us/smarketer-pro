import requests
from bs4 import BeautifulSoup
import os
import time
from urllib.parse import urljoin, urlparse
import json
import re
from datetime import datetime
import csv
from lxml import etree as ET
from lxml.etree import CDATA


class WordPressPortfolioGenerator:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            }
        )
        self.artworks = []
        self.base_url = "https://lookoverhere.xyz/esm"
        self.artist_info = {
            "name": "Elliot Spencer Morgan",
            "bio": "Elliot Spencer Morgan is a contemporary artist working across multiple mediums including painting, sculpture, collage, and installation. Their work explores the intersection of organic forms and structured compositions.",
            "statement": "My work is an exploration of the relationship between natural forms and constructed environments, blending organic shapes with geometric precision to create visual dialogues about our place in the modern world."
        }
        self.categories = set()

    def create_directory_structure(self):
        """Create directories for WordPress export"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.base_dir = f"wordpress_portfolio_{timestamp}"
        self.wp_content = os.path.join(self.base_dir, "wp-content")
        self.uploads_dir = os.path.join(
            self.wp_content,
            "uploads",
            datetime.now().strftime("%Y"),
            datetime.now().strftime("%m"),
        )
        self.export_dir = os.path.join(self.base_dir, "export")
        self.theme_dir = os.path.join(self.base_dir, "theme", "esm-portfolio")

        for directory in [
            self.base_dir,
            self.wp_content,
            self.uploads_dir,
            self.export_dir,
            self.theme_dir,
        ]:
            os.makedirs(directory, exist_ok=True)

    def get_artwork_urls(self):
        """Return the list of artwork URLs (first 4 for testing)"""
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

    def extract_artwork_data(self, url):
        """Extract minimal artwork information from Saatchi Art page"""
        try:
            print(f"📄 Scraping: {url}")
            response = self.session.get(url, timeout=30)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, "html.parser")

            # Extract title
            title = self.extract_title(soup, url)
            
            # Extract main image
            main_image = self.extract_main_image(soup)
            
            # Determine category from URL or content
            category = self.determine_category_from_url(url)
            
            # Add category to our set
            self.categories.add(category)

            data = {
                "url": url,
                "title": title or "Untitled Artwork",
                "category": category,
                "main_image": main_image,
                "scraped_at": datetime.now().isoformat(),
            }

            print(f"📝 Extracted: {data['title']} - Category: {data['category']}")
            return data

        except Exception as e:
            print(f"❌ Error scraping {url}: {e}")
            return None

    def extract_title(self, soup, url):
        """Extract title using multiple strategies"""
        title_selectors = [
            'h1[data-testid="artwork-title"]',
            "h1.artwork-title",
            "h1",
            "title",
            '[class*="title"] h1',
            ".ArtworkTitle",
            '[data-testid*="title"]',
        ]

        for selector in title_selectors:
            title = self.extract_text(soup, [selector])
            if title and title.strip() and title != "Saatchi Art":
                return title.strip()

        meta_selectors = [
            'meta[property="og:title"]',
            'meta[name="twitter:title"]',
        ]

        for selector in meta_selectors:
            meta = soup.select_one(selector)
            if meta and meta.get("content"):
                title = meta["content"]
                if title and title.strip() and title != "Saatchi Art":
                    return title.strip()

        url_path = urlparse(url).path
        path_parts = [part for part in url_path.split("/") if part and part not in ["art", "view"]]
        if len(path_parts) >= 2:
            potential_title = path_parts[1].replace("-", " ").title()
            return potential_title

        return "Untitled Artwork"

    def extract_text(self, soup, selectors):
        """Extract text using multiple selectors"""
        for selector in selectors:
            try:
                elem = soup.select_one(selector)
                if elem and elem.get_text(strip=True):
                    return elem.get_text(strip=True)
            except:
                continue
        return ""

    def extract_main_image(self, soup):
        """Extract the main high-quality image"""
        for meta in soup.find_all("meta", property=["og:image", "twitter:image"]):
            if meta.get("content"):
                img_url = meta["content"]
                if any(ext in img_url for ext in [".jpg", ".jpeg", ".png", ".webp"]):
                    return img_url

        img_selectors = [
            'img[data-testid="artwork-image"]',
            '.artwork-image',
            '.main-image',
            'img[class*="artwork"]',
            'img[src*="cloudfront.net"]',
        ]

        for selector in img_selectors:
            try:
                img = soup.select_one(selector)
                if img and (img.get("src") or img.get("data-src")):
                    img_url = img.get("data-src") or img.get("src")
                    if any(ext in img_url for ext in [".jpg", ".jpeg", ".png", ".webp"]):
                        return img_url
            except:
                continue

        for img in soup.find_all("img", src=True):
            src = img.get("src", "")
            if any(ext in src for ext in [".jpg", ".jpeg", ".png", ".webp"]):
                if "cloudfront.net" in src or "saatchiart" in src:
                    return src

        return None

    def determine_category_from_url(self, url):
        """Determine category based on URL path"""
        url_lower = url.lower()
        if "painting" in url_lower:
            return "Painting"
        elif "sculpture" in url_lower:
            return "Sculpture"
        elif "collage" in url_lower:
            return "Collage"
        elif "printmaking" in url_lower:
            return "Printmaking"
        elif "installation" in url_lower:
            return "Installation"
        else:
            return "Artwork"

    def download_image(self, artwork):
        """Download the main image for an artwork"""
        if not artwork.get("main_image"):
            return None

        try:
            img_url = artwork["main_image"]
            if img_url.startswith("//"):
                img_url = "https:" + img_url

            print(f"⬇️  Downloading image for: {artwork['title']}")
            response = self.session.get(img_url, stream=True, timeout=30)
            response.raise_for_status()

            base_filename = self.sanitize_filename(artwork['title'])
            ext = ".jpg"
            
            url_path = urlparse(img_url).path
            url_ext = os.path.splitext(url_path)[1]
            if url_ext and len(url_ext) <= 5:
                ext = url_ext

            filename = f"{base_filename}{ext}"
            filepath = os.path.join(self.uploads_dir, filename)

            if os.path.exists(filepath):
                print(f"⏩ Image already exists: {filename}")
                return {
                    "url": f"{self.base_url}/wp-content/uploads/{datetime.now().strftime('%Y/%m')}/{filename}",
                    "filepath": filepath,
                    "filename": filename,
                }

            with open(filepath, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)

            image_data = {
                "url": f"{self.base_url}/wp-content/uploads/{datetime.now().strftime('%Y/%m')}/{filename}",
                "filepath": filepath,
                "filename": filename,
            }
            
            print(f"✅ Downloaded: {filename}")
            return image_data

        except Exception as e:
            print(f"❌ Failed to download image for {artwork['title']}: {e}")
            return None

    def sanitize_filename(self, filename):
        """Sanitize filename for WordPress"""
        return re.sub(r"[^a-zA-Z0-9_-]", "_", filename).strip("_")

    def generate_homepage_content(self):
        """Generate homepage content with responsive grid - 3 cards per row on desktop, 2 on tablet, 1 on mobile"""
        homepage_content = f'''
        <div class="homepage-hero">
            <h1>Elliot Spencer Morgan</h1>
            <p class="tagline">Contemporary Art Portfolio</p>
        </div>
        
        <div class="homepage-container">
            <div class="artwork-grid">
        '''
        
        for artwork in self.artworks:
            if artwork.get('wordpress_image'):
                homepage_content += f'''
                <div class="artwork-card">
                    <a href="{artwork['url']}" target="_blank" class="artwork-link">
                        <div class="artwork-image-container">
                            <img src="{artwork['wordpress_image']['url']}" alt="{artwork['title']}" class="artwork-image">
                        </div>
                        <div class="artwork-info">
                            <h3 class="artwork-title">{artwork['title']}</h3>
                            <span class="artwork-category">{artwork['category']}</span>
                        </div>
                    </a>
                </div>
                '''
        
        homepage_content += '''
            </div>
        </div>
        '''
        
        return homepage_content

    def generate_navigation_menu(self):
        """Generate the navigation menu HTML with categories"""
        sorted_categories = sorted(self.categories)
        
        menu_html = '''
        <ul class="main-menu">
            <li><a href="''' + self.base_url + '''">Home</a></li>
        '''
        
        # Add category links (these will go to category archive pages)
        for category in sorted_categories:
            menu_html += f'<li><a href="{self.base_url}/category/{category.lower()}">{category}</a></li>'
        
        # Add About and Contact pages
        menu_html += f'''
            <li><a href="{self.base_url}/about">About</a></li>
            <li><a href="{self.base_url}/contact">Contact</a></li>
        </ul>
        '''
        
        return menu_html

    def generate_wordpress_xml(self):
        """Generate WordPress WXR export file with posts and pages"""
        nsmap = {
            'excerpt': "http://wordpress.org/export/1.2/excerpt/",
            'content': "http://purl.org/rss/1.0/modules/content/",
            'wfw': "http://wellformedweb.org/CommentAPI/",
            'dc': "http://purl.org/dc/elements/1.1/",
            'wp': "http://wordpress.org/export/1.2/"
        }
        
        rss = ET.Element("rss", version="2.0", nsmap=nsmap)
        channel = ET.SubElement(rss, "channel")
        
        # Basic channel info
        ET.SubElement(channel, "title").text = "Elliot Spencer Morgan - Art Portfolio"
        ET.SubElement(channel, "link").text = self.base_url
        ET.SubElement(channel, "description").text = "Artwork Portfolio of Elliot Spencer Morgan"
        ET.SubElement(channel, "pubDate").text = datetime.now().strftime("%a, %d %b %Y %H:%M:%S +0000")
        ET.SubElement(channel, "language").text = "en-US"
        
        # WordPress specific elements
        ET.SubElement(channel, "{%s}wxr_version" % nsmap['wp']).text = "1.2"
        ET.SubElement(channel, "{%s}base_site_url" % nsmap['wp']).text = self.base_url
        ET.SubElement(channel, "{%s}base_blog_url" % nsmap['wp']).text = self.base_url

        # Add author information
        author = ET.SubElement(channel, "{%s}author" % nsmap['wp'])
        ET.SubElement(author, "{%s}author_id" % nsmap['wp']).text = "1"
        ET.SubElement(author, "{%s}author_login" % nsmap['wp']).text = "admin"
        ET.SubElement(author, "{%s}author_email" % nsmap['wp']).text = "admin@lookoverhere.xyz"
        ET.SubElement(author, "{%s}author_display_name" % nsmap['wp']).text = "admin"
        ET.SubElement(author, "{%s}author_first_name" % nsmap['wp']).text = "Admin"
        ET.SubElement(author, "{%s}author_last_name" % nsmap['wp']).text = "User"

        # Add categories as terms
        for i, category in enumerate(sorted(self.categories), 1):
            term = ET.SubElement(channel, "{%s}term" % nsmap['wp'])
            ET.SubElement(term, "{%s}term_id" % nsmap['wp']).text = str(i)
            ET.SubElement(term, "{%s}term_taxonomy" % nsmap['wp']).text = "category"
            ET.SubElement(term, "{%s}term_slug" % nsmap['wp']).text = category.lower()
            ET.SubElement(term, "{%s}term_name" % nsmap['wp']).text = category

        # Add artworks as posts with categories
        for i, artwork in enumerate(self.artworks, 1):
            if artwork.get('wordpress_image'):
                item = ET.SubElement(channel, "item")
                
                # Post basics
                ET.SubElement(item, "title").text = artwork['title']
                ET.SubElement(item, "link").text = artwork['url']  # Link to Saatchi Art
                ET.SubElement(item, "pubDate").text = datetime.now().strftime("%a, %d %b %Y %H:%M:%S +0000")
                ET.SubElement(item, "{%s}creator" % nsmap['dc']).text = "admin"
                
                guid = ET.SubElement(item, "guid", isPermaLink="false")
                guid.text = f"{self.base_url}/?p={100 + i}"  # Unique GUID
                
                ET.SubElement(item, "description").text = ""
                
                # Post content with image and link
                post_content = f"""
                <div class="artwork-post">
                    <a href="{artwork['url']}" target="_blank" class="artwork-link">
                        <img src="{artwork['wordpress_image']['url']}" alt="{artwork['title']}" class="artwork-image">
                    </a>
                    <div class="artwork-info">
                        <h2>{artwork['title']}</h2>
                        <p class="artwork-category">Category: {artwork['category']}</p>
                        <a href="{artwork['url']}" target="_blank" class="view-original">View on Saatchi Art</a>
                    </div>
                </div>
                """
                
                content_elem = ET.SubElement(item, "{%s}encoded" % nsmap['content'])
                content_elem.text = CDATA(post_content)
                
                ET.SubElement(item, "{%s}encoded" % nsmap['excerpt']).text = CDATA(f"{artwork['title']} - {artwork['category']}")
                
                # Post meta
                ET.SubElement(item, "{%s}post_id" % nsmap['wp']).text = str(100 + i)
                ET.SubElement(item, "{%s}post_date" % nsmap['wp']).text = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                ET.SubElement(item, "{%s}post_date_gmt" % nsmap['wp']).text = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                ET.SubElement(item, "{%s}comment_status" % nsmap['wp']).text = "closed"
                ET.SubElement(item, "{%s}ping_status" % nsmap['wp']).text = "closed"
                ET.SubElement(item, "{%s}post_name" % nsmap['wp']).text = self.sanitize_filename(artwork['title'])
                ET.SubElement(item, "{%s}status" % nsmap['wp']).text = "publish"
                ET.SubElement(item, "{%s}post_parent" % nsmap['wp']).text = "0"
                ET.SubElement(item, "{%s}menu_order" % nsmap['wp']).text = "0"
                ET.SubElement(item, "{%s}post_type" % nsmap['wp']).text = "post"
                ET.SubElement(item, "{%s}post_password" % nsmap['wp']).text = ""
                
                # Category assignment
                category_elem = ET.SubElement(item, "category", domain="category", nicename=artwork['category'].lower())
                category_elem.text = artwork['category']
                
                # Custom fields for Saatchi URL and image URL
                postmeta_url = ET.SubElement(item, "{%s}postmeta" % nsmap['wp'])
                ET.SubElement(postmeta_url, "{%s}meta_key" % nsmap['wp']).text = "saatchi_url"
                ET.SubElement(postmeta_url, "{%s}meta_value" % nsmap['wp']).text = artwork['url']
                
                postmeta_image = ET.SubElement(item, "{%s}postmeta" % nsmap['wp'])
                ET.SubElement(postmeta_image, "{%s}meta_key" % nsmap['wp']).text = "artwork_image_url"
                ET.SubElement(postmeta_image, "{%s}meta_value" % nsmap['wp']).text = artwork['wordpress_image']['url']

        # Generate homepage content
        homepage_content = self.generate_homepage_content()
        
        # Create static pages
        pages = [
            {
                "title": "Home",
                "slug": "home",
                "content": homepage_content,
                "is_homepage": True,
                "id": 1
            },
            {
                "title": "About",
                "slug": "about",
                "content": f"""
                <div class="about-page">
                    <h1>About Elliot Spencer Morgan</h1>
                    <div class="bio-section">
                        <p>{self.artist_info['bio']}</p>
                    </div>
                    <div class="statement-section">
                        <h2>Artist Statement</h2>
                        <p>{self.artist_info['statement']}</p>
                    </div>
                </div>
                """,
                "id": 2
            },
            {
                "title": "Contact",
                "slug": "contact", 
                "content": """
                <div class="contact-page">
                    <h1>Contact</h1>
                    <div class="contact-info">
                        <p>For inquiries about artwork, commissions, or exhibitions, please reach out via email.</p>
                        <div class="contact-details">
                            <p><strong>Email:</strong> artist@elliotspencermorgan.com</p>
                            <p><strong>Studio:</strong> Available by appointment</p>
                        </div>
                    </div>
                </div>
                """,
                "id": 3
            }
        ]
        
        # Add static pages to XML
        for page in pages:
            item = ET.SubElement(channel, "item")
            
            ET.SubElement(item, "title").text = page["title"]
            ET.SubElement(item, "link").text = f"{self.base_url}/{page['slug']}" if page['slug'] != "home" else self.base_url
            ET.SubElement(item, "pubDate").text = datetime.now().strftime("%a, %d %b %Y %H:%M:%S +0000")
            ET.SubElement(item, "{%s}creator" % nsmap['dc']).text = "admin"
            
            guid = ET.SubElement(item, "guid", isPermaLink="false")
            guid.text = f"{self.base_url}/?page_id={page['id']}"
            
            ET.SubElement(item, "description").text = ""
            
            content_elem = ET.SubElement(item, "{%s}encoded" % nsmap['content'])
            content_elem.text = CDATA(page["content"])
            
            ET.SubElement(item, "{%s}encoded" % nsmap['excerpt']).text = CDATA(f"{page['title']} - Elliot Spencer Morgan")
            ET.SubElement(item, "{%s}post_id" % nsmap['wp']).text = str(page['id'])
            ET.SubElement(item, "{%s}post_date" % nsmap['wp']).text = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ET.SubElement(item, "{%s}post_date_gmt" % nsmap['wp']).text = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ET.SubElement(item, "{%s}comment_status" % nsmap['wp']).text = "closed"
            ET.SubElement(item, "{%s}ping_status" % nsmap['wp']).text = "closed"
            ET.SubElement(item, "{%s}post_name" % nsmap['wp']).text = page["slug"]
            ET.SubElement(item, "{%s}status" % nsmap['wp']).text = "publish"
            ET.SubElement(item, "{%s}post_parent" % nsmap['wp']).text = "0"
            ET.SubElement(item, "{%s}menu_order" % nsmap['wp']).text = str(page['id'])
            ET.SubElement(item, "{%s}post_type" % nsmap['wp']).text = "page"
            ET.SubElement(item, "{%s}post_password" % nsmap['wp']).text = ""
            
            if page.get("is_homepage"):
                show_on_front = ET.SubElement(channel, "{%s}option" % nsmap['wp'])
                ET.SubElement(show_on_front, "{%s}option_name" % nsmap['wp']).text = "show_on_front"
                ET.SubElement(show_on_front, "{%s}option_value" % nsmap['wp']).text = "page"
                
                page_on_front = ET.SubElement(channel, "{%s}option" % nsmap['wp'])
                ET.SubElement(page_on_front, "{%s}option_name" % nsmap['wp']).text = "page_on_front"
                ET.SubElement(page_on_front, "{%s}option_value" % nsmap['wp']).text = str(page['id'])

        xml_str = ET.tostring(rss, pretty_print=True, encoding="utf-8", xml_declaration=True).decode("utf-8")
        xml_path = os.path.join(self.export_dir, "portfolio-export.xml")
        with open(xml_path, "w", encoding="utf-8") as f:
            f.write(xml_str)
        
        print(f"✅ WordPress export file created: {xml_path}")

    def generate_theme_files(self):
        """Generate complete WordPress theme with responsive grid system"""
        # Generate navigation menu HTML
        navigation_menu = self.generate_navigation_menu()
        
        # style.css - Updated with proper responsive grid system
        style_content = f"""/*
Theme Name: ESM Portfolio
Theme URI: {self.base_url}
Author: Elliot Spencer Morgan
Description: Minimalist portfolio theme for Elliot Spencer Morgan with responsive grid system
Version: 1.0
Text Domain: esm-portfolio
*/

:root {{
    --primary-color: #2c3e50;
    --secondary-color: #e74c3c;
    --background-color: #ffffff;
    --text-color: #333333;
    --border-color: #e0e0e0;
    --card-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    --card-hover-shadow: 0 8px 15px rgba(0, 0, 0, 0.2);
}}

* {{
    box-sizing: border-box;
    margin: 0;
    padding: 0;
}}

body {{
    font-family: 'Helvetica Neue', Arial, sans-serif;
    line-height: 1.6;
    color: var(--text-color);
    background: var(--background-color);
}}

.container {{
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 20px;
}}

/* Header */
.site-header {{
    background: var(--primary-color);
    color: white;
    padding: 1rem 0;
    position: sticky;
    top: 0;
    z-index: 1000;
}}

.header-container {{
    display: flex;
    justify-content: space-between;
    align-items: center;
}}

.site-title {{
    font-size: 1.5rem;
    font-weight: bold;
}}

.site-title a {{
    color: white;
    text-decoration: none;
}}

.main-navigation ul {{
    display: flex;
    list-style: none;
    gap: 2rem;
}}

.main-navigation a {{
    color: white;
    text-decoration: none;
    transition: opacity 0.3s;
    font-weight: 500;
}}

.main-navigation a:hover {{
    opacity: 0.8;
    color: var(--secondary-color);
}}

/* Homepage */
.homepage-hero {{
    text-align: center;
    padding: 4rem 0;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
}}

.homepage-hero h1 {{
    font-size: 3rem;
    margin-bottom: 1rem;
}}

.tagline {{
    font-size: 1.2rem;
    opacity: 0.9;
}}

/* Homepage Container */
.homepage-container {{
    max-width: 1200px;
    margin: 0 auto;
    padding: 2rem 20px;
}}

/* Responsive Grid System */
.artwork-grid {{
    display: grid;
    grid-template-columns: repeat(3, 1fr); /* 3 columns on desktop */
    gap: 2rem;
    width: 100%;
}}

.artwork-card {{
    background: white;
    border-radius: 8px;
    overflow: hidden;
    box-shadow: var(--card-shadow);
    transition: transform 0.3s ease, box-shadow 0.3s ease;
    display: flex;
    flex-direction: column;
}}

.artwork-card:hover {{
    transform: translateY(-5px);
    box-shadow: var(--card-hover-shadow);
}}

.artwork-link {{
    display: flex;
    flex-direction: column;
    text-decoration: none;
    color: inherit;
    height: 100%;
}}

.artwork-image-container {{
    width: 100%;
    height: 250px;
    overflow: hidden;
}}

.artwork-image {{
    width: 100%;
    height: 100%;
    object-fit: cover;
    display: block;
    transition: transform 0.3s ease;
}}

.artwork-card:hover .artwork-image {{
    transform: scale(1.05);
}}

.artwork-info {{
    padding: 1.5rem;
    flex-grow: 1;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
}}

.artwork-title {{
    font-size: 1.1rem;
    margin: 0 0 0.5rem 0;
    color: var(--primary-color);
    font-weight: 600;
    line-height: 1.3;
}}

.artwork-category {{
    font-size: 0.9rem;
    color: var(--secondary-color);
    font-style: italic;
    margin-top: auto;
}}

/* Category Pages */
.category-header {{
    text-align: center;
    padding: 3rem 0 2rem;
    background: #f8f9fa;
}}

.category-title {{
    font-size: 2.5rem;
    color: var(--primary-color);
    margin-bottom: 1rem;
}}

.category-description {{
    font-size: 1.1rem;
    color: var(--text-color);
    opacity: 0.8;
}}

/* Single Post Pages */
.artwork-post {{
    max-width: 1000px;
    margin: 2rem auto;
    padding: 0 20px;
}}

.artwork-post .artwork-image {{
    width: 100%;
    height: auto;
    max-height: 600px;
    margin-bottom: 2rem;
}}

.artwork-info-post {{
    text-align: center;
}}

.artwork-info-post h2 {{
    font-size: 2rem;
    color: var(--primary-color);
    margin-bottom: 1rem;
}}

.view-original {{
    display: inline-block;
    background: var(--secondary-color);
    color: white;
    padding: 0.75rem 1.5rem;
    text-decoration: none;
    border-radius: 4px;
    margin-top: 1rem;
    transition: background 0.3s;
}}

.view-original:hover {{
    background: #c0392b;
}}

/* Pages */
.page-content {{
    padding: 4rem 0;
    max-width: 800px;
    margin: 0 auto;
}}

.page-content h1 {{
    font-size: 2.5rem;
    margin-bottom: 2rem;
    color: var(--primary-color);
}}

.bio-section, .statement-section {{
    margin-bottom: 3rem;
}}

.statement-section h2 {{
    color: var(--secondary-color);
    margin-bottom: 1rem;
}}

.contact-details {{
    background: #f8f9fa;
    padding: 2rem;
    border-radius: 8px;
    margin-top: 2rem;
}}

.contact-details p {{
    margin-bottom: 0.5rem;
}}

/* Footer */
.site-footer {{
    background: var(--primary-color);
    color: white;
    text-align: center;
    padding: 2rem 0;
    margin-top: 4rem;
}}

/* Responsive Design */
/* Tablet Styles (2 columns) */
@media (max-width: 1024px) {{
    .artwork-grid {{
        grid-template-columns: repeat(2, 1fr); /* 2 columns on tablet */
        gap: 1.5rem;
    }}
    
    .homepage-hero h1 {{
        font-size: 2.5rem;
    }}
}}

/* Mobile Styles (1 column) */
@media (max-width: 768px) {{
    .artwork-grid {{
        grid-template-columns: 1fr; /* 1 column on mobile */
        gap: 1rem;
    }}
    
    .homepage-hero {{
        padding: 3rem 0;
    }}
    
    .homepage-hero h1 {{
        font-size: 2rem;
    }}
    
    .homepage-container {{
        padding: 1.5rem 15px;
    }}
    
    .artwork-image-container {{
        height: 200px;
    }}
    
    .artwork-info {{
        padding: 1rem;
    }}
    
    .main-navigation ul {{
        flex-wrap: wrap;
        gap: 1rem;
    }}
    
    .category-title {{
        font-size: 2rem;
    }}
}}

/* Small Mobile Styles */
@media (max-width: 480px) {{
    .header-container {{
        flex-direction: column;
        gap: 1rem;
    }}
    
    .main-navigation ul {{
        flex-direction: column;
        text-align: center;
        gap: 0.5rem;
    }}
    
    .artwork-info {{
        padding: 0.75rem;
    }}
    
    .artwork-title {{
        font-size: 1rem;
    }}
    
    .homepage-hero h1 {{
        font-size: 1.8rem;
    }}
}}
"""

        with open(os.path.join(self.theme_dir, "style.css"), "w") as f:
            f.write(style_content)

        # index.php - Updated to use the new grid system
        index_content = """<?php
/**
 * The main template file
 *
 * @package ESM Portfolio
 */

get_header();
?>

<div class="container">
    <?php if (have_posts()) : ?>
        <?php if (is_category()) : ?>
            <header class="category-header">
                <h1 class="category-title"><?php single_cat_title(); ?></h1>
            </header>
        <?php endif; ?>
        
        <div class="artwork-grid">
            <?php while (have_posts()) : the_post(); ?>
                <div class="artwork-card">
                    <a href="<?php echo get_post_meta(get_the_ID(), 'saatchi_url', true); ?>" target="_blank" class="artwork-link">
                        <?php 
                        $image_url = get_post_meta(get_the_ID(), 'artwork_image_url', true);
                        if ($image_url) : ?>
                            <div class="artwork-image-container">
                                <img src="<?php echo esc_url($image_url); ?>" alt="<?php the_title(); ?>" class="artwork-image">
                            </div>
                        <?php else : ?>
                            <div class="artwork-image-placeholder">No Image Available</div>
                        <?php endif; ?>
                        <div class="artwork-info">
                            <h3 class="artwork-title"><?php the_title(); ?></h3>
                            <?php 
                            $categories = get_the_category();
                            if (!empty($categories)) {
                                echo '<span class="artwork-category">' . esc_html($categories[0]->name) . '</span>';
                            }
                            ?>
                        </div>
                    </a>
                </div>
            <?php endwhile; ?>
        </div>
        
        <?php the_posts_navigation(); ?>
    <?php else : ?>
        <div class="no-content">
            <h1>Nothing Found</h1>
            <p>Sorry, no content available.</p>
        </div>
    <?php endif; ?>
</div>

<?php get_footer(); ?>
"""

        with open(os.path.join(self.theme_dir, "index.php"), "w") as f:
            f.write(index_content)

        # functions.php
        functions_content = """<?php
/**
 * ESM Portfolio functions and definitions
 */

if (!defined('ABSPATH')) {
    exit;
}

function esm_portfolio_setup() {
    add_theme_support('title-tag');
    add_theme_support('post-thumbnails');
    add_theme_support('html5', array(
        'search-form',
        'comment-form',
        'comment-list',
        'gallery',
        'caption',
    ));
    
    // Register navigation menus
    register_nav_menus(array(
        'primary' => __('Primary Menu', 'esm-portfolio'),
    ));
    
    // Add image sizes
    add_image_size('artwork-thumbnail', 400, 300, true);
    add_image_size('artwork-large', 1200, 800, false);
}
add_action('after_setup_theme', 'esm_portfolio_setup');

function esm_portfolio_scripts() {
    wp_enqueue_style('esm-portfolio-style', get_stylesheet_uri());
}
add_action('wp_enqueue_scripts', 'esm_portfolio_scripts');

// Remove single post view - redirect to Saatchi Art
function esm_redirect_single_post() {
    if (is_single() && 'post' == get_post_type()) {
        $saatchi_url = get_post_meta(get_the_ID(), 'saatchi_url', true);
        if ($saatchi_url) {
            wp_redirect($saatchi_url, 301);
            exit;
        }
    }
}
add_action('template_redirect', 'esm_redirect_single_post');

// Custom menu walker
class ESM_Menu_Walker extends Walker_Nav_Menu {
    public function start_el(&$output, $item, $depth = 0, $args = array(), $id = 0) {
        $output .= '<li class="menu-item"><a href="' . $item->url . '">' . $item->title . '</a>';
    }
    
    public function end_el(&$output, $item, $depth = 0, $args = array()) {
        $output .= '</li>';
    }
}
?>
"""

        with open(os.path.join(self.theme_dir, "functions.php"), "w") as f:
            f.write(functions_content)

        # header.php
        header_content = f"""<?php
/**
 * The header for our theme
 */
?><!DOCTYPE html>
<html <?php language_attributes(); ?>>
<head>
    <meta charset="<?php bloginfo('charset'); ?>">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="profile" href="https://gmpg.org/xfn/11">
    <?php wp_head(); ?>
</head>

<body <?php body_class(); ?>>
<?php wp_body_open(); ?>

<header class="site-header">
    <div class="container">
        <div class="header-container">
            <div class="site-title">
                <a href="<?php echo esc_url(home_url('/')); ?>">Elliot Spencer Morgan</a>
            </div>
            
            <nav class="main-navigation">
                {navigation_menu}
            </nav>
        </div>
    </div>
</header>

<main class="site-main">
"""

        with open(os.path.join(self.theme_dir, "header.php"), "w") as f:
            f.write(header_content)

        # footer.php
        footer_content = """<?php
/**
 * The footer for our theme
 */
?>
</main>

<footer class="site-footer">
    <div class="container">
        <p>&copy; <?php echo date('Y'); ?> Elliot Spencer Morgan. All rights reserved.</p>
    </div>
</footer>

<?php wp_footer(); ?>
</body>
</html>
"""

        with open(os.path.join(self.theme_dir, "footer.php"), "w") as f:
            f.write(footer_content)

        # front-page.php - Homepage template
        front_page_content = """<?php
/**
 * The homepage template
 */
get_header();
?>

<?php if (have_posts()) : ?>
    <?php while (have_posts()) : the_post(); ?>
        <?php the_content(); ?>
    <?php endwhile; ?>
<?php endif; ?>

<?php get_footer(); ?>
"""

        with open(os.path.join(self.theme_dir, "front-page.php"), "w") as f:
            f.write(front_page_content)

        # page.php - Static pages
        page_content = """<?php
/**
 * The template for displaying pages
 */
get_header();
?>

<div class="container">
    <div class="page-content">
        <?php while (have_posts()) : the_post(); ?>
            <article id="post-<?php the_ID(); ?>" <?php post_class(); ?>>
                <header class="page-header">
                    <h1><?php the_title(); ?></h1>
                </header>
                
                <div class="entry-content">
                    <?php the_content(); ?>
                </div>
            </article>
        <?php endwhile; ?>
    </div>
</div>

<?php get_footer(); ?>
"""

        with open(os.path.join(self.theme_dir, "page.php"), "w") as f:
            f.write(page_content)

        # single.php - Single post (redirects to Saatchi)
        single_content = """<?php
/**
 * The template for displaying single posts
 * Note: This template redirects to Saatchi Art, but is here as a fallback
 */
get_header();
?>

<div class="container">
    <article id="post-<?php the_ID(); ?>" <?php post_class(); ?>>
        <header class="entry-header">
            <h1 class="entry-title"><?php the_title(); ?></h1>
        </header>
        
        <div class="entry-content">
            <?php the_content(); ?>
            <p><a href="<?php echo get_post_meta(get_the_ID(), 'saatchi_url', true); ?>" target="_blank">View on Saatchi Art</a></p>
        </div>
    </article>
</div>

<?php get_footer(); ?>
"""

        with open(os.path.join(self.theme_dir, "single.php"), "w") as f:
            f.write(single_content)

        # category.php - Category archive template
        category_content = """<?php
/**
 * The template for displaying category archive pages
 */
get_header();
?>

<div class="container">
    <header class="category-header">
        <h1 class="category-title"><?php single_cat_title(); ?></h1>
    </header>
    
    <div class="artwork-grid">
        <?php if (have_posts()) : ?>
            <?php while (have_posts()) : the_post(); ?>
                <div class="artwork-card">
                    <a href="<?php echo get_post_meta(get_the_ID(), 'saatchi_url', true); ?>" target="_blank" class="artwork-link">
                        <?php 
                        $image_url = get_post_meta(get_the_ID(), 'artwork_image_url', true);
                        if ($image_url) : ?>
                            <div class="artwork-image-container">
                                <img src="<?php echo esc_url($image_url); ?>" alt="<?php the_title(); ?>" class="artwork-image">
                            </div>
                        <?php else : ?>
                            <div class="artwork-image-placeholder">No Image Available</div>
                        <?php endif; ?>
                        <div class="artwork-info">
                            <h3 class="artwork-title"><?php the_title(); ?></h3>
                        </div>
                    </a>
                </div>
            <?php endwhile; ?>
        <?php else : ?>
            <p>No artworks found in this category.</p>
        <?php endif; ?>
    </div>
    
    <?php the_posts_navigation(); ?>
</div>

<?php get_footer(); ?>
"""

        with open(os.path.join(self.theme_dir, "category.php"), "w") as f:
            f.write(category_content)

        # Create screenshot.txt
        screenshot_content = f"""ESM Portfolio Theme Screenshot
=============================

This theme features a clean, modern design for Elliot Spencer Morgan's art portfolio with a responsive grid system.

Categories Found: {', '.join(sorted(self.categories))}

Key Features:
- Responsive grid: 3 cards per row on desktop, 2 on tablet, 1 on mobile
- Fixed image display with hover effects
- Artwork titles displayed below images
- Navigation with category links
- Clickable images linking to Saatchi Art
- About and Contact static pages
- Mobile-responsive design

Grid System:
- Desktop (1024px+): 3 columns
- Tablet (768px-1024px): 2 columns  
- Mobile (<768px): 1 column

To add a proper screenshot:
1. Take a screenshot of your live site
2. Save it as screenshot.png (1200x900 pixels)
3. Upload it to the theme folder
"""

        with open(os.path.join(self.theme_dir, "screenshot.txt"), "w") as f:
            f.write(screenshot_content)

        print(f"✅ Complete theme files created in: {self.theme_dir}")
        print(f"📊 Categories found: {', '.join(sorted(self.categories))}")

    def generate_import_instructions(self):
        """Generate import instructions"""
        categories_list = ', '.join(sorted(self.categories))
        
        instructions = f"""
        # WordPress Portfolio Import Instructions
        
        ## Files Generated:
        1. `portfolio-export.xml` - WordPress WXR import file with posts and pages
        2. `wp-content/uploads/` - All downloaded artwork images
        3. `theme/esm-portfolio/` - Complete WordPress theme
        
        ## Structure:
        - **Homepage**: Static page with responsive grid (3 cards per row on desktop, 2 on tablet, 1 on mobile)
        - **Category Pages**: Dynamic pages showing filtered artwork posts with responsive grid
        - **About/Contact**: Static pages
        - **Navigation**: Includes category links to post archives
        
        ## Categories Found:
        {categories_list}
        
        ## Installation Steps:
        
        1. **Install WordPress** at: {self.base_url}
        
        2. **Upload Images** via FTP to: `/wp-content/uploads/`
        
        3. **Import XML File**:
           - Go to WordPress Admin → Tools → Import
           - Install "WordPress Importer" plugin
           - Upload and import `portfolio-export.xml`
           - Assign authors to 'admin' user
        
        4. **Install Theme**:
           - Zip the `esm-portfolio` folder (inside the theme folder)
           - WordPress Admin → Appearance → Themes → Add New → Upload Theme
           - Upload the zip file and activate the theme
        
        5. **Set Up Navigation** (Already configured in theme):
           - The navigation menu automatically includes categories: {categories_list}
           - Category links go to post archive pages
        
        6. **Set Homepage**:
           - Settings → Reading
           - "Your homepage displays" → "A static page"
           - Homepage: Select "Home"
        
        7. **Configure Permalinks**:
           - Settings → Permalinks
           - Choose "Post name" for clean URLs
           - Save changes
        
        ## Responsive Grid Features:
        - **Desktop (1024px+)**: 3 cards per row
        - **Tablet (768px-1024px)**: 2 cards per row
        - **Mobile (<768px)**: 1 card per row
        - Hover effects on cards
        - Consistent spacing and styling
        
        ## Theme Features:
        - Consistent navigation across all pages
        - Responsive grid layout on homepage and category pages
        - Fixed image display with proper aspect ratios
        - Mobile-responsive design
        - Automatic category-based filtering
        
        ## Important Notes:
        - Zip the 'esm-portfolio' folder (not the parent 'theme' folder)
        - Images are stored in custom fields for reliable display
        - All artwork thumbnails link directly to Saatchi Art
        - The grid system is fully responsive and will adapt to different screen sizes
        """

        with open(os.path.join(self.base_dir, "IMPORT_INSTRUCTIONS.md"), "w", encoding="utf-8") as f:
            f.write(instructions)

        print(f"✅ Import instructions created")

    def run(self):
        """Main function to generate WordPress portfolio"""
        print("🚀 Generating WordPress Portfolio...")
        self.create_directory_structure()

        # Get artwork URLs
        artwork_urls = self.get_artwork_urls()
        total_artworks = len(artwork_urls)

        print(f"🎨 Processing {total_artworks} artworks...")

        # Scrape and process each artwork
        for i, url in enumerate(artwork_urls, 1):
            print(f"\n📄 Processing {i}/{total_artworks}: {url}")

            artwork_data = self.extract_artwork_data(url)
            if artwork_data:
                image_data = self.download_image(artwork_data)
                if image_data:
                    artwork_data["wordpress_image"] = image_data
                    self.artworks.append(artwork_data)
                    print(f"✅ Added: {artwork_data['title']}")
                else:
                    print(f"❌ Failed to download image for: {artwork_data['title']}")

            time.sleep(2)

        # Generate WordPress files
        print("\n🛠️  Generating WordPress export files...")
        self.generate_wordpress_xml()
        self.generate_theme_files()
        self.generate_import_instructions()

        # Summary
        print(f"\n🎉 WordPress Portfolio Generation Complete!")
        print(f"📁 Output directory: {self.base_dir}")
        print(f"🖼️  Artworks processed: {len(self.artworks)}")
        print(f"📊 Categories found: {', '.join(sorted(self.categories))}")
        print(f"🌐 Base URL: {self.base_url}")
        print(f"📄 Export file: {self.export_dir}/portfolio-export.xml")
        print(f"🎨 Theme folder: {self.theme_dir}/")
        print(f"📖 Instructions: {self.base_dir}/IMPORT_INSTRUCTIONS.md")
        print(f"\n💡 Important: Zip the 'esm-portfolio' folder for theme installation")
        print(f"📱 Responsive Grid: 3 columns (desktop), 2 columns (tablet), 1 column (mobile)")


def main():
    """Main function"""
    try:
        generator = WordPressPortfolioGenerator()
        generator.run()
    except KeyboardInterrupt:
        print("\n⏹️  Process interrupted by user")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()