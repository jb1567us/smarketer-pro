import json
import os
import zipfile
import urllib.request
from pathlib import Path

# Configuration
HIGH_RES_BASE_URL = "https://elliotspencermorgan.com/wp-content/uploads/2025/11-holdingspace-originals/"
OUTPUT_DIR = r'C:\sandbox\esm\highres_packages'
ARTWORK_DATA_PATH = r'C:\sandbox\esm\artwork_data.json'

# Create output directory
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Load artwork data
with open(ARTWORK_DATA_PATH, 'r', encoding='utf-8') as f:
    artworks = json.load(f)

print(f"Loaded {len(artworks)} artworks")
print(f"High-res base URL: {HIGH_RES_BASE_URL}")
print(f"Output directory: {OUTPUT_DIR}")

# TODO: After we see what files are available, we'll:
# 1. Match image filenames to artwork titles
# 2. Create individual ZIP files per artwork (with all resolutions)
# 3. Create collection ZIP files (all artworks in a collection)
# 4. Create master ZIP file (all high-res images)

print("\nNext step: Scan the directory listing to map available images")
