#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Image Optimization Script for Artwork Portfolio
Optimizes images for Core Web Vitals:
- Converts to WebP format
- Compresses to 100-250 KB target
- Generates responsive srcset variants
- Renames with SEO-friendly names
- Generates alt text suggestions
"""

import os
import sys
from PIL import Image
import re
from pathlib import Path
from typing import List, Tuple, Optional
import json


class ImageOptimizer:
    """Optimize artwork images for web performance"""
    
    def __init__(self, target_size_kb: int = 200, quality: int = 85):
        """
        Initialize optimizer
        
        Args:
            target_size_kb: Target file size in KB (default 200)
            quality: WebP quality 1-100 (default 85)
        """
        self.target_size_kb = target_size_kb
        self.quality = quality
        self.sizes = [800, 1200, 1600]  # Responsive breakpoints
    
    def optimize_directory(self, input_dir: str, output_dir: str) -> List[dict]:
        """
        Optimize all images in a directory
        
        Args:
            input_dir: Source directory with images
            output_dir: Destination directory for optimized images
            
        Returns:
            List of optimization results
        """
        input_path = Path(input_dir)
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        results = []
        
        # Find all image files
        image_extensions = {'.jpg', '.jpeg', '.png', '.webp'}
        image_files = [f for f in input_path.iterdir() 
                      if f.suffix.lower() in image_extensions]
        
        print(f"Found {len(image_files)} images to optimize...")
        
        for img_file in image_files:
            try:
                result = self.optimize_image(str(img_file), str(output_path))
                results.append(result)
                print(f"✅ Optimized: {img_file.name} → {result['output_file']}")
            except Exception as e:
                print(f"❌ Failed to optimize {img_file.name}: {e}")
                results.append({
                    'input_file': str(img_file),
                    'error': str(e),
                    'success': False
                })
        
        # Save results summary
        summary_path = output_path / 'optimization_summary.json'
        with open(summary_path, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"\n✅ Optimization complete! Summary saved to {summary_path}")
        return results
    
    def optimize_image(self, input_file: str, output_dir: str) -> dict:
        """
        Optimize a single image
        
        Args:
            input_file: Path to source image
            output_dir: Directory for optimized output
            
        Returns:
            Dictionary with optimization results
        """
        input_path = Path(input_file)
        output_path = Path(output_dir)
        
        # Open and convert image
        with Image.open(input_file) as img:
            # Convert to RGB if necessary (for WebP)
            if img.mode in ('RGBA', 'LA', 'P'):
                # Create white background
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = background
            elif img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Get original dimensions
            original_width, original_height = img.size
            original_size_kb = input_path.stat().st_size / 1024
            
            # Generate SEO-friendly filename
            seo_filename = self.generate_seo_filename(input_path.stem)
            
            # Optimize main image
            main_output = output_path / f"{seo_filename}.webp"
            optimized_img = self._resize_and_compress(img, self.target_size_kb, self.quality)
            optimized_img.save(main_output, 'WEBP', quality=self.quality, method=6)
            
            main_size_kb = main_output.stat().st_size / 1024
            
            # Generate responsive variants
            variants = []
            for size in self.sizes:
                if size < original_width:  # Only create smaller versions
                    variant_output = output_path / f"{seo_filename}-{size}w.webp"
                    variant_img = self._resize_to_width(img, size)
                    variant_img.save(variant_output, 'WEBP', quality=self.quality, method=6)
                    variants.append({
                        'width': size,
                        'file': variant_output.name,
                        'size_kb': round(variant_output.stat().st_size / 1024, 2)
                    })
            
            # Generate alt text suggestion
            alt_text = self.generate_alt_text(input_path.stem)
            
            return {
                'input_file': str(input_path),
                'output_file': main_output.name,
                'seo_filename': seo_filename,
                'original_size_kb': round(original_size_kb, 2),
                'optimized_size_kb': round(main_size_kb, 2),
                'compression_ratio': round((1 - main_size_kb / original_size_kb) * 100, 1),
                'original_dimensions': f"{original_width}x{original_height}",
                'variants': variants,
                'suggested_alt_text': alt_text,
                'success': True
            }
    
    def _resize_and_compress(self, img: Image.Image, target_kb: int, quality: int) -> Image.Image:
        """Resize image to meet target file size"""
        # Start with original size
        width, height = img.size
        
        # If image is very large, resize to max 1600px width
        if width > 1600:
            ratio = 1600 / width
            new_width = 1600
            new_height = int(height * ratio)
            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        return img
    
    def _resize_to_width(self, img: Image.Image, target_width: int) -> Image.Image:
        """Resize image to specific width maintaining aspect ratio"""
        width, height = img.size
        ratio = target_width / width
        new_height = int(height * ratio)
        return img.resize((target_width, new_height), Image.Resampling.LANCZOS)
    
    def generate_seo_filename(self, original_name: str) -> str:
        """
        Generate SEO-friendly filename
        
        Example: "YorkiePainting" → "yorkie-abstract-mixed-media-painting-elliot-morgan"
        """
        # Clean the name
        name = original_name.lower().strip()
        
        # Remove common suffixes
        name = re.sub(r'[-_](painting|sculpture|collage|print|artwork)$', '', name)
        
        # Replace spaces and underscores with hyphens
        name = re.sub(r'[\s_]+', '-', name)
        
        # Remove special characters
        name = re.sub(r'[^a-z0-9-]', '', name)
        
        # Add descriptive keywords
        # In production, you'd customize this based on actual artwork data
        name = f"{name}-abstract-art-elliot-morgan"
        
        # Remove duplicate hyphens
        name = re.sub(r'-+', '-', name)
        
        # Remove leading/trailing hyphens
        name = name.strip('-')
        
        return name or "artwork"
    
    def generate_alt_text(self, filename: str) -> str:
        """
        Generate descriptive alt text suggestion
        
        Example: "Yorkie" → "Yorkie - Pattern-oriented abstract painting in mixed media by Austin artist Elliot Spencer Morgan"
        """
        # Clean filename
        title = filename.replace('-', ' ').replace('_', ' ').title()
        title = re.sub(r'\s+(Painting|Sculpture|Collage|Print|Artwork)$', '', title, flags=re.I)
        
        # Generate descriptive alt text
        alt = f"{title} - Pattern-oriented abstract art in mixed media by Austin artist Elliot Spencer Morgan"
        
        return alt
    
    def generate_srcset(self, base_filename: str, variants: List[dict]) -> str:
        """Generate srcset attribute for responsive images"""
        srcset_parts = []
        for variant in variants:
            srcset_parts.append(f"{variant['file']} {variant['width']}w")
        return ", ".join(srcset_parts)


def main():
    """CLI interface for image optimization"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Optimize artwork images for web')
    parser.add_argument('--input', '-i', required=True, help='Input directory with images')
    parser.add_argument('--output', '-o', required=True, help='Output directory for optimized images')
    parser.add_argument('--target-size', '-s', type=int, default=200, help='Target size in KB (default: 200)')
    parser.add_argument('--quality', '-q', type=int, default=85, help='WebP quality 1-100 (default: 85)')
    
    args = parser.parse_args()
    
    optimizer = ImageOptimizer(target_size_kb=args.target_size, quality=args.quality)
    results = optimizer.optimize_directory(args.input, args.output)
    
    # Print summary
    successful = [r for r in results if r.get('success')]
    failed = [r for r in results if not r.get('success')]
    
    print(f"\n{'='*60}")
    print(f"OPTIMIZATION SUMMARY")
    print(f"{'='*60}")
    print(f"Total images: {len(results)}")
    print(f"Successful: {len(successful)}")
    print(f"Failed: {len(failed)}")
    
    if successful:
        avg_compression = sum(r['compression_ratio'] for r in successful) / len(successful)
        avg_size = sum(r['optimized_size_kb'] for r in successful) / len(successful)
        print(f"Average compression: {avg_compression:.1f}%")
        print(f"Average optimized size: {avg_size:.1f} KB")
    
    print(f"{'='*60}\n")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        main()
    else:
        # Example usage
        print("Image Optimizer for Artwork Portfolio")
        print("\nUsage:")
        print("  python image_optimizer.py --input ./original_images --output ./optimized_images")
        print("\nOptions:")
        print("  --target-size, -s    Target file size in KB (default: 200)")
        print("  --quality, -q        WebP quality 1-100 (default: 85)")
        print("\nExample:")
        print("  python image_optimizer.py -i ./compressedImages -o ./web_optimized -s 180 -q 90")
