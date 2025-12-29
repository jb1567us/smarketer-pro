import requests
from bs4 import BeautifulSoup
import time
import random

def search_google(query, num_results=10):
    """
    Performs a Google search and returns a list of URLs.
    Warning: This is a basic implementation and may be blocked by Google.
    """
    search_url = "https://www.google.com/search"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    params = {
        "q": query,
        "num": num_results
    }

    try:
        print(f"Searching Google for: {query}")
        response = requests.get(search_url, headers=headers, params=params)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        links = []

        # This selector is brittle and changes often. 
        # Targeting standard organic results (usually in div.g or similar)
        # We look for 'a' tags with href beginning with http, excluding google links.
        for a in soup.find_all('a', href=True):
            href = a['href']
            # Basic filtering to strip out google internal links
            if href.startswith('http') and 'google.com' not in href:
                 # Try to identify actual result links (often they have h3 children)
                 if a.find('h3'):
                     links.append(href)
        
        # Deduplicate
        unique_links = list(set(links))
        print(f"Found {len(unique_links)} links.")
        return unique_links[:num_results]

    except Exception as e:
        print(f"Error scraping Google: {e}")
        return []

def search_ddg(query, num_results=10):
    """
    Fallback: Scrape DuckDuckGo HTML version which is friendlier.
    """
    url = "https://html.duckduckgo.com/html/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    data = {'q': query}
    
    try:
        print(f"Searching DuckDuckGo for: {query}")
        response = requests.post(url, data=data, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        links = []
        
        for a in soup.select('.result__a'):
            href = a.get('href')
            if href:
                links.append(href)
                
        unique_links = list(set(links))
        print(f"Found {len(unique_links)} links.")
        return unique_links[:num_results]
        
    except Exception as e:
        print(f"Error scraping DuckDuckGo: {e}")
        return []

def search_searxng(query, num_results=10, base_url="http://localhost:8080/search"):
    """
    Uses local SearXNG instance to find URLs via HTML scraping.
    """
    params = {
        "q": query,
        # "format": "json" # API blocked, using HTML
    }
    # User-Agent is still good practice
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    try:
        print(f"Searching SearXNG (HTML) for: {query}")
        response = requests.get(base_url, params=params, headers=headers)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        links = []
        
        # SearXNG results are usually in <article class="result"> 
        # and URLs are in <a class="url_wrapper" href="..."> or <a href="..."> inside h3
        for article in soup.select('article.result'):
            a_tag = article.find('a', href=True)
            if a_tag:
                url = a_tag['href']
                # Skip internal links if any (usually starting with /)
                if url.startswith('http'):
                    links.append(url)
        
        unique_links = list(set(links))
        print(f"Found {len(unique_links)} links.")
        return unique_links[:num_results]

    except Exception as e:
        print(f"Error scraping SearXNG: {e}")
        return []

if __name__ == "__main__":
    # Test
    # results = search_google("plumbers in new york")
    # results = search_ddg("software companies in austin")
    results = search_searxng("software companies in austin")
    for link in results:
        print(link)
