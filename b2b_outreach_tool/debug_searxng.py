import requests
from bs4 import BeautifulSoup

url = "http://localhost:8080/search"
params = {"q": "marketing agencies in Austin"}
try:
    resp = requests.get(url, params=params)
    print(f"Status: {resp.status_code}")
    if resp.status_code == 200:
        soup = BeautifulSoup(resp.text, 'html.parser')
        articles = soup.select('article.result')
        print(f"Found {len(articles)} 'article.result' items.")
        
        # Try finding ANY links
        links = soup.find_all('a', href=True)
        print(f"Total links on page: {len(links)}")
        
        # Save HTML for inspection
        with open("debug_search.html", "w", encoding="utf-8") as f:
            f.write(resp.text)
            
except Exception as e:
    print(f"Error: {e}")
