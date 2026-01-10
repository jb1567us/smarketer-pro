#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Main Integration Script: Elliot Spencer Morgan Website Enhancement
Integrates all tools to implement the strategic plan:
1. Scrape artwork data from Saatchi Art
2. Optimize images
3. Generate artwork pages with VisualArtwork schema
4. Create collection pages
5. Generate WordPress import files
"""

import os
import sys
from pathlib import Path
import json
from datetime import datetime

# Import existing generator
from wordpress_portfolio_generator import WordPressPortfolioGenerator

# Import new enhanced modules
from artwork_page_generator_enhanced import (
    VisualArtworkSchema,
    ArtworkPageTemplate,
    CollectionPageGenerator
)
from image_optimizer import ImageOptimizer


class ESMWebsiteEnhancer:
    """Main orchestrator for website enhancement"""
    
    def __init__(self, output_dir: str = None):
        """Initialize enhancer"""
        self.output_dir = output_dir or f"esm_enhanced_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.portfolio_gen = WordPressPortfolioGenerator()
        self.image_optimizer = ImageOptimizer(target_size_kb=200, quality=85)
        
        # Create directory structure
        self.setup_directories()
    
    def setup_directories(self):
        """Create output directory structure"""
        dirs = [
            self.output_dir,
            os.path.join(self.output_dir, 'images_optimized'),
            os.path.join(self.output_dir, 'wordpress_pages'),
            os.path.join(self.output_dir, 'collection_pages'),
            os.path.join(self.output_dir, 'schema_markup'),
            os.path.join(self.output_dir, 'export'),
        ]
        for d in dirs:
            os.makedirs(d, exist_ok=True)
        
        print(f"✅ Created output directory: {self.output_dir}")
    
    def run_full_enhancement(self, limit: int = None):
        """
        Run complete enhancement workflow
        
        Args:
            limit: Limit number of artworks to process (for testing)
        """
        print("="*60)
        print("ELLIOT SPENCER MORGAN WEBSITE ENHANCEMENT")
        print("="*60)
        print()
        
        # Step 1: Scrape artwork data
        print("Step 1: Scraping artwork data from Saatchi Art...")
        artworks = self.scrape_artworks(limit=limit)
        print(f"✅ Scraped {len(artworks)} artworks\n")
        
        # Step 2: Download and optimize images
        print("Step 2: Downloading and optimizing images...")
        artworks_with_images = self.process_images(artworks)
        print(f"✅ Processed images for {len(artworks_with_images)} artworks\n")
        
        # Step 3: Generate artwork pages with schema
        print("Step 3: Generating artwork pages with VisualArtwork schema...")
        self.generate_artwork_pages(artworks_with_images)
        print(f"✅ Generated {len(artworks_with_images)} artwork pages\n")
        
        # Step 4: Generate collection pages
        print("Step 4: Generating collection landing pages...")
        self.generate_collection_pages(artworks_with_images)
        print(f"✅ Generated collection pages\n")
        
        # Step 5: Create WordPress import file
        print("Step 5: Creating WordPress import file...")
        self.create_wordpress_import(artworks_with_images)
        print(f"✅ Created WordPress import file\n")
        
        # Step 6: Generate implementation guide
        print("Step 6: Generating implementation guide...")
        self.generate_implementation_guide(artworks_with_images)
        print(f"✅ Generated implementation guide\n")
        
        print("="*60)
        print("ENHANCEMENT COMPLETE!")
        print(f"Output directory: {self.output_dir}")
        print("="*60)
    
    def scrape_artworks(self, limit: int = None) -> list:
        """Scrape artwork data from Saatchi Art"""
        self.portfolio_gen.create_directory_structure()
        
        urls = self.portfolio_gen.get_artwork_urls()
        if limit:
            urls = urls[:limit]
        
        artworks = []
        for i, url in enumerate(urls, 1):
            print(f"  [{i}/{len(urls)}] Scraping {url.split('/')[-2]}...")
            soup = self.portfolio_gen.fetch_page(url)
            if soup:
                artwork_data = self.portfolio_gen.extract_artwork_data(soup, url)
                if artwork_data:
                    artworks.append(artwork_data)
            
            # Be polite
            if i < len(urls):
                import time
                time.sleep(self.portfolio_gen.delay_seconds)
        
        # Save raw data
        raw_data_path = os.path.join(self.output_dir, 'artworks_raw_data.json')
        with open(raw_data_path, 'w', encoding='utf-8') as f:
            json.dump(artworks, f, indent=2, ensure_ascii=False)
        
        return artworks
    
    def process_images(self, artworks: list) -> list:
        """Download and optimize images"""
        processed_artworks = []
        
        for i, artwork in enumerate(artworks, 1):
            print(f"  [{i}/{len(artworks)}] Processing images for {artwork['title']}...")
            
            # Download images using existing method
            wordpress_images = self.portfolio_gen.download_images(artwork)
            
            if wordpress_images:
                # Optimize each downloaded image
                optimized_images = []
                for img_data in wordpress_images:
                    try:
                        input_file = img_data['filepath']
                        output_dir = os.path.join(self.output_dir, 'images_optimized')
                        
                        result = self.image_optimizer.optimize_image(input_file, output_dir)
                        optimized_images.append({
                            'original': img_data,
                            'optimized': result
                        })
                    except Exception as e:
                        print(f"    ⚠️  Failed to optimize {img_data['filename']}: {e}")
                
                artwork['wordpress_images'] = wordpress_images
                artwork['optimized_images'] = optimized_images
                artwork['primary_image_url'] = wordpress_images[0]['url'] if wordpress_images else ''
                
                processed_artworks.append(artwork)
        
        return processed_artworks
    
    def generate_artwork_pages(self, artworks: list):
        """Generate individual artwork pages with schema"""
        pages_dir = os.path.join(self.output_dir, 'wordpress_pages')
        schema_dir = os.path.join(self.output_dir, 'schema_markup')
        
        for artwork in artworks:
            # Generate schema
            schema_json = VisualArtworkSchema.generate(artwork)
            
            # Generate page content
            page_content = ArtworkPageTemplate.generate_content(artwork, schema_json)
            
            # Save schema separately
            slug = self._slugify(artwork['title'])
            schema_file = os.path.join(schema_dir, f"{slug}_schema.json")
            with open(schema_file, 'w', encoding='utf-8') as f:
                f.write(schema_json)
            
            # Save page content
            page_file = os.path.join(pages_dir, f"{slug}_page.html")
            with open(page_file, 'w', encoding='utf-8') as f:
                f.write(page_content)
    
    def generate_collection_pages(self, artworks: list):
        """Generate collection landing pages"""
        collections_dir = os.path.join(self.output_dir, 'collection_pages')
        
        for collection_slug in CollectionPageGenerator.COLLECTIONS.keys():
            content = CollectionPageGenerator.generate_collection_page(collection_slug, artworks)
            
            page_file = os.path.join(collections_dir, f"{collection_slug}.html")
            with open(page_file, 'w', encoding='utf-8') as f:
                f.write(content)
    
    def create_wordpress_import(self, artworks: list):
        """Create WordPress XML import file"""
        # Use existing generator's XML export
        self.portfolio_gen.artworks = artworks
        self.portfolio_gen.export_dir = os.path.join(self.output_dir, 'export')
        self.portfolio_gen.generate_wordpress_xml()
        self.portfolio_gen.generate_csv_export()
    
    def generate_implementation_guide(self, artworks: list):
        """Generate step-by-step implementation guide"""
        guide_content = f"""# Implementation Guide: Elliot Spencer Morgan Website Enhancement
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Overview

This package contains all files needed to implement Phase 1 of the strategic plan:
- {len(artworks)} artwork pages with VisualArtwork schema
- {len(CollectionPageGenerator.COLLECTIONS)} collection landing pages
- Optimized images (WebP format, 100-250 KB)
- WordPress import file (XML)
- CSV data export

## Directory Structure

```
{self.output_dir}/
├── wordpress_pages/          # Individual artwork page HTML
├── collection_pages/         # Collection landing pages
├── schema_markup/            # JSON-LD schema files
├── images_optimized/         # WebP optimized images
├── export/                   # WordPress XML + CSV
└── artworks_raw_data.json   # Raw scraped data
```

## Implementation Steps

### Option 1: WordPress Import (Recommended)

1. **Backup your WordPress site** before making changes

2. **Install required plugins:**
   - WordPress Importer (for XML import)
   - Schema Pro or Rank Math (for schema markup)
   - Contact Form 7 or WPForms (for forms)

3. **Import artwork pages:**
   - Go to Tools → Import → WordPress
   - Upload `export/portfolio-export.xml`
   - Assign to existing user or create new
   - Download and import file attachments: YES
   - Click "Submit"

4. **Upload optimized images:**
   - Upload all files from `images_optimized/` to WordPress Media Library
   - Or use FTP to upload to `/wp-content/uploads/`

5. **Add schema markup:**
   - For each artwork page, add the corresponding JSON-LD from `schema_markup/`
   - If using Schema Pro: Add custom schema → Paste JSON
   - If using Rank Math: Schema tab → Add custom schema → Paste JSON
   - Or add directly to page using HTML block with `<script type="application/ld+json">...</script>`

6. **Create collection pages:**
   - Create new pages in WordPress
   - Copy content from `collection_pages/*.html`
   - Set URL slugs: `/collections/pattern-oriented-abstract`, etc.

### Option 2: Manual Page Creation

1. **Use the CSV export** (`export/artwork-data.csv`) as reference

2. **For each artwork:**
   - Create new page in WordPress
   - Set title from CSV
   - Copy HTML from `wordpress_pages/[slug]_page.html`
   - Add schema from `schema_markup/[slug]_schema.json`
   - Upload corresponding images from `images_optimized/`
   - Set URL slug: `/artwork/[slug]`

3. **Create collection pages** from `collection_pages/`

## Next Steps After Import

### 1. Update Homepage
- Change portfolio grid to link to new on-site artwork pages
- Add email opt-in footer
- Optimize hero image for LCP

### 2. Create Trade Portal
- New page: `/trade`
- Add size/color/style filters (JavaScript or WordPress plugin)
- Create trade inquiry form
- Upload spec sheet PDF

### 3. Expand About Page
- Add full biography (3-4 paragraphs)
- Add detailed CV
- Add professional photos
- Add press mentions

### 4. Update Contact Page
- Add NAP information (Name, Address, Phone)
- Add "Austin, Texas" mention
- Add contact form
- Add commission inquiry form

### 5. Set Up Google Analytics 4
- Install GA4 tracking code
- Configure custom events:
  - artwork_view
  - saatchi_referral_click
  - trade_portal_view
  - trade_inquiry_submit
  - commission_inquiry_submit

### 6. Claim Google Business Profile
- Visit google.com/business
- Claim "Elliot Spencer Morgan - Abstract Artist"
- Complete profile with Austin, TX location
- Upload photos
- Set up weekly posting schedule

### 7. Verify Implementation
- Test all artwork page links
- Validate schema with Google Rich Results Test
- Check Core Web Vitals with PageSpeed Insights
- Test mobile responsiveness
- Verify all CTAs work correctly

## Troubleshooting

### Images not displaying
- Check file paths in WordPress Media Library
- Ensure images uploaded to correct directory
- Verify image URLs in page content

### Schema not validating
- Use Google Rich Results Test: https://search.google.com/test/rich-results
- Check JSON syntax (no trailing commas)
- Ensure all required properties present

### Pages not importing
- Check WordPress version compatibility
- Increase PHP memory limit if needed
- Import in smaller batches (25-50 pages at a time)

## Support Files

- **Raw data:** `artworks_raw_data.json`
- **CSV export:** `export/artwork-data.csv`
- **WordPress XML:** `export/portfolio-export.xml`
- **Image optimization summary:** `images_optimized/optimization_summary.json`

## Questions?

Refer to the main strategic plan document for detailed context and long-term roadmap.

---
**Generated by ESM Website Enhancer**
**Version 1.0**
"""
        
        guide_file = os.path.join(self.output_dir, 'IMPLEMENTATION_GUIDE.md')
        with open(guide_file, 'w', encoding='utf-8') as f:
            f.write(guide_content)
    
    def _slugify(self, text: str) -> str:
        """Convert text to URL slug"""
        import re
        slug = text.lower().strip()
        slug = re.sub(r'[^\w\s-]', '', slug)
        slug = re.sub(r'[\s_-]+', '-', slug)
        slug = re.sub(r'^-+|-+$', '', slug)
        return slug


def main():
    """CLI interface"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Enhance Elliot Spencer Morgan website')
    parser.add_argument('--limit', '-l', type=int, help='Limit number of artworks (for testing)')
    parser.add_argument('--output', '-o', help='Output directory')
    
    args = parser.parse_args()
    
    enhancer = ESMWebsiteEnhancer(output_dir=args.output)
    enhancer.run_full_enhancement(limit=args.limit)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        main()
    else:
        print("ESM Website Enhancer")
        print("\nUsage:")
        print("  python esm_website_enhancer.py [options]")
        print("\nOptions:")
        print("  --limit, -l    Limit number of artworks to process (for testing)")
        print("  --output, -o   Output directory name")
        print("\nExamples:")
        print("  # Process first 10 artworks for testing")
        print("  python esm_website_enhancer.py --limit 10")
        print()
        print("  # Process all artworks")
        print("  python esm_website_enhancer.py")
        print()
        print("  # Custom output directory")
        print("  python esm_website_enhancer.py --output my_enhancement")
