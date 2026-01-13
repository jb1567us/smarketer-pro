import requests
from bs4 import BeautifulSoup
import logging
import urllib.parse
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/weekly_seo_audit.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("WeeklySEOAudit")

class SEOAuditor:
    def __init__(self, base_url):
        self.base_url = base_url.rstrip('/')
        self.visited_urls = set()
        self.broken_links = []

    def get_links(self, url):
        """Extracts all internal links from a page."""
        try:
            response = requests.get(url, timeout=15)
            if response.status_code != 200:
                return []
            
            soup = BeautifulSoup(response.text, 'html.parser')
            links = []
            for a in soup.find_all('a', href=True):
                href = a['href']
                full_url = urllib.parse.urljoin(url, href)
                # Only follow internal links
                if full_url.startswith(self.base_url) and "#" not in full_url:
                    links.append(full_url)
            return links
        except Exception as e:
            logger.error(f"Error fetching links from {url}: {str(e)}")
            return []

    def scan(self, max_pages=20):
        """Scans the site for broken links up to max_pages."""
        to_visit = [self.base_url]
        pages_scanned = 0

        while to_visit and pages_scanned < max_pages:
            current_url = to_visit.pop(0)
            if current_url in self.visited_urls:
                continue
            
            self.visited_urls.add(current_url)
            pages_scanned += 1
            logger.info(f"Scanning ({pages_scanned}/{max_pages}): {current_url}")

            try:
                response = requests.get(current_url, timeout=10)
                if response.status_code == 404:
                    self.broken_links.append(current_url)
                    logger.warning(f"BROKEN LINK FOUND: {current_url}")
                
                # Expand search
                new_links = self.get_links(current_url)
                for link in new_links:
                    if link not in self.visited_urls:
                        to_visit.append(link)

            except Exception as e:
                logger.error(f"Failed to scan {current_url}: {str(e)}")

        logger.info(f"Scan Complete. Scanned {pages_scanned} pages. Found {len(self.broken_links)} broken links.")
        return self.broken_links

if __name__ == "__main__":
    SITE_URL = os.getenv("WP_SITE_URL", "https://example.com")
    auditor = SEOAuditor(SITE_URL)
    auditor.scan(max_pages=10) # Default to 10 for quick testing
