
import sys
import os

# Add src directory to path
src_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../src'))
sys.path.insert(0, src_dir)

print(f"Added {src_dir} to sys.path")

print("Attempting to import src.social_scraper (which depends on CaptchaSolver)...")
try:
    from social_scraper import SocialScraper
    print("SUCCESS: SocialScraper imported without error.")
except ImportError as e:
    print(f"FAILURE: Import failed with error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"FAILURE: Unexpected error: {e}")
    sys.exit(1)
