#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Enhanced Artwork Page Generator with VisualArtwork Schema
Extends the original wordpress_portfolio_generator.py with:
- VisualArtwork JSON-LD schema markup
- Optimized page templates for SEO
- Trade Portal integration
- Collection page generation
- Enhanced image handling
"""

import json
import re
from datetime import datetime
from typing import Dict, List, Optional


class VisualArtworkSchema:
    """Generate Schema.org VisualArtwork JSON-LD markup"""
    
    @staticmethod
    def generate(artwork_data: Dict, artist_url: str = "https://elliotspencermorgan.com/about#artist") -> str:
        """
        Generate VisualArtwork schema markup
        
        Args:
            artwork_data: Dictionary with artwork details
            artist_url: URL to artist Person schema
            
        Returns:
            JSON-LD string ready to inject into page
        """
        # Parse dimensions
        dimensions = VisualArtworkSchema._parse_dimensions(artwork_data.get('dimensions', ''))
        
        # Determine artform and surface
        medium = artwork_data.get('medium', '').lower()
        artform = VisualArtworkSchema._determine_artform(medium)
        surface = VisualArtworkSchema._determine_surface(medium)
        
        schema = {
            "@context": "https://schema.org",
            "@type": "VisualArtwork",
            "name": artwork_data.get('title', 'Untitled'),
            "artMedium": artwork_data.get('medium', 'Mixed media'),
            "artform": artform,
            "artworkSurface": surface,
            "artist": {
                "@type": "Person",
                "@id": artist_url,
                "name": "Elliot Spencer Morgan"
            },
            "artEdition": "1",  # Original artwork
            "image": artwork_data.get('primary_image_url', ''),
            "description": artwork_data.get('description', ''),
        }
        
        # Add dimensions if available
        if dimensions:
            if 'height' in dimensions:
                schema["height"] = {
                    "@type": "Distance",
                    "value": str(dimensions['height']),
                    "unitCode": dimensions.get('unit', 'INH')
                }
            if 'width' in dimensions:
                schema["width"] = {
                    "@type": "Distance",
                    "value": str(dimensions['width']),
                    "unitCode": dimensions.get('unit', 'INH')
                }
            if 'depth' in dimensions:
                schema["depth"] = {
                    "@type": "Distance",
                    "value": str(dimensions['depth']),
                    "unitCode": dimensions.get('unit', 'INH')
                }
        
        # Add year if available
        year = artwork_data.get('year_created')
        if year and year != "Year not specified":
            schema["dateCreated"] = year
        
        # Add Saatchi Art link as sameAs
        saatchi_url = artwork_data.get('url', '')
        if saatchi_url:
            schema["sameAs"] = saatchi_url
            
            # Add offer pointing to Saatchi
            schema["offers"] = {
                "@type": "Offer",
                "availability": "https://schema.org/InStock",
                "url": saatchi_url
            }
            
            # Add price if available
            price_str = artwork_data.get('price', '')
            price_match = re.search(r'(\d[\d,]*(?:\.\d{2})?)', price_str)
            if price_match:
                schema["offers"]["price"] = price_match.group(1).replace(',', '')
                schema["offers"]["priceCurrency"] = "USD"
        
        return json.dumps(schema, indent=2)
    
    @staticmethod
    def _parse_dimensions(dim_str: str) -> Optional[Dict]:
        """Parse dimension string into structured data"""
        if not dim_str or dim_str == "Dimensions not specified":
            return None
        
        # Try to match WxHxD or WxH patterns
        # Example: "48 × 48 × 1.5 in" or "121.9 × 121.9 cm"
        pattern = r'([\d.]+)\s*[×x]\s*([\d.]+)(?:\s*[×x]\s*([\d.]+))?\s*(in|cm|inches|centimeters)'
        match = re.search(pattern, dim_str, re.I)
        
        if match:
            width, height, depth, unit = match.groups()
            unit_code = "INH" if unit.lower().startswith('in') else "CMT"
            
            result = {
                'width': float(width),
                'height': float(height),
                'unit': unit_code
            }
            if depth:
                result['depth'] = float(depth)
            return result
        
        return None
    
    @staticmethod
    def _determine_artform(medium: str) -> str:
        """Determine artform from medium"""
        if any(x in medium for x in ['painting', 'acrylic', 'oil', 'watercolor', 'ink']):
            return "Painting"
        elif any(x in medium for x in ['sculpture', '3d', 'wood', 'metal']):
            return "Sculpture"
        elif 'collage' in medium:
            return "Collage"
        elif any(x in medium for x in ['print', 'edition']):
            return "Print"
        elif 'drawing' in medium:
            return "Drawing"
        else:
            return "Painting"  # Default
    
    @staticmethod
    def _determine_surface(medium: str) -> str:
        """Determine artwork surface from medium"""
        if 'canvas' in medium:
            return "Canvas"
        elif 'paper' in medium:
            return "Paper"
        elif 'wood' in medium or 'panel' in medium:
            return "Wood panel"
        elif 'board' in medium:
            return "Board"
        else:
            return "Canvas"  # Default


class ArtworkPageTemplate:
    """Generate WordPress page content for artwork"""
    
    @staticmethod
    def generate_content(artwork_data: Dict, schema_json: str) -> str:
        """
        Generate complete WordPress page content
        
        Args:
            artwork_data: Artwork details
            schema_json: VisualArtwork schema JSON-LD
            
        Returns:
            HTML content for WordPress page
        """
        saatchi_url = artwork_data.get('url', '#')
        title = artwork_data.get('title', 'Untitled')
        medium = artwork_data.get('medium', 'Mixed media')
        dimensions = artwork_data.get('dimensions', 'Dimensions not specified')
        year = artwork_data.get('year_created', '')
        price = artwork_data.get('price', 'Inquire')
        description = artwork_data.get('description', '')
        
        # Build image gallery HTML
        images_html = ""
        wordpress_images = artwork_data.get('wordpress_images', [])
        if wordpress_images:
            # Primary image
            primary_img = wordpress_images[0]
            images_html += f'''
<div class="artwork-primary-image">
    <img src="{primary_img['url']}" 
         alt="{ArtworkPageTemplate._escape_html(title)} - Pattern-oriented abstract art by Elliot Spencer Morgan" 
         width="1200" 
         height="1200"
         loading="eager"
         style="width: 100%; height: auto; border-radius: 8px; margin-bottom: 2rem;">
</div>
'''
            
            # Detail shots (lazy loaded)
            if len(wordpress_images) > 1:
                images_html += '<div class="artwork-detail-images" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 1rem; margin-bottom: 2rem;">\n'
                for img in wordpress_images[1:]:
                    images_html += f'''    <img src="{img['url']}" 
         alt="{ArtworkPageTemplate._escape_html(title)} detail" 
         loading="lazy"
         style="width: 100%; height: auto; border-radius: 8px;">
'''
                images_html += '</div>\n'
        
        # Build details list
        details_items = [
            ("Medium", medium),
            ("Dimensions", dimensions),
            ("Year", year if year and year != "Year not specified" else ""),
            ("Price", price),
        ]
        
        details_html = '<ul class="artwork-details" style="list-style: none; padding: 0; margin: 1.5rem 0;">\n'
        for label, value in details_items:
            if value:
                details_html += f'    <li style="padding: 0.75rem 0; border-bottom: 1px solid #ecf0f1;"><strong>{label}:</strong> {ArtworkPageTemplate._escape_html(str(value))}</li>\n'
        details_html += '</ul>\n'
        
        # CTAs
        cta_html = f'''
<div class="artwork-ctas" style="margin: 2rem 0; display: flex; gap: 1rem; flex-wrap: wrap;">
    <a href="{saatchi_url}" 
       class="btn-primary" 
       style="display: inline-block; padding: 1rem 2rem; background: #e74c3c; color: white; text-decoration: none; border-radius: 6px; font-weight: 600; transition: background 0.3s;"
       onclick="gtag('event', 'saatchi_referral_click', {{'artwork_title': '{ArtworkPageTemplate._escape_js(title)}'}});">
        View/Purchase on Saatchi Art →
    </a>
    <a href="/trade" 
       class="btn-secondary" 
       style="display: inline-block; padding: 1rem 2rem; background: #34495e; color: white; text-decoration: none; border-radius: 6px; font-weight: 600; transition: background 0.3s;">
        Designer Trade Access
    </a>
</div>
'''
        
        # Complete page content
        content = f'''
<!-- VisualArtwork Schema -->
<script type="application/ld+json">
{schema_json}
</script>

{images_html}

<div class="artwork-info" style="max-width: 800px; margin: 0 auto;">
    <h2 style="font-size: 2rem; margin-bottom: 1rem; color: #2c3e50;">{ArtworkPageTemplate._escape_html(title)}</h2>
    
    {details_html}
    
    {cta_html}
    
    <div class="artwork-description" style="margin: 2rem 0; line-height: 1.8;">
        <h3 style="font-size: 1.5rem; margin-bottom: 1rem; color: #34495e;">About This Artwork</h3>
        <p>{ArtworkPageTemplate._escape_html(description)}</p>
    </div>
    
    <div class="artwork-artist-info" style="margin: 2rem 0; padding: 1.5rem; background: #f8f9fa; border-radius: 8px;">
        <h3 style="font-size: 1.3rem; margin-bottom: 0.5rem;">About the Artist</h3>
        <p><strong>Elliot Spencer Morgan</strong> is a contemporary abstract artist based in Austin, Texas, specializing in pattern-oriented mixed media works. <a href="/about">Learn more →</a></p>
    </div>
</div>

<!-- GA4 Event Tracking -->
<script>
    // Track artwork page view
    if (typeof gtag !== 'undefined') {{
        gtag('event', 'artwork_view', {{
            'artwork_title': '{ArtworkPageTemplate._escape_js(title)}',
            'artwork_medium': '{ArtworkPageTemplate._escape_js(medium)}'
        }});
    }}
</script>
'''
        
        return content
    
    @staticmethod
    def _escape_html(text: str) -> str:
        """Escape HTML special characters"""
        if not text:
            return ""
        return (str(text)
                .replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
                .replace('"', "&quot;")
                .replace("'", "&#39;"))
    
    @staticmethod
    def _escape_js(text: str) -> str:
        """Escape JavaScript special characters"""
        if not text:
            return ""
        return (str(text)
                .replace("\\", "\\\\")
                .replace("'", "\\'")
                .replace('"', '\\"')
                .replace("\n", "\\n"))


class CollectionPageGenerator:
    """Generate collection landing pages"""
    
    COLLECTIONS = {
        'pattern-oriented-abstract': {
            'title': 'Pattern-Oriented Abstract Art',
            'description': 'Explore Elliot Spencer Morgan\'s signature pattern-oriented abstract works, featuring intricate geometric compositions and rhythmic visual structures.',
            'keywords': ['pattern oriented abstract art', 'geometric pattern paintings', 'structured abstract art'],
            'filter_tags': ['pattern', 'geometric']
        },
        'blue-indigo-abstract': {
            'title': 'Blue & Indigo Abstract Paintings',
            'description': 'A curated collection of abstract works in rich blues and indigos, perfect for creating calming, sophisticated interior spaces.',
            'keywords': ['blue abstract art', 'indigo contemporary paintings', 'royal blue wall art'],
            'filter_tags': ['blue', 'indigo']
        },
        'oversized-statement-pieces': {
            'title': 'Oversized Statement Pieces',
            'description': 'Large-scale abstract artworks designed to command attention and transform spaces. Ideal for residential and commercial interiors.',
            'keywords': ['large abstract art', 'oversized contemporary paintings', 'statement wall art'],
            'filter_size': 'large'
        },
        'minimalist-abstract': {
            'title': 'Minimalist Abstract Art',
            'description': 'Clean, refined abstract compositions that embody simplicity and elegance. Perfect for modern, minimalist interiors.',
            'keywords': ['minimalist abstract art', 'simple modern paintings', 'contemporary minimalism'],
            'filter_tags': ['minimalist', 'simple']
        },
        'neutral-tones': {
            'title': 'Neutral Tones Collection',
            'description': 'Sophisticated abstract works in neutral palettes—perfect for versatile interior design and timeless aesthetic appeal.',
            'keywords': ['neutral abstract art', 'beige contemporary paintings', 'neutral wall art'],
            'filter_tags': ['neutral', 'beige', 'earth']
        }
    }
    
    @staticmethod
    def generate_collection_page(collection_slug: str, artworks: List[Dict]) -> str:
        """Generate collection page content"""
        if collection_slug not in CollectionPageGenerator.COLLECTIONS:
            return ""
        
        collection = CollectionPageGenerator.COLLECTIONS[collection_slug]
        
        # Filter artworks based on collection criteria
        filtered_artworks = CollectionPageGenerator._filter_artworks(artworks, collection)
        
        # Build artwork grid
        grid_html = '<div class="collection-grid" style="display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 2rem; margin: 3rem 0;">\n'
        
        for artwork in filtered_artworks[:12]:  # Show first 12
            title = artwork.get('title', 'Untitled')
            slug = CollectionPageGenerator._slugify(title)
            img_url = artwork.get('wordpress_images', [{}])[0].get('url', '')
            price = artwork.get('price', 'Inquire')
            
            grid_html += f'''    <div class="collection-item" style="background: white; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 10px rgba(0,0,0,0.1); transition: transform 0.3s;">
        <a href="/artwork/{slug}" style="text-decoration: none; color: inherit;">
            <img src="{img_url}" alt="{ArtworkPageTemplate._escape_html(title)}" style="width: 100%; height: 300px; object-fit: cover;" loading="lazy">
            <div style="padding: 1rem;">
                <h3 style="font-size: 1.1rem; margin: 0 0 0.5rem 0; color: #2c3e50;">{ArtworkPageTemplate._escape_html(title)}</h3>
                <p style="margin: 0; color: #e74c3c; font-weight: 600;">{ArtworkPageTemplate._escape_html(price)}</p>
            </div>
        </a>
    </div>
'''
        
        grid_html += '</div>\n'
        
        # Build related collections links
        related_html = '<div class="related-collections" style="margin: 3rem 0; padding: 2rem; background: #f8f9fa; border-radius: 8px;">\n'
        related_html += '    <h3 style="margin-bottom: 1rem;">Explore More Collections</h3>\n'
        related_html += '    <div style="display: flex; gap: 1rem; flex-wrap: wrap;">\n'
        
        for slug, info in CollectionPageGenerator.COLLECTIONS.items():
            if slug != collection_slug:
                related_html += f'        <a href="/collections/{slug}" style="padding: 0.5rem 1rem; background: white; border-radius: 4px; text-decoration: none; color: #34495e; border: 1px solid #ddd;">{info["title"]}</a>\n'
        
        related_html += '    </div>\n</div>\n'
        
        # Complete page
        content = f'''
<div class="collection-header" style="max-width: 800px; margin: 0 auto 3rem; text-align: center;">
    <h1 style="font-size: 2.5rem; margin-bottom: 1rem; color: #2c3e50;">{collection['title']}</h1>
    <p style="font-size: 1.2rem; line-height: 1.8; color: #555;">{collection['description']}</p>
</div>

{grid_html}

{related_html}

<div class="collection-cta" style="text-align: center; margin: 3rem 0;">
    <a href="/contact" style="display: inline-block; padding: 1rem 2rem; background: #34495e; color: white; text-decoration: none; border-radius: 6px; font-weight: 600;">Request a Custom Commission →</a>
</div>
'''
        
        return content
    
    @staticmethod
    def _filter_artworks(artworks: List[Dict], collection: Dict) -> List[Dict]:
        """Filter artworks based on collection criteria"""
        # This is a simplified filter - in production, you'd use more sophisticated matching
        filtered = []
        
        filter_tags = collection.get('filter_tags', [])
        filter_size = collection.get('filter_size', '')
        
        for artwork in artworks:
            title_lower = artwork.get('title', '').lower()
            medium_lower = artwork.get('medium', '').lower()
            description_lower = artwork.get('description', '').lower()
            
            # Check tags
            if filter_tags:
                if any(tag in title_lower or tag in medium_lower or tag in description_lower for tag in filter_tags):
                    filtered.append(artwork)
            
            # Check size
            elif filter_size == 'large':
                dims = artwork.get('dimensions', '')
                # Simple heuristic: look for dimensions > 40 inches
                if re.search(r'(4[0-9]|[5-9][0-9]|[1-9][0-9]{2})\s*[×x]', dims):
                    filtered.append(artwork)
        
        return filtered
    
    @staticmethod
    def _slugify(text: str) -> str:
        """Convert text to URL slug"""
        slug = text.lower().strip()
        slug = re.sub(r'[^\w\s-]', '', slug)
        slug = re.sub(r'[\s_-]+', '-', slug)
        slug = re.sub(r'^-+|-+$', '', slug)
        return slug


# Example usage
if __name__ == "__main__":
    # Sample artwork data
    sample_artwork = {
        'title': 'Caviar',
        'medium': 'Mixed media on canvas',
        'dimensions': '48 × 48 × 1.5 in',
        'year_created': '2024',
        'price': '$2,500',
        'description': 'A pattern-oriented abstract painting featuring intricate geometric compositions in rich blues and indigos.',
        'url': 'https://www.saatchiart.com/art/Painting-Caviar/1295487/12292979/view',
        'primary_image_url': 'https://example.com/caviar-main.jpg',
        'wordpress_images': [
            {'url': '/wp-content/uploads/2024/12/caviar-main.jpg', 'filename': 'caviar-main.jpg'}
        ]
    }
    
    # Generate schema
    schema = VisualArtworkSchema.generate(sample_artwork)
    print("=== VisualArtwork Schema ===")
    print(schema)
    print("\n")
    
    # Generate page content
    content = ArtworkPageTemplate.generate_content(sample_artwork, schema)
    print("=== WordPress Page Content ===")
    print(content[:500] + "...")
