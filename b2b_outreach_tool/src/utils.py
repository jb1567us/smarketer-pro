import requests
from bs4 import BeautifulSoup
import time

def get_page_content(url, timeout=15):
    """
    Fetches the homepage content of a URL.
    Returns a dictionary with 'html' and 'clean_text', or None if failed.
    """
    if not url.startswith('http'):
        url = 'https://' + url

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    try:
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Keep a copy of the full HTML for email extraction
        html_content = response.text

        # Remove scripts and styles for text analysis
        for script in soup(["script", "style", "nav", "footer", "header"]):
            script.decompose()
            
        # Get visible text
        text = soup.get_text(separator=' ', strip=True)
        
        return {
            "html": html_content,
            "clean_text": text[:20000] # Limit text length
        }
        
    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return None
