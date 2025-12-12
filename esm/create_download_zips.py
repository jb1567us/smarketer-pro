import json
import os
import zipfile
import urllib.request
from pathlib import Path
import time

# Configuration
HIGH_RES_BASE_URL = "https://elliotspencermorgan.com/wp-content/uploads/2025/11-holdingspace-originals/"
OUTPUT_DIR = r'C:\sandbox\esm\download_packages'
ARTWORK_DATA_PATH = r'C:\sandbox\esm\artwork_data.json'
COLLECTIONS_DATA_PATH = r'C:\sandbox\esm\collections_data.json'

# Create output directories
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(os.path.join(OUTPUT_DIR, 'individual_artworks'), exist_ok=True)
os.makedirs(os.path.join(OUTPUT_DIR, 'collections'), exist_ok=True)

# Load data
with open(ARTWORK_DATA_PATH, 'r', encoding='utf-8') as f:
    artworks = json.load(f)

with open(COLLECTIONS_DATA_PATH, 'r', encoding='utf-8') as f:
    collections = json.load(f)

def normalize_filename(title):
    """Convert artwork title to likely filename"""
    # Replace spaces and special chars
    clean = title.replace(' ', '_').replace('-', '_').replace('/', '_')
    clean = ''.join(c for c in clean if c.isalnum() or c == '_')
    return clean

def download_file(url, dest_path):
    """Download a file from URL"""
    try:
        urllib.request.urlretrieve(url, dest_path)
        return True
    except Exception as e:
        print(f"  Failed to download {url}: {e}")
        return False

def create_artwork_zip(artwork, output_dir):
    """Create ZIP file for a single artwork with all resolutions"""
    title = artwork.get('title', 'Untitled')
    slug = artwork.get('slug', normalize_filename(title))
    
    # Determine file type from URL
    file_type = 'Painting'
    if 'sculpture' in artwork.get('saatchi_url', '').lower():
        file_type = 'Sculpture'
    elif 'collage' in artwork.get('saatchi_url', '').lower():
        file_type = 'Collage'
    
    # Possible filename bases
    possible_bases = [
        normalize_filename(title) + file_type,
        normalize_filename(title),
        title.replace(' ', '_') + file_type,
    ]
    
    # Size variations to try
    size_suffixes = [
        '.jpg',  # Original full resolution
        '-768x800.jpg',
        '-768x768.jpg',
        '-768x530.jpg',
        '-400x300.jpg',
        '-300x300.jpg',
        '-150x150.jpg',
    ]
    
    # Create ZIP
    zip_filename = f"{slug}_highres.zip"
    zip_path = os.path.join(output_dir, zip_filename)
    
    downloaded_files = []
    temp_dir = os.path.join(output_dir, 'temp', slug)
    os.makedirs(temp_dir, exist_ok=True)
    
    # Try to download files
    for base in possible_bases:
        for suffix in size_suffixes:
            filename = base + suffix
            url = HIGH_RES_BASE_URL + filename
            local_path = os.path.join(temp_dir, filename)
            
            if download_file(url, local_path):
                downloaded_files.append(local_path)
                print(f"  Downloaded: {filename}")
                time.sleep(0.2)  # Be respectful to server
    
    if downloaded_files:
        # Create ZIP
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in downloaded_files:
                zipf.write(file_path, os.path.basename(file_path))
        
        print(f"✅ Created: {zip_filename} ({len(downloaded_files)} files)")
        
        # Cleanup temp files
        for f in downloaded_files:
            os.remove(f)
        os.rmdir(temp_dir)
        
        return zip_path
    else:
        print(f"⚠️ No files found for: {title}")
        return None

def create_collection_zip(collection_name, artworks_list, output_dir):
    """Create ZIP file for an entire collection"""
    zip_filename = f"{collection_name.replace(' ', '_')}_collection.zip"
    zip_path = os.path.join(output_dir, zip_filename)
    
    print(f"\nCreating collection ZIP: {collection_name}")
    print(f"  Artworks in collection: {len(artworks_list)}")
    
    # For each artwork, just get the full resolution original
    # To keep collection ZIPs manageable
    
    temp_dir = os.path.join(output_dir, 'temp', 'collection_' + collection_name.replace(' ', '_'))
    os.makedirs(temp_dir, exist_ok=True)
    
    downloaded_files = []
    
    for artwork in artworks_list[:20]:  # Limit to first 20 to avoid huge ZIPs
        title = artwork.get('title', '')
        file_type = 'Painting'
        
        if 'sculpture' in artwork.get('saatchi_url', '').lower():
            file_type = 'Sculpture'
        elif 'collage' in artwork.get('saatchi_url', '').lower():
            file_type = 'Collage'
        
        filename = normalize_filename(title) + file_type + '.jpg'
        url = HIGH_RES_BASE_URL + filename
        local_path = os.path.join(temp_dir, filename)
        
        if download_file(url, local_path):
            downloaded_files.append(local_path)
            print(f"  ✓ {title}")
            time.sleep(0.3)
    
    if downloaded_files:
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in downloaded_files:
                zipf.write(file_path, os.path.basename(file_path))
        
        print(f"✅ Created: {zip_filename} ({len(downloaded_files)} files)")
        
        # Cleanup
        for f in downloaded_files:
            os.remove(f)
        os.rmdir(temp_dir)
        
        return zip_path
    else:
        print(f"⚠️ No files downloaded for collection: {collection_name}")
        return None

# Main execution
if __name__ == "__main__":
    print("=== CREATING DOWNLOAD PACKAGES ===\n")
    
    # Option 1: Individual artwork ZIPs (commented out for now - can take a while)
    # print("Creating individual artwork ZIPs...")
    # individual_created = 0
    # for artwork in artworks[:5]:  # Test with first 5
    #     if artwork.get('saatchi_url'):
    #         if create_artwork_zip(artwork, os.path.join(OUTPUT_DIR, 'individual_artworks')):
    #             individual_created += 1
    
    # print(f"\nIndividual artworks: {individual_created} ZIPs created")
    
    # Option 2: Collection ZIPs
    print("\nCreating collection ZIPs...")
    collection_created = 0
    
    for collection_key, collection_data in collections.items():
        zip_path = create_collection_zip(
            collection_data['title'],
            collection_data['artworks'],
            os.path.join(OUTPUT_DIR, 'collections')
        )
        if zip_path:
            collection_created += 1
    
    print(f"\n=== COMPLETE ===")
    print(f"Collection ZIPs created: {collection_created}")
    print(f"Output directory: {OUTPUT_DIR}")
    print("\nNote: Individual artwork ZIPs are commented out.")
    print("Uncomment in the script to generate all individual ZIPs.")
