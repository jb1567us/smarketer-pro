import json
import os
import re

# Parse the directory listing and create a mapping
HIGH_RES_BASE = "https://elliotspencermorgan.com/wp-content/uploads/2025/11-holdingspace-originals/"

# Create a simple text file listing all available artworks
# This will help us create download links without needing to download all images

with open(r'C:\sandbox\esm\artwork_data.json', 'r', encoding='utf-8') as f:
    artworks = json.load(f)

# Generate download manifest
download_manifest = []

for artwork in artworks:
    title = artwork.get('title', '')
    if not title:
        continue
    
    # Clean title to match filename pattern
    # Example: "Anemones" -> "AnemonesPainting"
    # Example: "GOLD SERIES 001" -> "GOLD_SERIES_001Painting"
    
    clean_title = title.replace(' ', '_').replace('-', '_')
    
    # Common filename patterns
    possible_filenames = [
        f"{clean_title}Painting",
        f"{clean_title}Sculpture",
        f"{clean_title}Collage",
        f"{clean_title}",
        f"{title.replace(' ', '_')}Painting",
    ]
    
    artwork_images = {
        'title': title,
        'slug': artwork.get('slug', ''),
        'saatchi_url': artwork.get('saatchi_url', ''),
        'possible_filenames': possible_filenames,
        'download_sizes': [
            '150x150',      # Thumbnail
            '300x...',      # Small web
            '400x300',      # Medium web
            '768x...',      # Large web
            'original.jpg'  # Full resolution
        ]
    }
    
    download_manifest.append(artwork_images)

# Save manifest
with open(r'C:\sandbox\esm\highres_download_manifest.json', 'w', encoding='utf-8') as f:
    json.dump(download_manifest, f, indent=2)

print(f"Created download manifest for {len(download_manifest)} artworks")

# Create a simple HTML download page generator
html_template = '''
<!DOCTYPE html>
<html>
<head>
    <title>High-Resolution Image Downloads - Trade Portal</title>
    <style>
        body {{ font-family: Arial, sans-serif; max-width: 1200px; margin: 40px auto; padding: 0 20px; }}
        h1 {{ border-bottom: 3px solid #000; padding-bottom: 10px; }}
        .artwork-section {{ margin: 30px 0; padding: 20px; background: #f9f9f9; }}
        .artwork-title {{ font-size: 20px; font-weight: bold; margin-bottom: 10px; }}
        .download-links {{ display: flex; gap: 15px; flex-wrap: wrap; }}
        .download-link {{ padding: 8px 15px; background: #000; color: #fff; text-decoration: none; border-radius: 4px; }}
        .download-link:hover {{ background: #333; }}
    </style>
</head>
<body>
    <h1>Trade Portal - High-Resolution Downloads</h1>
    <p>Download high-resolution images for specification sheets, presentations, and client proposals.</p>
    
    {artwork_sections}
    
</body>
</html>
'''

artwork_sections_html = ""
for item in download_manifest[:10]:  # First 10 as example
    filename_base = item['possible_filenames'][0]
    
    links_html = f'''
        <a href="{HIGH_RES_BASE}{filename_base}.jpg" class="download-link" download>Full Resolution</a>
        <a href="{HIGH_RES_BASE}{filename_base}-768x800.jpg" class="download-link" download>Large (768px)</a>
        <a href="{HIGH_RES_BASE}{filename_base}-400x300.jpg" class="download-link" download>Medium (400px)</a>
    '''
    
    artwork_sections_html += f'''
    <div class="artwork-section">
        <div class="artwork-title">{item['title']}</div>
        <div class="download-links">
            {links_html}
        </div>
    </div>
    '''

final_html = html_template.format(artwork_sections=artwork_sections_html)

with open(r'C:\sandbox\esm\highres_downloads.html', 'w', encoding='utf-8') as f:
    f.write(final_html)

print("Created sample download page: highres_downloads.html")
print("\nFor Trade Portal integration, we can:")
print("1. Add download buttons to each artwork page")
print("2. Create collection ZIP files (Gold Collection, Blue Collection, etc.)")
print("3. Add bulk download option on trade portal page")
