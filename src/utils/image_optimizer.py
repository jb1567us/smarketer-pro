
import os
import sys
from PIL import Image
import re
from pathlib import Path
from typing import List, Tuple, Optional
import json
import logging

# Configure logger
logger = logging.getLogger("ImageOptimizer")

class ImageOptimizer:
    """
    Optimize images for web performance (WebP, resizing, compression).
    Ported from ESM project for B2B Outreach Tool.
    """
    
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
        output_path.mkdir(parents=True, exist_ok=True)
        
        try:
            # Open and convert image
            with Image.open(input_file) as img:
                # Convert to RGB if necessary (for WebP)
                if img.mode in ('RGBA', 'LA', 'P'):
                    # Create white background for transparency handling if needed,
                    # or just keep it if we want transparency (WebP supports it).
                    # ESM logic flattened it, but let's be safer and convert to RGB for consistency unless user wants PNG.
                    # For WebP, RGBA is fine.
                    if img.mode == 'P':
                        img = img.convert('RGBA')
                
                # Get original dimensions
                original_width, original_height = img.size
                original_size_kb = input_path.stat().st_size / 1024
                
                # Generate SEO-friendly filename
                seo_filename = self.generate_seo_filename(input_path.stem)
                
                # Optimize main image
                main_output = output_path / f"{seo_filename}.webp"
                
                # Resize logic
                optimized_img = self._resize_and_compress(img)
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
                    'output_file': str(main_output),
                    'filename': main_output.name,
                    'seo_filename': seo_filename,
                    'original_size_kb': round(original_size_kb, 2),
                    'optimized_size_kb': round(main_size_kb, 2),
                    'compression_ratio': round((1 - main_size_kb / original_size_kb) * 100, 1) if original_size_kb > 0 else 0,
                    'original_dimensions': f"{original_width}x{original_height}",
                    'variants': variants,
                    'suggested_alt_text': alt_text,
                    'success': True
                }
        except Exception as e:
            logger.error(f"Optimization failed for {input_file}: {e}")
            return {
                'input_file': str(input_file),
                'error': str(e),
                'success': False
            }
    
    def _resize_and_compress(self, img: Image.Image) -> Image.Image:
        """Resize image to meet target max width (1600px)"""
        width, height = img.size
        
        # If image is very large, resize to max 1600px width
        if width > 1600:
            ratio = 1600 / width
            new_width = 1600
            new_height = int(height * ratio)
            return img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
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
        Example: "YorkiePainting" -> "yorkie-painting"
        """
        # Clean the name
        name = original_name.lower().strip()
        
        # Replace spaces and underscores with hyphens
        name = re.sub(r'[\s_]+', '-', name)
        
        # Remove special characters
        name = re.sub(r'[^a-z0-9-]', '', name)
        
        # Remove duplicate hyphens
        name = re.sub(r'-+', '-', name)
        
        return name.strip('-') or "image"
    
    def generate_alt_text(self, filename: str) -> str:
        """
        Generate descriptive alt text suggestion
        """
        # Clean filename
        title = filename.replace('-', ' ').replace('_', ' ').strip()
        # CamelCase to Space
        title = re.sub('([a-z])([A-Z])', r'\1 \2', title)
        return title.title()
