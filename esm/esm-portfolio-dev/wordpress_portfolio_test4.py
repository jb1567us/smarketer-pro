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
        self.artist_info = {
            "name": "Elliot Spencer Morgan",
            "bio": "",
            "statement": ""
        }

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
        self.theme_dir = os.path.join(self.base_dir, "theme")

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
            # Add the rest of your URLs here later
        ]

    def extract_artist_info(self):
        """Extract artist information from the first artwork page"""
        try:
            # Use the first artwork URL to get artist info
            url = self.get_artwork_urls()[0]
            print(f"📄 Extracting artist info from: {url}")
            response = self.session.get(url, timeout=30)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, "html.parser")
            
            # Extract artist bio if available
            bio_selectors = [
                '.artist-bio',
                '.artist-description',
                '[data-testid*="bio"]',
                '[class*="artist-about"]'
            ]
            
            for selector in bio_selectors:
                bio_elem = soup.select_one(selector)
                if bio_elem and bio_elem.get_text(strip=True):
                    self.artist_info["bio"] = bio_elem.get_text(strip=True)
                    break
            
            # If no bio found, create a default one
            if not self.artist_info["bio"]:
                self.artist_info["bio"] = "Elliot Spencer Morgan is a contemporary artist working across multiple mediums including painting, sculpture, collage, and installation. Their work explores the intersection of organic forms and structured compositions."
            
            # Artist statement
            self.artist_info["statement"] = "My work is an exploration of the relationship between natural forms and constructed environments, blending organic shapes with geometric precision to create visual dialogues about our place in the modern world."
            
            print(f"✅ Extracted artist information")
            
        except Exception as e:
            print(f"❌ Error extracting artist info: {e}")
            # Set default values
            self.artist_info["bio"] = "Elliot Spencer Morgan is a contemporary artist working across multiple mediums including painting, sculpture, collage, and installation."
            self.artist_info["statement"] = "My work explores the relationship between natural forms and constructed environments."

    def extract_artwork_data(self, url):
        """Extract detailed artwork information from Saatchi Art page"""
        try:
            print(f"📄 Scraping: {url}")
            response = self.session.get(url, timeout=30)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, "html.parser")

            # Try multiple strategies to extract title
            title = self.extract_title(soup, url)

            data = {
                "url": url,
                "title": title,
                "artist": "Elliot Spencer Morgan",  # Hardcoded as requested
                "price": self.extract_price(soup),
                "medium": self.extract_medium(soup),
                "dimensions": self.extract_dimensions(soup),
                "description": self.extract_description(soup),
                "year_created": self.extract_year(soup),
                "subject": self.extract_subject(soup),
                "styles": self.extract_styles(soup),
                "rarity": self.extract_rarity(soup),
                "ready_to_hang": self.extract_ready_to_hang(soup),
                "framing": self.extract_framing(soup),
                "authenticity": self.extract_authenticity(soup),
                "packaging": self.extract_packaging(soup),
                "images": self.extract_images(soup),
                "scraped_at": datetime.now().isoformat(),
            }

            # Clean up data
            data["title"] = data["title"] or "Untitled Artwork"

            print(f"📝 Extracted: {data['title']}")
            return data

        except Exception as e:
            print(f"❌ Error scraping {url}: {e}")
            return None

    def extract_title(self, soup, url):
        """Extract title using multiple strategies"""
        # Strategy 1: Direct CSS selectors
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

        # Strategy 2: Meta tags
        meta_selectors = [
            'meta[property="og:title"]',
            'meta[name="twitter:title"]',
            'meta[property="twitter:title"]',
        ]

        for selector in meta_selectors:
            meta = soup.select_one(selector)
            if meta and meta.get("content"):
                title = meta["content"]
                if title and title.strip() and title != "Saatchi Art":
                    return title.strip()

        # Strategy 3: Extract from URL as last resort
        url_path = urlparse(url).path
        path_parts = [
            part for part in url_path.split("/") if part and part not in ["art", "view"]
        ]
        if len(path_parts) >= 2:
            # The title is usually the part after /art/
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

    def extract_price(self, soup):
        """Extract price information"""
        price_selectors = [
            '[data-testid="price-amount"]',
            '[class*="price"]',
            ".price-value",
            'span:contains("$")',
        ]

        for selector in price_selectors:
            try:
                elem = soup.select_one(selector)
                if elem and "$" in elem.get_text():
                    return elem.get_text(strip=True)
            except:
                continue
        return "Price not available"

    
    def extract_dimensions(self, soup):
        """Extract dimensions"""
        # Look for dimensions pattern (W × H × D or W x H x D)
        dimensions_pattern = (
            r"\d+\.?\d*\s*[×x]\s*\d+\.?\d*\s*[×x]?\s*\d*\.?\d*\s*(in|cm)"
        )
        text = soup.get_text()
        match = re.search(dimensions_pattern, text)
        if match:
            return match.group(0)
        return "Dimensions not specified"

    def extract_description(self, soup):
        """Extract clean artwork description only"""
        # Look for the actual description text, not the entire page
        description_selectors = [
            '[data-testid="artwork-description"]',
            ".artwork-description",
            'p:contains("ABOUT THE ARTWORK") + p',
            'div:contains("ABOUT THE ARTWORK") + div',
        ]
    
        for selector in description_selectors:
            try:
                elem = soup.select_one(selector)
                if elem and elem.get_text(strip=True):
                    # Get just the first paragraph or reasonable length
                    text = elem.get_text(strip=True)
                    # Clean up - take only the actual description part
                    if "ABOUT THE ARTWORK" in text:
                        text = text.split("ABOUT THE ARTWORK")[-1].strip()
                    if "DETAILS AND DIMENSIONS" in text:
                        text = text.split("DETAILS AND DIMENSIONS")[0].strip()
                    if "SHIPPING AND RETURNS" in text:
                        text = text.split("SHIPPING AND RETURNS")[0].strip()
                    
                    # Limit to reasonable length and clean up
                    if len(text) > 500:
                        # Find a good breaking point
                        sentences = text.split('.')
                        if len(sentences) > 1:
                            text = '.'.join(sentences[:2]) + '.'
                        else:
                            text = text[:497] + '...'
                    
                    return text
            except:
                continue
    
        # Fallback: look for any meaningful paragraph
        paragraphs = soup.find_all('p')
        for p in paragraphs:
            text = p.get_text(strip=True)
            if len(text) > 50 and len(text) < 500:
                if not any(x in text.lower() for x in ['copyright', 'terms', 'privacy', 'shipping', 'return']):
                    return text
        
        return "No description available"

    def extract_clean_field(self, soup, field_name, default="Not specified"):
        """Extract a specific field cleanly without grabbing entire page content"""
        # First try to find the field in details section
        details = self.extract_details_section(soup)
        for line in details:
            if field_name.lower() in line.lower():
                # Extract just the value after the field name
                if ':' in line:
                    parts = line.split(':', 1)
                    if len(parts) > 1:
                        value = parts[1].strip()
                        # Clean up - stop at next field or reasonable point
                        stop_words = ['Year', 'Subject', 'Styles', 'Medium', 'Rarity', 
                                    'Size', 'Ready', 'Frame', 'Authenticity', 'Packaging',
                                    'Delivery', 'Returns', 'Handling', 'Ships']
                        for word in stop_words:
                            if word in value and word != field_name:
                                value = value.split(word)[0].strip()
                        return value[:200]  # Limit length
                return line
        
        # If not found in details, try regex with boundaries
        pattern = rf"{field_name}:\s*([^\n\r]+?)(?=\w+:|$)"
        text = soup.get_text()
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            value = match.group(1).strip()
            return value[:200]
        
        return default

    def extract_year(self, soup):
        """Extract year created - clean version"""
        return self.extract_clean_field(soup, "Year Created", "Year not specified")

    def extract_subject(self, soup):
        """Extract subject - clean version"""
        return self.extract_clean_field(soup, "Subject", "Subject not specified")

    def extract_styles(self, soup):
        """Extract styles - clean version"""
        return self.extract_clean_field(soup, "Styles", "Styles not specified")

    def extract_rarity(self, soup):
        """Extract rarity - clean version"""
        return self.extract_clean_field(soup, "Rarity", "Rarity not specified")

    def extract_ready_to_hang(self, soup):
        """Extract ready to hang - clean version"""
        return self.extract_clean_field(soup, "Ready To Hang", "Not specified")

    def extract_framing(self, soup):
        """Extract framing - clean version"""
        return self.extract_clean_field(soup, "Frame", "Not specified")

    def extract_authenticity(self, soup):
        """Extract authenticity - clean version"""
        return self.extract_clean_field(soup, "Authenticity", "Not specified")

    def extract_packaging(self, soup):
        """Extract packaging - clean version"""
        return self.extract_clean_field(soup, "Packaging", "Not specified")

    def extract_medium(self, soup):
        """Extract medium - clean version"""
        # Try multiple field names for medium
        for field_name in ["Medium", "Mediums", "Materials"]:
            result = self.extract_clean_field(soup, field_name, "")
            if result and result != "Not specified":
                return result
        
        # Fallback to original method but cleaned up
        details = self.extract_details_section(soup)
        for line in details:
            if "medium" in line.lower():
                if ':' in line:
                    return line.split(':', 1)[1].strip()[:100]
                return line[:100]
        return "Medium not specified"

    def extract_details_section(self, soup):
        """Extract all details text"""
        details_selectors = [
            '[data-testid*="detail"]',
            ".artwork-details",
            ".details-section",
            'div:contains("DETAILS AND DIMENSIONS") + div',
        ]

        for selector in details_selectors:
            try:
                elem = soup.select_one(selector)
                if elem:
                    return [
                        line.strip()
                        for line in elem.get_text().split("\n")
                        if line.strip()
                    ]
            except:
                continue
        return []

    def extract_images(self, soup):
        """Extract image URLs"""
        images = set()
        # Meta tags
        for meta in soup.find_all("meta", property=["og:image", "twitter:image"]):
            if meta.get("content"):
                images.add(meta["content"])
        # Image tags
        for img in soup.find_all("img"):
            for attr in ["src", "data-src"]:
                if img.get(attr) and any(
                    x in img[attr] for x in [".jpg", ".jpeg", ".png", ".webp"]
                ):
                    images.add(img[attr])
        return list(images)

    def download_images(self, artwork):
        """Download images for an artwork with proper filenames"""
        image_paths = []

        # Get a good base filename
        if artwork["title"] and artwork["title"] != "Untitled Artwork":
            base_filename = self.sanitize_filename(artwork["title"])
        else:
            # Extract from URL as fallback
            url_path = urlparse(artwork["url"]).path
            path_parts = [
                part
                for part in url_path.split("/")
                if part and part not in ["art", "view"]
            ]
            if len(path_parts) >= 2:
                base_filename = self.sanitize_filename(path_parts[1].replace("-", " "))
            else:
                base_filename = "artwork"

        for i, img_url in enumerate(
            artwork["images"][:5]  # Limit to 5 images per artwork
        ):
            try:
                if img_url.startswith("//"):
                    img_url = "https:" + img_url

                response = self.session.get(img_url, stream=True, timeout=30)
                response.raise_for_status()

                # Get file extension from content type or URL
                content_type = response.headers.get("content-type", "")
                if "image/jpeg" in content_type:
                    ext = ".jpg"
                elif "image/png" in content_type:
                    ext = ".png"
                elif "image/webp" in content_type:
                    ext = ".webp"
                else:
                    # Get extension from URL
                    url_path = urlparse(img_url).path
                    ext = os.path.splitext(url_path)[1]
                    if not ext or len(ext) > 5:
                        ext = ".jpg"

                filename = f"{base_filename}_{i:02d}{ext}"
                filepath = os.path.join(self.uploads_dir, filename)

                # Check if file already exists to avoid duplicates
                if os.path.exists(filepath):
                    print(f"⏩ Image already exists: {filename}")
                    image_paths.append(
                        {
                            "url": f"/wp-content/uploads/{datetime.now().strftime('%Y/%m')}/{filename}",
                            "filepath": filepath,
                            "filename": filename,
                        }
                    )
                    continue

                with open(filepath, "wb") as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)

                image_paths.append(
                    {
                        "url": f"/wp-content/uploads/{datetime.now().strftime('%Y/%m')}/{filename}",
                        "filepath": filepath,
                        "filename": filename,
                    }
                )
                print(f"✅ Downloaded: {filename}")

            except Exception as e:
                print(f"❌ Failed to download image: {e}")

        return image_paths

    def sanitize_filename(self, filename):
        """Sanitize filename for WordPress"""
        return re.sub(r"[^a-zA-Z0-9_-]", "_", filename).strip("_")

    def generate_post_content(self, artwork):
        """Generate clean, concise WordPress-formatted content for a post"""
        # Create image gallery HTML
        image_gallery = ""
        if artwork.get("wordpress_images"):
            image_gallery = '<div class="artwork-gallery">'
            for img in artwork["wordpress_images"][:3]:  # Limit to 3 images
                image_gallery += f'<img src="{img["url"]}" alt="{artwork["title"]}" class="artwork-image" />'
            image_gallery += '</div>'
        
        # Clean up the description - remove any duplicate or excessive content
        description = artwork['description']
        if len(description) > 500:
            # Find a natural breaking point
            sentences = description.split('.')
            if len(sentences) > 2:
                description = '.'.join(sentences[:3]) + '.'
            else:
                description = description[:497] + '...'
        
        content = f"""
        <div class="artwork-detail-page">
            {image_gallery}
            
            <div class="artwork-info">
                <h1>{artwork['title']}</h1>
                
                <div class="artwork-meta">
                    <div class="artwork-price">{artwork['price']}</div>
                    <div class="artwork-medium">{artwork['medium']}</div>
                    <div class="artwork-dimensions">{artwork['dimensions']}</div>
                </div>
                
                <div class="artwork-description">
                    <h3>About the Artwork</h3>
                    <p>{description}</p>
                </div>
                
                <div class="artwork-details">
                    <h3>Details</h3>
                    <ul>
                        <li><strong>Year Created:</strong> {artwork['year_created']}</li>
                        <li><strong>Subject:</strong> {artwork['subject']}</li>
                        <li><strong>Styles:</strong> {artwork['styles']}</li>
                        <li><strong>Rarity:</strong> {artwork['rarity']}</li>
                        <li><strong>Ready to Hang:</strong> {artwork['ready_to_hang']}</li>
                        <li><strong>Framing:</strong> {artwork['framing']}</li>
                        <li><strong>Authenticity:</strong> {artwork['authenticity']}</li>
                        <li><strong>Packaging:</strong> {artwork['packaging']}</li>
                    </ul>
                </div>
            </div>
        </div>
        """
        
        return content

    def generate_wordpress_xml(self):
        """Generate WordPress WXR export file with proper WXR format using lxml"""
        # Define namespace map
        nsmap = {
            'excerpt': "http://wordpress.org/export/1.2/excerpt/",
            'content': "http://purl.org/rss/1.0/modules/content/",
            'wfw': "http://wellformedweb.org/CommentAPI/",
            'dc': "http://purl.org/dc/elements/1.1/",
            'wp': "http://wordpress.org/export/1.2/"
        }
        
        # Create the root element with namespaces
        rss = ET.Element("rss", version="2.0", nsmap=nsmap)
        
        # Create channel element
        channel = ET.SubElement(rss, "channel")
        
        # Add required channel elements
        title = ET.SubElement(channel, "title")
        title.text = "Elliot Spencer Morgan - Art Portfolio"
        
        link = ET.SubElement(channel, "link")
        link.text = "https://lookoverhere.xyz/elliot"
        
        description = ET.SubElement(channel, "description")
        description.text = "Artwork Portfolio of Elliot Spencer Morgan"
        
        pub_date = ET.SubElement(channel, "pubDate")
        pub_date.text = datetime.now().strftime("%a, %d %b %Y %H:%M:%S +0000")
        
        language = ET.SubElement(channel, "language")
        language.text = "en-US"
        
        # Use proper namespace prefixes for elements
        wxr_version = ET.SubElement(channel, "{%s}wxr_version" % nsmap['wp'])
        wxr_version.text = "1.2"
        
        base_site_url = ET.SubElement(channel, "{%s}base_site_url" % nsmap['wp'])
        base_site_url.text = "https://lookoverhere.xyz/elliot"
        
        base_blog_url = ET.SubElement(channel, "{%s}base_blog_url" % nsmap['wp'])
        base_blog_url.text = "https://lookoverhere.xyz/elliot"

        # Add categories (terms)
        categories = [
            "Painting",
            "Sculpture",
            "Collage",
            "Printmaking",
            "Installation",
            "Artwork",
        ]
        
        for i, cat in enumerate(categories, 1):
            term = ET.SubElement(channel, "{%s}term" % nsmap['wp'])
            
            term_id = ET.SubElement(term, "{%s}term_id" % nsmap['wp'])
            term_id.text = str(i)
            
            term_taxonomy = ET.SubElement(term, "{%s}term_taxonomy" % nsmap['wp'])
            term_taxonomy.text = "category"
            
            term_slug = ET.SubElement(term, "{%s}term_slug" % nsmap['wp'])
            term_slug.text = cat.lower()
            
            term_name = ET.SubElement(term, "{%s}term_name" % nsmap['wp'])
            term_name.text = cat
        
        # Add author information
        author = ET.SubElement(channel, "{%s}author" % nsmap['wp'])
        
        author_id = ET.SubElement(author, "{%s}author_id" % nsmap['wp'])
        author_id.text = "1"
        
        author_login = ET.SubElement(author, "{%s}author_login" % nsmap['wp'])
        author_login.text = "admin"
        
        author_email = ET.SubElement(author, "{%s}author_email" % nsmap['wp'])
        author_email.text = "admin@lookoverhere.xyz"
        
        author_display_name = ET.SubElement(author, "{%s}author_display_name" % nsmap['wp'])
        author_display_name.text = "admin"
        
        author_first_name = ET.SubElement(author, "{%s}author_first_name" % nsmap['wp'])
        author_first_name.text = "Admin"
        
        author_last_name = ET.SubElement(author, "{%s}author_last_name" % nsmap['wp'])
        author_last_name.text = "User"

        # Add artworks as posts
        for i, artwork in enumerate(self.artworks, 1):
            if artwork.get("images"):
                item = ET.SubElement(channel, "item")
                
                # Title
                title = ET.SubElement(item, "title")
                title.text = artwork['title']
                
                # Link
                link = ET.SubElement(item, "link")
                link.text = f"https://lookoverhere.xyz/elliot/artwork/{self.sanitize_filename(artwork['title'])}"
                
                # Publication date
                pub_date = ET.SubElement(item, "pubDate")
                pub_date.text = datetime.now().strftime("%a, %d %b %Y %H:%M:%S +0000")
                
                # Creator
                creator = ET.SubElement(item, "{%s}creator" % nsmap['dc'])
                creator.text = "admin"
                
                # GUID
                guid = ET.SubElement(item, "guid", isPermaLink="false")
                guid.text = f"https://lookoverhere.xyz/elliot/?p={i}"
                
                # Description
                description = ET.SubElement(item, "description")
                description.text = ""
                
                # Content
                content = ET.SubElement(item, "{%s}encoded" % nsmap['content'])
                content.text = CDATA(self.generate_post_content(artwork))
                
                # Excerpt
                excerpt = ET.SubElement(item, "{%s}encoded" % nsmap['excerpt'])
                excerpt_text = artwork["description"][:200] + "..." if artwork["description"] else ""
                excerpt.text = CDATA(excerpt_text)
                
                # Post ID
                post_id = ET.SubElement(item, "{%s}post_id" % nsmap['wp'])
                post_id.text = str(i)
                
                # Post date
                post_date = ET.SubElement(item, "{%s}post_date" % nsmap['wp'])
                post_date.text = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                # Post date GMT
                post_date_gmt = ET.SubElement(item, "{%s}post_date_gmt" % nsmap['wp'])
                post_date_gmt.text = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                # Comment status
                comment_status = ET.SubElement(item, "{%s}comment_status" % nsmap['wp'])
                comment_status.text = "closed"
                
                # Ping status
                ping_status = ET.SubElement(item, "{%s}ping_status" % nsmap['wp'])
                ping_status.text = "closed"
                
                # Post name (slug)
                post_name = ET.SubElement(item, "{%s}post_name" % nsmap['wp'])
                post_name.text = self.sanitize_filename(artwork['title'])
                
                # Status
                status = ET.SubElement(item, "{%s}status" % nsmap['wp'])
                status.text = "publish"
                
                # Post parent
                post_parent = ET.SubElement(item, "{%s}post_parent" % nsmap['wp'])
                post_parent.text = "0"
                
                # Menu order
                menu_order = ET.SubElement(item, "{%s}menu_order" % nsmap['wp'])
                menu_order.text = "0"
                
                # Post type
                post_type = ET.SubElement(item, "{%s}post_type" % nsmap['wp'])
                post_type.text = "post"
                
                # Post password
                post_password = ET.SubElement(item, "{%s}post_password" % nsmap['wp'])
                post_password.text = ""
                
                # Category
                category = ET.SubElement(item, "category", domain="category", nicename=self.determine_category(artwork['medium']).lower())
                category.text = self.determine_category(artwork['medium'])
                
                # Add post meta for artwork details
                meta_fields = {
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
                
                for key, value in meta_fields.items():
                    postmeta = ET.SubElement(item, "{%s}postmeta" % nsmap['wp'])
                    
                    meta_key = ET.SubElement(postmeta, "{%s}meta_key" % nsmap['wp'])
                    meta_key.text = key
                    
                    meta_value = ET.SubElement(postmeta, "{%s}meta_value" % nsmap['wp'])
                    meta_value.text = str(value)
        
        # Add About and Contact pages
        pages_content = self.create_pages_xml(nsmap)
        for page in pages_content:
            channel.append(page)
        
        # Create XML tree
        tree = ET.ElementTree(rss)
        
        # Convert to string with pretty formatting
        xml_str = ET.tostring(rss, pretty_print=True, encoding="utf-8", xml_declaration=True).decode("utf-8")
        
        # Remove extra empty lines
        xml_str = os.linesep.join([s for s in xml_str.splitlines() if s.strip()])
        
        # Save XML file
        xml_path = os.path.join(self.export_dir, "portfolio-export.xml")
        with open(xml_path, "w", encoding="utf-8") as f:
            f.write(xml_str)
        
        print(f"✅ WordPress export file created: {xml_path}")

    def create_page_xml(self, title, content, post_id, slug, nsmap):
        """Create XML for a page with absolute URLs"""
        item = ET.Element("item")
        
        # Title
        title_elem = ET.SubElement(item, "title")
        title_elem.text = title
        
        # Link - ABSOLUTE URL
        link = ET.SubElement(item, "link")
        link.text = f"https://lookoverhere.xyz/elliot/{slug}"
        
        # Publication date
        pub_date = ET.SubElement(item, "pubDate")
        pub_date.text = datetime.now().strftime("%a, %d %b %Y %H:%M:%S +0000")
        
        # Creator
        creator = ET.SubElement(item, "{%s}creator" % nsmap['dc'])
        creator.text = "admin"
        
        # GUID - ABSOLUTE URL
        guid = ET.SubElement(item, "guid", isPermaLink="false")
        guid.text = f"https://lookoverhere.xyz/elliot/?page_id={post_id}"
        
        # Description
        description = ET.SubElement(item, "description")
        description.text = ""
        
        # Content
        content_elem = ET.SubElement(item, "{%s}encoded" % nsmap['content'])
        content_elem.text = CDATA(content)
        
        # Excerpt
        excerpt = ET.SubElement(item, "{%s}encoded" % nsmap['excerpt'])
        excerpt.text = CDATA(f"{title} - Elliot Spencer Morgan")
        
        # Post ID
        post_id_elem = ET.SubElement(item, "{%s}post_id" % nsmap['wp'])
        post_id_elem.text = str(post_id)
        
        # Post date
        post_date = ET.SubElement(item, "{%s}post_date" % nsmap['wp'])
        post_date.text = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Post date GMT
        post_date_gmt = ET.SubElement(item, "{%s}post_date_gmt" % nsmap['wp'])
        post_date_gmt.text = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Comment status
        comment_status = ET.SubElement(item, "{%s}comment_status" % nsmap['wp'])
        comment_status.text = "closed"
        
        # Ping status
        ping_status = ET.SubElement(item, "{%s}ping_status" % nsmap['wp'])
        ping_status.text = "closed"
        
        # Post name (slug)
        post_name = ET.SubElement(item, "{%s}post_name" % nsmap['wp'])
        post_name.text = slug
        
        # Status
        status = ET.SubElement(item, "{%s}status" % nsmap['wp'])
        status.text = "publish"
        
        # Post parent
        post_parent = ET.SubElement(item, "{%s}post_parent" % nsmap['wp'])
        post_parent.text = "0"
        
        # Menu order
        menu_order = ET.SubElement(item, "{%s}menu_order" % nsmap['wp'])
        menu_order.text = str(post_id - len(self.artworks))  # 1 for About, 2 for Contact
        
        # Post type
        post_type = ET.SubElement(item, "{%s}post_type" % nsmap['wp'])
        post_type.text = "page"
        
        # Post password
        post_password = ET.SubElement(item, "{%s}post_password" % nsmap['wp'])
        post_password.text = ""
        
        return item

    def create_pages_xml(self, nsmap):
        """Create XML elements for About and Contact pages using lxml"""
        about_content = f"""
        <h2>About Elliot Spencer Morgan</h2>
        <p>{self.artist_info['bio']}</p>
        
        <h3>Artist Statement</h3>
        <p>{self.artist_info['statement']}</p>
        
        <h3>Exhibitions & Recognition</h3>
        <p>Elliot's work has been exhibited in galleries across the country and is held in private collections internationally.</p>
        """

        contact_content = """
        <h2>Contact Elliot Spencer Morgan</h2>
        <p>For inquiries about artwork, commissions, or exhibitions, please reach out using the form below or via email.</p>
        
        <div class="contact-form">
            <p>Email: artist@elliotspencermorgan.com</p>
            <p>Studio: Available by appointment</p>
        </div>
        """

        pages = []
        
        # About page
        about_page = self.create_page_xml(
            "About", 
            about_content, 
            len(self.artworks) + 1,
            "about",
            nsmap
        )
        pages.append(about_page)
        
        # Contact page
        contact_page = self.create_page_xml(
            "Contact", 
            contact_content, 
            len(self.artworks) + 2,
            "contact",
            nsmap
        )
        pages.append(contact_page)
        
        return pages

    def determine_category(self, medium):
        """Determine category based on medium"""
        medium_lower = medium.lower()
        if any(
            x in medium_lower
            for x in ["painting", "ink", "acrylic", "oil", "watercolor"]
        ):
            return "Painting"
        elif any(x in medium_lower for x in ["sculpture", "3d", "wood", "metal"]):
            return "Sculpture"
        elif any(x in medium_lower for x in ["print", "edition"]):
            return "Printmaking"
        elif "collage" in medium_lower:
            return "Collage"
        elif "installation" in medium_lower:
            return "Installation"
        else:
            return "Artwork"

    def generate_csv_export(self):
        """Generate CSV file with all artwork data"""
        csv_path = os.path.join(self.export_dir, "artwork-data.csv")
        with open(csv_path, "w", newline="", encoding="utf-8") as csvfile:
            fieldnames = [
                "Title",
                "Artist",
                "Price",
                "Medium",
                "Dimensions",
                "Description",
                "Year_Created",
                "Subject",
                "Styles",
                "Rarity",
                "Ready_To_Hang",
                "Framing",
                "Authenticity",
                "Packaging",
                "URL",
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            for artwork in self.artworks:
                writer.writerow(
                    {
                        "Title": artwork["title"],
                        "Artist": artwork["artist"],
                        "Price": artwork["price"],
                        "Medium": artwork["medium"],
                        "Dimensions": artwork["dimensions"],
                        "Description": artwork["description"],
                        "Year_Created": artwork["year_created"],
                        "Subject": artwork["subject"],
                        "Styles": artwork["styles"],
                        "Rarity": artwork["rarity"],
                        "Ready_To_Hang": artwork["ready_to_hang"],
                        "Framing": artwork["framing"],
                        "Authenticity": artwork["authenticity"],
                        "Packaging": artwork["packaging"],
                        "URL": artwork["url"],
                    }
                )

        print(f"✅ CSV export created: {csv_path}")

    def generate_theme_files(self):
        """Generate WordPress theme files optimized for artwork display with Saatchi-style design"""
        # style.css
        style_content = """
        /*
        Theme Name: Elliot Spencer Morgan Portfolio
        Theme URI: https://lookoverhere.xyz/elliot
        Author: Elliot Spencer Morgan
        Description: Custom theme for art portfolio with Saatchi Art inspired design
        Version: 1.0
        */
        
        /* Saatchi Art Color Scheme */
        :root {
            --saatchi-red: #e32c2b;
            --saatchi-black: #000000;
            --saatchi-white: #ffffff;
            --saatchi-gray: #f5f5f5;
            --saatchi-dark-gray: #333333;
        }
        
        /* Global Styles */
        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }
        
        body {
            font-family: 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: var(--saatchi-dark-gray);
            background: var(--saatchi-white);
        }
        
        a {
            text-decoration: none;
            color: var(--saatchi-red);
            transition: color 0.3s ease;
        }
        
        a:hover {
            color: var(--saatchi-black);
        }
        
        /* Header & Navigation */
        .site-header {
            background: var(--saatchi-white);
            border-bottom: 1px solid #eee;
            padding: 1rem 0;
            position: sticky;
            top: 0;
            z-index: 1000;
        }
        
        .header-container {
            max-width: 1200px;
            margin: 0 auto;
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 0 2rem;
        }
        
        .site-branding h1 {
            font-size: 1.8rem;
            font-weight: 700;
            color: var(--saatchi-black);
        }
        
        .main-navigation {
            display: flex;
        }
        
        .main-menu {
            display: flex;
            list-style: none;
            gap: 2rem;
        }
        
        .main-menu li a {
            color: var(--saatchi-dark-gray);
            font-weight: 500;
            padding: 0.5rem 0;
        }
        
        .main-menu li a:hover {
            color: var(--saatchi-red);
        }
        
        .main-menu li.current-menu-item a {
            color: var(--saatchi-red);
            border-bottom: 2px solid var(--saatchi-red);
        }
        
        /* Artwork Grid Layout */
        .artwork-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 2rem;
            padding: 2rem;
            max-width: 1400px;
            margin: 0 auto;
        }
        
        .artwork-item {
            background: var(--saatchi-white);
            border-radius: 8px;
            overflow: hidden;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            border: 1px solid #eee;
        }
        
        .artwork-item:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 30px rgba(0,0,0,0.15);
        }
        
        .artwork-item img {
            width: 100%;
            height: 250px;
            object-fit: cover;
        }
        
        .artwork-info {
            padding: 1.5rem;
        }
        
        .artwork-title {
            font-size: 1.2rem;
            font-weight: 600;
            margin: 0 0 0.5rem 0;
            color: var(--saatchi-black);
        }
        
        .artwork-price {
            font-size: 1.1rem;
            font-weight: 700;
            color: var(--saatchi-red);
            margin: 0 0 0.5rem 0;
        }
        
        .artwork-medium {
            color: var(--saatchi-dark-gray);
            margin: 0 0 0.5rem 0;
            font-size: 0.9rem;
        }
        
        /* Single Artwork Page */
        .artwork-detail-page {
            max-width: 1200px;
            margin: 2rem auto;
            padding: 0 2rem;
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 3rem;
            align-items: start;
        }
        
        .artwork-gallery {
            position: sticky;
            top: 2rem;
        }
        
        .artwork-gallery img {
            width: 100%;
            height: auto;
            border-radius: 8px;
            margin-bottom: 1rem;
        }
        
        .artwork-meta {
            margin-bottom: 2rem;
        }
        
        .artwork-description {
            margin-bottom: 2rem;
        }
        
        .artwork-details ul {
            list-style: none;
        }
        
        .artwork-details li {
            padding: 0.5rem 0;
            border-bottom: 1px solid #eee;
        }
        
        .artwork-details li:last-child {
            border-bottom: none;
        }
        
        /* Pages */
        .page-content {
            max-width: 800px;
            margin: 2rem auto;
            padding: 0 2rem;
        }
        
        .page-content h2 {
            color: var(--saatchi-black);
            margin-bottom: 1.5rem;
        }
        
        .page-content h3 {
            color: var(--saatchi-dark-gray);
            margin: 1.5rem 0 1rem 0;
        }
        
        /* Contact Form */
        .contact-form {
            margin: 2rem 0;
        }
        
        .form-group {
            margin-bottom: 1.5rem;
        }
        
        .form-group label {
            display: block;
            margin-bottom: 0.5rem;
            font-weight: 600;
        }
        
        .form-group input,
        .form-group textarea {
            width: 100%;
            padding: 0.75rem;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-family: inherit;
        }
        
        .form-group textarea {
            min-height: 150px;
            resize: vertical;
        }
        
        button[type="submit"] {
            background: var(--saatchi-red);
            color: var(--saatchi-white);
            padding: 1rem 2rem;
            border: none;
            border-radius: 4px;
            font-weight: 600;
            cursor: pointer;
            transition: background 0.3s ease;
        }
        
        button[type="submit"]:hover {
            background: #c52120;
        }
        
        .contact-info {
            margin-top: 2rem;
            padding: 1.5rem;
            background: var(--saatchi-gray);
            border-radius: 8px;
        }
        
        /* Footer */
        .site-footer {
            background: var(--saatchi-black);
            color: var(--saatchi-white);
            text-align: center;
            padding: 2rem;
            margin-top: 4rem;
        }
        
        /* Responsive Design */
        @media (max-width: 768px) {
            .header-container {
                flex-direction: column;
                gap: 1rem;
            }
            
            .main-menu {
                gap: 1rem;
            }
            
            .artwork-grid {
                grid-template-columns: 1fr;
                padding: 1rem;
            }
            
            .artwork-detail-page {
                grid-template-columns: 1fr;
                gap: 2rem;
                padding: 0 1rem;
            }
            
            .artwork-gallery {
                position: static;
            }
            
            .page-content {
                padding: 0 1rem;
            }
        }
        
        @media (max-width: 480px) {
            .main-menu {
                flex-wrap: wrap;
                justify-content: center;
            }
            
            .artwork-item img {
                height: 200px;
            }
        }
        """

        with open(os.path.join(self.theme_dir, "style.css"), "w") as f:
            f.write(style_content)

        # functions.php
        functions_content = """
        <?php
        function esm_portfolio_setup() {
            add_theme_support('post-thumbnails');
            add_theme_support('title-tag');
            add_theme_support('html5', array('search-form', 'comment-form', 'comment-list', 'gallery', 'caption'));
            
            // Register navigation menus
            register_nav_menus(array(
                'primary' => __('Primary Menu', 'esm-portfolio'),
            ));
            
            // Custom image sizes
            add_image_size('artwork-thumbnail', 400, 300, true);
            add_image_size('artwork-large', 1200, 800, false);
        }
        add_action('after_setup_theme', 'esm_portfolio_setup');
        
        function esm_portfolio_scripts() {
            wp_enqueue_style('esm-portfolio-style', get_stylesheet_uri());
            
            // Google Fonts
            wp_enqueue_style('esm-google-fonts', 'https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap', array(), null);
        }
        add_action('wp_enqueue_scripts', 'esm_portfolio_scripts');
        
        // Add custom post meta for artwork details
        function get_artwork_meta($meta_key) {
            global $post;
            return get_post_meta($post->ID, $meta_key, true);
        }
        
        // Create custom menu walker for simple navigation
        class Simple_Menu_Walker extends Walker_Nav_Menu {
            function start_el(&$output, $item, $depth = 0, $args = array(), $id = 0) {
                $output .= '<li class="' . implode(' ', $item->classes) . '"><a href="' . $item->url . '">' . $item->title . '</a>';
            }
            
            function end_el(&$output, $item, $depth = 0, $args = array()) {
                $output .= '</li>';
            }
        }
        ?>
        """

        with open(os.path.join(self.theme_dir, "functions.php"), "w") as f:
            f.write(functions_content)

        # header.php
        header_content = """
        <!DOCTYPE html>
        <html <?php language_attributes(); ?>>
        <head>
            <meta charset="<?php bloginfo('charset'); ?>">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <?php wp_head(); ?>
        </head>
        <body <?php body_class(); ?>>
        
        <header class="site-header">
            <div class="header-container">
                <div class="site-branding">
                    <h1><a href="<?php echo home_url(); ?>">Elliot Spencer Morgan</a></h1>
                </div>
                
                <nav class="main-navigation">
                    <?php
                    wp_nav_menu(array(
                        'theme_location' => 'primary',
                        'menu_class' => 'main-menu',
                        'container' => false,
                        'walker' => new Simple_Menu_Walker(),
                        'fallback_cb' => false
                    ));
                    ?>
                </nav>
            </div>
        </header>
        
        <main class="site-main">
        """

        with open(os.path.join(self.theme_dir, "header.php"), "w") as f:
            f.write(header_content)

        # footer.php
        footer_content = """
        </main>
        
        <footer class="site-footer">
            <div class="footer-content">
                <p>&copy; <?php echo date('Y'); ?> Elliot Spencer Morgan. All rights reserved.</p>
            </div>
        </footer>
        
        <?php wp_footer(); ?>
        </body>
        </html>
        """

        with open(os.path.join(self.theme_dir, "footer.php"), "w") as f:
            f.write(footer_content)

        # single.php (for individual artwork pages)
        single_content = """
        <?php get_header(); ?>
        
        <div class="artwork-detail-page">
            <article id="post-<?php the_ID(); ?>" <?php post_class(); ?>>
                
                <div class="artwork-gallery">
                    <?php if (has_post_thumbnail()) : ?>
                        <?php the_post_thumbnail('artwork-large', array('class' => 'artwork-image')); ?>
                    <?php endif; ?>
                </div>
                
                <div class="artwork-info">
                    <h1 class="artwork-title"><?php the_title(); ?></h1>
                    
                    <div class="artwork-meta">
                        <div class="artwork-price"><?php echo get_artwork_meta('artwork_price'); ?></div>
                        <div class="artwork-medium"><?php echo get_artwork_meta('artwork_medium'); ?></div>
                        <div class="artwork-dimensions"><?php echo get_artwork_meta('artwork_dimensions'); ?></div>
                    </div>
                    
                    <div class="artwork-description">
                        <?php the_content(); ?>
                    </div>
                    
                    <div class="artwork-details">
                        <h3>Artwork Details</h3>
                        <ul>
                            <li><strong>Year Created:</strong> <?php echo get_artwork_meta('artwork_year'); ?></li>
                            <li><strong>Subject:</strong> <?php echo get_artwork_meta('artwork_subject'); ?></li>
                            <li><strong>Styles:</strong> <?php echo get_artwork_meta('artwork_styles'); ?></li>
                            <li><strong>Rarity:</strong> <?php echo get_artwork_meta('artwork_rarity'); ?></li>
                            <li><strong>Ready to Hang:</strong> <?php echo get_artwork_meta('artwork_ready_to_hang'); ?></li>
                            <li><strong>Framing:</strong> <?php echo get_artwork_meta('artwork_framing'); ?></li>
                            <li><strong>Authenticity:</strong> <?php echo get_artwork_meta('artwork_authenticity'); ?></li>
                            <li><strong>Packaging:</strong> <?php echo get_artwork_meta('artwork_packaging'); ?></li>
                        </ul>
                    </div>
                </div>
                
            </article>
        </div>
        
        <?php get_footer(); ?>
        """

        with open(os.path.join(self.theme_dir, "single.php"), "w") as f:
            f.write(single_content)

        # index.php (main gallery page)
        index_content = """
        <?php get_header(); ?>
        
        <div class="artwork-grid">
            <?php if (have_posts()) : while (have_posts()) : the_post(); ?>
                <article class="artwork-item">
                    <a href="<?php the_permalink(); ?>">
                        <?php if (has_post_thumbnail()) : ?>
                            <?php the_post_thumbnail('artwork-thumbnail'); ?>
                        <?php endif; ?>
                        
                        <div class="artwork-info">
                            <h2 class="artwork-title"><?php the_title(); ?></h2>
                            <div class="artwork-price"><?php echo get_artwork_meta('artwork_price'); ?></div>
                            <div class="artwork-medium"><?php echo get_artwork_meta('artwork_medium'); ?></div>
                        </div>
                    </a>
                </article>
            <?php endwhile; endif; ?>
        </div>
        
        <?php get_footer(); ?>
        """

        with open(os.path.join(self.theme_dir, "index.php"), "w") as f:
            f.write(index_content)

        # page.php (for About and Contact pages)
        page_content = """
        <?php get_header(); ?>
        
        <div class="page-content">
            <article id="post-<?php the_ID(); ?>" <?php post_class(); ?>>
                <header class="page-header">
                    <h1><?php the_title(); ?></h1>
                </header>
                
                <div class="entry-content">
                    <?php the_content(); ?>
                </div>
            </article>
        </div>
        
        <?php get_footer(); ?>
        """

        with open(os.path.join(self.theme_dir, "page.php"), "w") as f:
            f.write(page_content)

        print(f"✅ Theme files created in: {self.theme_dir}")

    def generate_import_instructions(self):
        """Generate detailed import instructions"""

        instructions = """
        # WordPress Portfolio Import Instructions
        
        ## Files Generated:
        1. `portfolio-export.xml` - WordPress WXR import file with all artwork data
        2. `artwork-data.csv` - CSV backup with all artwork information
        3. `wp-content/uploads/` - All downloaded high-quality images
        4. `theme/` - Custom WordPress theme with Saatchi Art inspired design
        
        ## Installation Steps:
        
        1. **Install WordPress**
        - Fresh WordPress installation on your server or local environment
        - Recommended: Use Local by Flywheel for local development
        
        2. **Import Artwork Data**
        - Go to WordPress Admin -> Tools -> Import
        - Install "WordPress Importer" plugin if not already installed
        - Upload and import `portfolio-export.xml`
        - Check "Download and import file attachments" option
        - Assign authors to existing user (usually 'admin')
        
        3. **Upload Images** (if not imported automatically)
        - Upload the entire `wp-content/uploads/` folder to your WordPress installation
        - Place it in the `/wp-content/uploads/` directory
        
        4. **Install and Activate Theme**
        - Zip the `theme/` folder (right-click -> compress)
        - WordPress Admin -> Appearance -> Themes -> Add New -> Upload Theme
        - Upload the zip file and activate the theme
        
        5. **Set Up Navigation Menu**
        - Go to Appearance -> Menus
        - Create a new menu named "Primary Navigation"
        - Add the following items:
          * Home (custom link to your homepage)
          * Painting (category link)
          * Sculpture (category link) 
          * Collage (category link)
          * Printmaking (category link)
          * Installation (category link)
          * About (page link)
          * Contact (page link)
        - Set the menu location to "Primary Menu"
        
        6. **Configure Permalinks**
        - Go to Settings -> Permalinks
        - Choose "Post name" structure for clean URLs
        - Save changes
        
        7. **Configure Reading Settings**
        - Go to Settings -> Reading
        - Set "Your homepage displays" to "Latest posts"
        - This will show your artwork gallery on the homepage
        
        8. **Set Up Categories**
        - The import should have created these categories automatically:
          * Painting
          * Sculpture  
          * Collage
          * Printmaking
          * Installation
          * Artwork
        
        ## Customization Options:
        
        ### Modify Artwork Display:
        Edit these files in the `theme/` directory:
        - `style.css` - Change colors, fonts, and layout
        - `index.php` - Modify gallery grid display
        - `single.php` - Change individual artwork page layout
        - `page.php` - Modify About and Contact pages
        
        ### Add Custom Fields:
        The script includes these custom fields for each artwork:
        - Price, Medium, Dimensions, Year, Subject, Styles
        - Rarity, Framing, Authenticity, Packaging
        
        ## Troubleshooting:
        
        1. **Import Fails**: 
        - Increase PHP memory limit in wp-config.php: `define('WP_MEMORY_LIMIT', '256M');`
        - Import in smaller batches if you have many artworks
        
        2. **Images Not Showing**:
        - Check file permissions on uploads directory
        - Verify images were uploaded correctly
        
        3. **Theme Not Working**:
        - Ensure all theme files are present
        - Check for PHP errors in debug mode
        
        ## Next Steps:
        
        1. **Review All Artwork Pages**: Check that all data imported correctly
        2. **Optimize Images**: Compress images for faster loading
        3. **Test Navigation**: Ensure all menu links work properly
        4. **Test Contact Form**: Consider installing a contact form plugin
        5. **Configure SEO**: Set up meta descriptions and titles
        6. **Test Responsiveness**: Check mobile display
        
        Your portfolio website is now ready! All artwork is displayed with:
        - Professional gallery layout based on Saatchi Art design
        - Detailed artwork information
        - High-quality images
        - Mobile-responsive design
        - Clean navigation with your specified categories
        """

        with open(
            os.path.join(self.base_dir, "IMPORT_INSTRUCTIONS.md"), "w", encoding="utf-8"
        ) as f:
            f.write(instructions)

        print(f"✅ Import instructions created")

    def run(self):
        """Main function to generate WordPress portfolio"""
        print("🚀 Generating WordPress Portfolio...")
        self.create_directory_structure()

        # Extract artist information first
        self.extract_artist_info()

        # Get artwork URLs
        artwork_urls = self.get_artwork_urls()
        total_artworks = len(artwork_urls)

        print(f"🎨 Processing {total_artworks} artworks...")

        # Scrape and process each artwork
        for i, url in enumerate(artwork_urls, 1):
            print(f"\n📄 Processing {i}/{total_artworks}: {url}")

            artwork_data = self.extract_artwork_data(url)
            if artwork_data:
                # Download images
                image_paths = self.download_images(artwork_data)
                artwork_data["wordpress_images"] = image_paths
                self.artworks.append(artwork_data)
                print(f"✅ Added: {artwork_data['title']}")

            # Respectful delay
            time.sleep(2)

        # Generate WordPress files
        print("\n🛠️  Generating WordPress export files...")
        self.generate_wordpress_xml()
        self.generate_csv_export()
        self.generate_theme_files()
        self.generate_import_instructions()

        # Summary
        print(f"\n🎉 WordPress Portfolio Generation Complete!")
        print(f"📁 Output directory: {self.base_dir}")
        print(f"🖼️  Artworks processed: {len(self.artworks)}")
        print(f"📄 Export file: {self.export_dir}/portfolio-export.xml")
        print(f"🎨 Theme files: {self.theme_dir}/")
        print(f"📖 Instructions: {self.base_dir}/IMPORT_INSTRUCTIONS.md")


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