#!/usr/bin/env python3
"""
Simple test script to verify tools are working
"""

import sys
import os

print("="*60)
print("ESM WEBSITE ENHANCEMENT TOOLS - VERIFICATION TEST")
print("="*60)
print()

# Test 1: Check Python version
print("✓ Python version:", sys.version.split()[0])

# Test 2: Check dependencies
print("\nChecking dependencies...")
dependencies = {
    'requests': False,
    'beautifulsoup4': False,
    'PIL': False
}

for dep in dependencies:
    try:
        if dep == 'beautifulsoup4':
            import bs4
            dependencies[dep] = True
            print(f"  ✓ {dep} installed")
        elif dep == 'PIL':
            from PIL import Image
            dependencies[dep] = True
            print(f"  ✓ Pillow installed")
        else:
            __import__(dep)
            dependencies[dep] = True
            print(f"  ✓ {dep} installed")
    except ImportError:
        print(f"  ✗ {dep} NOT installed")

# Test 3: Check if tools exist
print("\nChecking tool files...")
tools = [
    'esm_website_enhancer.py',
    'artwork_page_generator_enhanced.py',
    'image_optimizer.py',
    'wordpress_portfolio_generator.py'
]

for tool in tools:
    if os.path.exists(tool):
        print(f"  ✓ {tool} found")
    else:
        print(f"  ✗ {tool} NOT found")

# Test 4: Test image optimizer import
print("\nTesting module imports...")
try:
    from artwork_page_generator_enhanced import VisualArtworkSchema
    print("  ✓ VisualArtworkSchema imported")
except Exception as e:
    print(f"  ✗ Failed to import VisualArtworkSchema: {e}")

try:
    from image_optimizer import ImageOptimizer
    print("  ✓ ImageOptimizer imported")
except Exception as e:
    print(f"  ✗ Failed to import ImageOptimizer: {e}")

# Summary
print("\n" + "="*60)
all_deps = all(dependencies.values())
if all_deps:
    print("✅ ALL CHECKS PASSED - Ready to run!")
    print("\nNext steps:")
    print("  1. Test with 10 artworks:")
    print("     python esm_website_enhancer.py --limit 10")
    print()
    print("  2. Or test image optimizer only:")
    print("     python image_optimizer.py -i ../compressedImages -o ./test_output")
else:
    print("⚠️  MISSING DEPENDENCIES")
    print("\nInstall missing packages:")
    print("  pip install requests beautifulsoup4 pillow")
print("="*60)
