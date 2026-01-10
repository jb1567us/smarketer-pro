import json
import os
import requests
from urllib.parse import urlparse

# 1. Setup
output_dir = os.path.join(os.getcwd(), 'images')
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# 2. Read Data
with open('artwork_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print(f"Downloading {len(data)} images to {output_dir}...")

# 3. Download Loop
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

for item in data:
    url = item.get('image_url')
    if not url or 'upload' not in url:
        continue
        
    filename = os.path.basename(urlparse(url).path)
    filepath = os.path.join(output_dir, filename)
    
    # Skip if exists
    if os.path.exists(filepath):
        print(f"Skipping existing: {filename}")
        continue
        
    print(f"Downloading {item['title']}...")
    try:
        r = requests.get(url, headers=headers, stream=True, verify=False) # Disable verify for self-signed
        if r.status_code == 200:
            with open(filepath, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
            print(f"✅ Saved {filename}")
        else:
            print(f"❌ Failed {filename}: Status {r.status_code}")
    except Exception as e:
        print(f"❌ Error {filename}: {e}")

print("Download complete.")
