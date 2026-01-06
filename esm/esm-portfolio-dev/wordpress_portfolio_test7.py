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
        """Generate homepage content with categorized artwork grid"""
        categories = {}
        for artwork in self.artworks:
            category = artwork.get('category', 'Artwork')
            if category not in categories:
                categories[category] = []
            categories[category].append(artwork)
        
        category_sections = []
        for category, artworks in categories.items():
            section_html = f'''
            <section class="category-section" id="{category.lower()}">
                <h2 class="category-title">{category}</h2>
                <div class="artwork-grid">
            '''
            
            for artwork in artworks:
                if artwork.get('wordpress_image'):
                    section_html += f'''
                    <div class="artwork-item">
                        <a href="{artwork['url']}" target="_blank" class="artwork-link">
                            <img src="{artwork['wordpress_image']['url']}" alt="{artwork['title']}" class="artwork-image">
                            <div class="artwork-overlay">
                                <h3 class="artwork-title">{artwork['title']}</h3>
                            </div>
                        </a>
                    </div>
                    '''
            
            section_html += '''
                </div>
            </section>
            '''
            category_sections.append(section_html)
        
        homepage_content = f'''
        <div class="homepage-hero">
            <h1>Elliot Spencer Morgan</h1>
            <p class="tagline">Contemporary Art Portfolio</p>
        </div>
        
        <nav class="category-nav">
            <ul>
        '''
        
        for category in categories.keys():
            homepage_content += f'<li><a href="#{category.lower()}">{category}</a></li>'
        
        homepage_content += '''
            </ul>
        </nav>
        
        ''' + '\n'.join(category_sections)
        
        return homepage_content

    def generate_wordpress_xml(self):
        """Generate WordPress WXR export file with only 3 pages"""
        nsmap = {
            'excerpt': "http://wordpress.org/export/1.2/excerpt/",
            'content': "http://purl.org/rss/1.0/modules/content/",
            'wfw': "http://wellformedweb.org/CommentAPI/",
            'dc': "http://purl.org/dc/elements/1.1/",
            'wp': "http://wordpress.org/export/1.2/"
        }
        
        rss = ET.Element("rss", version="2.0", nsmap=nsmap)
        channel = ET.SubElement(rss, "channel")
        
        ET.SubElement(channel, "title").text = "Elliot Spencer Morgan - Art Portfolio"
        ET.SubElement(channel, "link").text = self.base_url
        ET.SubElement(channel, "description").text = "Artwork Portfolio of Elliot Spencer Morgan"
        ET.SubElement(channel, "pubDate").text = datetime.now().strftime("%a, %d %b %Y %H:%M:%S +0000")
        ET.SubElement(channel, "language").text = "en-US"
        
        ET.SubElement(channel, "{%s}wxr_version" % nsmap['wp']).text = "1.2"
        ET.SubElement(channel, "{%s}base_site_url" % nsmap['wp']).text = self.base_url
        ET.SubElement(channel, "{%s}base_blog_url" % nsmap['wp']).text = self.base_url

        author = ET.SubElement(channel, "{%s}author" % nsmap['wp'])
        ET.SubElement(author, "{%s}author_id" % nsmap['wp']).text = "1"
        ET.SubElement(author, "{%s}author_login" % nsmap['wp']).text = "admin"
        ET.SubElement(author, "{%s}author_email" % nsmap['wp']).text = "admin@lookoverhere.xyz"
        ET.SubElement(author, "{%s}author_display_name" % nsmap['wp']).text = "admin"
        ET.SubElement(author, "{%s}author_first_name" % nsmap['wp']).text = "Admin"
        ET.SubElement(author, "{%s}author_last_name" % nsmap['wp']).text = "User"

        homepage_content = self.generate_homepage_content()
        
        pages = [
            {
                "title": "Home",
                "slug": "home",
                "content": homepage_content,
                "is_homepage": True
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
                """
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
                """
            }
        ]
        
        for i, page in enumerate(pages, 1):
            item = ET.SubElement(channel, "item")
            
            ET.SubElement(item, "title").text = page["title"]
            ET.SubElement(item, "link").text = f"{self.base_url}/{page['slug']}" if page['slug'] != "home" else self.base_url
            ET.SubElement(item, "pubDate").text = datetime.now().strftime("%a, %d %b %Y %H:%M:%S +0000")
            ET.SubElement(item, "{%s}creator" % nsmap['dc']).text = "admin"
            
            guid = ET.SubElement(item, "guid", isPermaLink="false")
            guid.text = f"{self.base_url}/?page_id={i}"
            
            ET.SubElement(item, "description").text = ""
            
            content_elem = ET.SubElement(item, "{%s}encoded" % nsmap['content'])
            content_elem.text = CDATA(page["content"])
            
            ET.SubElement(item, "{%s}encoded" % nsmap['excerpt']).text = CDATA(f"{page['title']} - Elliot Spencer Morgan")
            ET.SubElement(item, "{%s}post_id" % nsmap['wp']).text = str(i)
            ET.SubElement(item, "{%s}post_date" % nsmap['wp']).text = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ET.SubElement(item, "{%s}post_date_gmt" % nsmap['wp']).text = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ET.SubElement(item, "{%s}comment_status" % nsmap['wp']).text = "closed"
            ET.SubElement(item, "{%s}ping_status" % nsmap['wp']).text = "closed"
            ET.SubElement(item, "{%s}post_name" % nsmap['wp']).text = page["slug"]
            ET.SubElement(item, "{%s}status" % nsmap['wp']).text = "publish"
            ET.SubElement(item, "{%s}post_parent" % nsmap['wp']).text = "0"
            ET.SubElement(item, "{%s}menu_order" % nsmap['wp']).text = str(i)
            ET.SubElement(item, "{%s}post_type" % nsmap['wp']).text = "page"
            ET.SubElement(item, "{%s}post_password" % nsmap['wp']).text = ""
            
            if page.get("is_homepage"):
                show_on_front = ET.SubElement(channel, "{%s}option" % nsmap['wp'])
                ET.SubElement(show_on_front, "{%s}option_name" % nsmap['wp']).text = "show_on_front"
                ET.SubElement(show_on_front, "{%s}option_value" % nsmap['wp']).text = "page"
                
                page_on_front = ET.SubElement(channel, "{%s}option" % nsmap['wp'])
                ET.SubElement(page_on_front, "{%s}option_name" % nsmap['wp']).text = "page_on_front"
                ET.SubElement(page_on_front, "{%s}option_value" % nsmap['wp']).text = str(i)

        xml_str = ET.tostring(rss, pretty_print=True, encoding="utf-8", xml_declaration=True).decode("utf-8")
        xml_path = os.path.join(self.export_dir, "portfolio-export.xml")
        with open(xml_path, "w", encoding="utf-8") as f:
            f.write(xml_str)
        
        print(f"✅ WordPress export file created: {xml_path}")

    def generate_theme_files(self):
        """Generate complete WordPress theme without PIL dependency"""
        # style.css
        style_content = f"""/*
Theme Name: ESM Portfolio
Theme URI: {self.base_url}
Author: Elliot Spencer Morgan
Description: Minimalist portfolio theme for Elliot Spencer Morgan
Version: 1.0
Text Domain: esm-portfolio
*/

:root {{
    --primary-color: #2c3e50;
    --secondary-color: #e74c3c;
    --background-color: #ffffff;
    --text-color: #333333;
    --border-color: #e0e0e0;
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
}}

.main-navigation a:hover {{
    opacity: 0.8;
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

.category-nav {{
    background: #f8f9fa;
    padding: 1rem 0;
    position: sticky;
    top: 60px;
    z-index: 999;
}}

.category-nav ul {{
    display: flex;
    justify-content: center;
    list-style: none;
    gap: 2rem;
}}

.category-nav a {{
    color: var(--primary-color);
    text-decoration: none;
    font-weight: 500;
}}

.category-nav a:hover {{
    color: var(--secondary-color);
}}

.category-section {{
    padding: 4rem 0;
}}

.category-title {{
    text-align: center;
    font-size: 2.5rem;
    margin-bottom: 3rem;
    color: var(--primary-color);
}}

.artwork-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 2rem;
    padding: 0 20px;
}}

.artwork-item {{
    position: relative;
    overflow: hidden;
    border-radius: 8px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    transition: transform 0.3s, box-shadow 0.3s;
}}

.artwork-item:hover {{
    transform: translateY(-5px);
    box-shadow: 0 8px 15px rgba(0, 0, 0, 0.2);
}}

.artwork-link {{
    display: block;
    text-decoration: none;
    color: inherit;
}}

.artwork-image {{
    width: 100%;
    height: 300px;
    object-fit: cover;
    display: block;
}}

.artwork-overlay {{
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    background: linear-gradient(transparent, rgba(0, 0, 0, 0.8));
    color: white;
    padding: 2rem 1rem 1rem;
    transform: translateY(100%);
    transition: transform 0.3s;
}}

.artwork-item:hover .artwork-overlay {{
    transform: translateY(0);
}}

.artwork-title {{
    font-size: 1.1rem;
    margin: 0;
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

/* Responsive */
@media (max-width: 768px) {{
    .artwork-grid {{
        grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
        gap: 1rem;
    }}
    
    .homepage-hero h1 {{
        font-size: 2rem;
    }}
    
    .category-nav ul {{
        flex-wrap: wrap;
        gap: 1rem;
    }}
    
    .main-navigation ul {{
        gap: 1rem;
    }}
}}

@media (max-width: 480px) {{
    .artwork-grid {{
        grid-template-columns: 1fr;
    }}
    
    .header-container {{
        flex-direction: column;
        gap: 1rem;
    }}
}}
"""

        with open(os.path.join(self.theme_dir, "style.css"), "w") as f:
            f.write(style_content)

        # index.php
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
        <?php while (have_posts()) : the_post(); ?>
            <article id="post-<?php the_ID(); ?>" <?php post_class(); ?>>
                <div class="entry-content">
                    <?php the_content(); ?>
                </div>
            </article>
        <?php endwhile; ?>
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
    
    register_nav_menus(array(
        'primary' => __('Primary Menu', 'esm-portfolio'),
    ));
    
    add_image_size('artwork-thumbnail', 400, 300, true);
}
add_action('after_setup_theme', 'esm_portfolio_setup');

function esm_portfolio_scripts() {
    wp_enqueue_style('esm-portfolio-style', get_stylesheet_uri());
}
add_action('wp_enqueue_scripts', 'esm_portfolio_scripts');

class ESM_Menu_Walker extends Walker_Nav_Menu {
    public function start_l(&$output, $item, $depth = 0, $args = array(), $id = 0) {
        $output .= '<li class="menu-item"><a href="' . $item->url . '">' . $item->title . '</a>';
    }
    
    public function end_l(&$output, $item, $depth = 0, $args = array()) {
        $output .= '</li>';
    }
}
?>
"""

        with open(os.path.join(self.theme_dir, "functions.php"), "w") as f:
            f.write(functions_content)

        # header.php
        header_content = """<?php
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
                <?php
                wp_nav_menu(array(
                    'theme_location' => 'primary',
                    'menu_class' => 'nav-menu',
                    'container' => false,
                    'walker' => new ESM_Menu_Walker(),
                ));
                ?>
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

        # front-page.php
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

        # page.php
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

        # Create a simple screenshot.txt file instead of PNG
        screenshot_content = """ESM Portfolio Theme Screenshot
=============================

This theme features a clean, modern design for Elliot Spencer Morgan's art portfolio.

Key Features:
- Homepage with categorized artwork grid
- Clickable images linking to Saatchi Art
- About page with artist bio and statement
- Contact page with information
- Mobile-responsive design
- Clean, minimalist aesthetic

To add a proper screenshot:
1. Take a screenshot of your live site
2. Save it as screenshot.png (1200x900 pixels)
3. Upload it to the theme folder
"""

        with open(os.path.join(self.theme_dir, "screenshot.txt"), "w") as f:
            f.write(screenshot_content)

        print(f"✅ Complete theme files created in: {self.theme_dir}")
        print("ℹ️  Screenshot generation skipped (PIL not available). Theme will work without it.")

    def generate_import_instructions(self):
        """Generate import instructions"""
        instructions = f"""
        # WordPress Portfolio Import Instructions
        
        ## Files Generated:
        1. `portfolio-export.xml` - WordPress WXR import file with 3 pages
        2. `wp-content/uploads/` - All downloaded artwork images
        3. `theme/esm-portfolio/` - Complete WordPress theme
        
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
        
        5. **Set Up Navigation**:
           - Appearance → Menus
           - Create menu "Primary Navigation" with:
             * Home (custom link to {self.base_url})
             * About (page link)
             * Contact (page link)
           - Set menu location to "Primary Menu"
        
        6. **Set Homepage**:
           - Settings → Reading
           - "Your homepage displays" → "A static page"
           - Homepage: Select "Home"
        
        ## Theme Features:
        - Complete WordPress theme with all required template files
        - Homepage with categorized artwork grid
        - Clickable images linking to Saatchi Art pages
        - About page with artist bio
        - Contact page with information
        - Mobile-responsive design
        
        ## Important Notes:
        - Zip the 'esm-portfolio' folder (not the parent 'theme' folder)
        - All required WordPress template files are included
        - Theme meets WordPress standards
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
        print(f"🌐 Base URL: {self.base_url}")
        print(f"📄 Export file: {self.export_dir}/portfolio-export.xml")
        print(f"🎨 Theme folder: {self.theme_dir}/")
        print(f"📖 Instructions: {self.base_dir}/IMPORT_INSTRUCTIONS.md")
        print(f"\\n💡 Important: Zip the 'esm-portfolio' folder for theme installation")


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