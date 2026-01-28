import os
import csv
import urllib.parse
import argparse
import sys
from typing import List, Optional

class SearchLinkGenerator:
    """
    Generates search URLs for safe, manual, or browser-based scraping.
    Supports Google, Bing, and DuckDuckGo.
    """
    def __init__(self, output_file: str = "data/generated_search_links.csv"):
        self.output_file = output_file
        self.ensure_output_dir()

    def ensure_output_dir(self):
        os.makedirs(os.path.dirname(self.output_file), exist_ok=True)

    def generate_url(self, platform: str, query: str) -> str:
        """
        Constructs the search URL for a specific platform.
        """
        encoded_query = urllib.parse.quote_plus(query)
        
        if platform.lower() == "google":
            return f"https://www.google.com/search?q={encoded_query}"
        elif platform.lower() == "bing":
            return f"https://www.bing.com/search?q={encoded_query}"
        elif platform.lower() == "duckduckgo":
            return f"https://duckduckgo.com/?q={encoded_query}"
        else:
            raise ValueError(f"Unsupported platform: {platform}")

    def generate_links(self, 
                       dorks: List[str], 
                       keywords: List[str], 
                       locations: List[str], 
                       platforms: List[str] = ["google"]):
        """
        Combines dorks, keywords, and locations into search queries and generates URLs.
        """
        results = []
        
        # If no keywords provided, just use dorks (or vice versa handled by loops)
        # We need at least one of each list to be non-empty effectively, 
        # but let's handle empty lists gracefully by treating them as [""]
        
        _dorks = dorks if dorks else [""]
        _keywords = keywords if keywords else [""]
        _locations = locations if locations else [""]
        
        print(f"🔗 Generating links for {len(platforms)} platform(s)...")

        count = 0
        for platform in platforms:
            for dork in _dorks:
                for keyword in _keywords:
                    for location in _locations:
                        # Construct the query string
                        components = [part for part in [dork, keyword, location] if part]
                        if not components:
                            continue
                            
                        full_query = " ".join(components)
                        url = self.generate_url(platform, full_query)
                        
                        row = {
                            "platform": platform,
                            "query": full_query,
                            "url": url,
                            "dork": dork,
                            "keyword": keyword,
                            "location": location
                        }
                        results.append(row)
                        count += 1

        self.save_to_csv(results)
        return results

    def save_to_csv(self, data: List[dict]):
        """
        Appends generated links to the CSV file.
        """
        file_exists = os.path.exists(self.output_file)
        
        with open(self.output_file, 'a', newline='', encoding='utf-8') as f:
            fieldnames = ["platform", "query", "url", "dork", "keyword", "location"]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            
            if not file_exists:
                writer.writeheader()
                
            for row in data:
                writer.writerow(row)
                
        print(f"✅ Saved {len(data)} links to {self.output_file}")
        print(f"   (Total file path: {os.path.abspath(self.output_file)})")

def parse_list_arg(arg_str: Optional[str]) -> List[str]:
    if not arg_str:
        return []
    # Split by semicolon or comma, strip whitespace
    delimiters = [";", ","]
    for d in delimiters:
        if d in arg_str:
            return [x.strip() for x in arg_str.split(d) if x.strip()]
    return [arg_str.strip()]

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate Search URLs for scraping.")
    
    parser.add_argument("--dorks", help="List of dorks (e.g., 'site:linkedin.com/in/')", default="")
    parser.add_argument("--keywords", help="List of keywords (e.g., 'CEO;CTO')", default="")
    parser.add_argument("--locations", help="List of locations (e.g., 'NY;London')", default="")
    parser.add_argument("--platforms", help="List of platforms (google,bing,duckduckgo)", default="google")
    parser.add_argument("--output", help="Output CSV file path", default="data/generated_search_links.csv")
    
    args = parser.parse_args()
    
    dorks_list = parse_list_arg(args.dorks)
    keywords_list = parse_list_arg(args.keywords)
    locations_list = parse_list_arg(args.locations)
    platforms_list = parse_list_arg(args.platforms)
    
    if not (dorks_list or keywords_list):
        print("❌ Error: You must provide at least --dorks or --keywords.")
        sys.exit(1)
        
    generator = SearchLinkGenerator(output_file=args.output)
    generator.generate_links(dorks_list, keywords_list, locations_list, platforms_list)
