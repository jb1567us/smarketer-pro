import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin

EMAIL_REGEX = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'

# Blocklist of common junk emails
EMAIL_BLOCKLIST = {
    'sentry', 'noreply', 'no-reply', 'admin', 'hostmaster', 'postmaster', 
    'webmaster', 'support', 'info', 'hello', 'contact', 'example', 'domain',
    'privacy', 'legal', 'compliance', 'abuse'
}

# Actually 'info', 'hello', 'contact', 'support' are often GOOD targets for B2B. 
# I will refine the blocklist to only structural/garbage emails.
STRICT_BLOCKLIST = {
    'sentry', 'noreply', 'no-reply', 'example', 'domain', 'image', 'png', 'jpg', 'jpeg', 'gif', 'js', 'css', 
    'wix', 'wordpress', 'cloudflare', 'abuse'
}

def extract_emails_from_url(url):
    """
    Visits a URL and extracts emails from the page text.
    Timout is short to avoid hanging.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    found_emails = set()
    
    try:
        print(f"Scanning {url}...")
        response = requests.get(url, headers=headers, timeout=10)
        # We don't raise status, just skip on error
        if response.status_code != 200:
            return set()

        text = response.text
        
        # Simple regex search
        matches = re.findall(EMAIL_REGEX, text)
        for email in matches:
            email_lower = email.lower()
            # Filter extensions (sometimes images or files get matched)
            if email_lower.endswith(('.png', '.jpg', '.jpeg', '.gif', '.js', '.css')):
                continue
                
            username = email_lower.split('@')[0]
            if not any(blocked in username for blocked in STRICT_BLOCKLIST):
                found_emails.add(email_lower)
                
    except Exception as e:
        # print(f"Error scanning {url}: {e}")
        pass
        
    return found_emails

if __name__ == "__main__":
    # Test
    test_url = "https://www.example.com" # Replace with a real one for testing
    print(extract_emails_from_url(test_url))
