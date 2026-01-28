import asyncio
import os
import csv
import sys
import argparse
from typing import List, Dict

# Ensure src is in path
sys.path.append(os.path.join(os.getcwd(), 'src'))

from search_providers.direct_browser import DirectBrowser

class MapsHarvester:
    """
    Harvester that searches DuckDuckGo for Google Maps listings for specific queries in specific cities.
    """
    def __init__(self, output_file="data/harvested_maps_links.csv"):
        self.output_file = output_file
        # Browser no longer needed for direct link generation
        self.ensure_output_dir()

    def ensure_output_dir(self):
        os.makedirs(os.path.dirname(self.output_file), exist_ok=True)

    async def harvest(self, queries: List[str], cities: List[Dict[str, str]]):
        """
        Generates Google Maps Search URLs for the parser.
        """
        all_results = []
        existing_urls = set()
        
        if os.path.exists(self.output_file):
            with open(self.output_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    existing_urls.add(row.get('maps_url'))

        print(f"🚜 MapsHarvester: Generating links for {len(cities)} cities and {len(queries)} queries.")

        for city_obj in cities:
            city = city_obj.get("city")
            country = city_obj.get("country", "")
            location = f"{city} {country}".strip()
            
            for query in queries:
                # Construct Direct Google Maps Search URL
                # Format: https://www.google.com/maps/search/query+location
                
                # Encode params
                import urllib.parse
                q_str = urllib.parse.quote_plus(f"{query} {location}")
                search_url = f"https://www.google.com/maps/search/{q_str}"
                
                if search_url in existing_urls:
                    print(f"  Existing: {search_url}")
                    continue
                
                print(f"  ➕ Generated: {search_url}")
                
                row = {
                    "city": city,
                    "country": country,
                    "search_query": query,
                    "business_name": "Search List", # Placeholder
                    "maps_url": search_url,
                    "source": "direct_gen"
                }
                
                all_results.append(row)
                existing_urls.add(search_url)
                self.save_row(row)

        print(f"✅ Harvest complete. Generated {len(all_results)} new maps links.")
        return all_results

    def save_row(self, row):
        file_exists = os.path.exists(self.output_file)
        with open(self.output_file, 'a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=["city", "country", "search_query", "business_name", "maps_url", "source"])
            if not file_exists:
                writer.writeheader()
            writer.writerow(row)

if __name__ == "__main__":
    # CLI for testing
    # Example: python src/maps/harvester.py --cities "Paris,France;London,UK" --query "interior designers"
    parser = argparse.ArgumentParser(description="Harvest Google Maps links via DuckDuckGo")
    parser.add_argument("--cities", help="Semicolon-separated list of City,Country (e.g. 'Paris,France;London,UK')")
    parser.add_argument("--query", help="Search query (e.g. 'interior designers')", default="interior designers")
    parser.add_argument("--file", help="Path to input CSV with 'city' and 'country' columns")
    
    args = parser.parse_args()
    
    cities_list = []
    
    if args.cities:
        for item in args.cities.split(';'):
            if ',' in item:
                c, country = item.split(',', 1)
                cities_list.append({"city": c.strip(), "country": country.strip()})
            else:
                cities_list.append({"city": item.strip(), "country": ""})
    elif args.file:
        with open(args.file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                cities_list.append(row)
                
    if not cities_list:
        print("Please provide cities via --cities or --file")
        sys.exit(1)
        
    harvester = MapsHarvester()
    
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
        
    asyncio.run(harvester.harvest([args.query], cities_list))
