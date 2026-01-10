# Quick Start Guide: ESM Website Enhancement Tools

## What You Have

Three powerful automation tools to implement the strategic plan:

1. **`esm_website_enhancer.py`** - Main orchestrator (runs everything)
2. **`artwork_page_generator_enhanced.py`** - Generates pages with VisualArtwork schema
3. **`image_optimizer.py`** - Optimizes images for Core Web Vitals

## Quick Test Run (10 Artworks)

```bash
cd C:\sandbox\esm\esm-portfolio-dev

# Install dependencies
pip install requests beautifulsoup4 pillow

# Test with first 10 artworks
python esm_website_enhancer.py --limit 10
```

This will:
- ✅ Scrape 10 artworks from Saatchi Art
- ✅ Download and optimize images to WebP
- ✅ Generate artwork pages with VisualArtwork schema
- ✅ Create collection pages
- ✅ Generate WordPress XML import file
- ✅ Create implementation guide

**Output:** `esm_enhanced_YYYYMMDD_HHMMSS/` directory with all files

## Full Production Run (All 149 Artworks)

```bash
python esm_website_enhancer.py
```

⚠️ **Warning:** This will take 10-15 minutes due to polite scraping delays.

## Individual Tool Usage

### Image Optimizer Only

```bash
# Optimize images in a directory
python image_optimizer.py --input ./compressedImages --output ./web_optimized

# Custom settings
python image_optimizer.py -i ./images -o ./optimized -s 180 -q 90
```

**Options:**
- `-s, --target-size` - Target size in KB (default: 200)
- `-q, --quality` - WebP quality 1-100 (default: 85)

### Test Image Optimization

```bash
# Test on your existing Yorkie image
python image_optimizer.py --input . --output ./test_optimized
```

## What Gets Generated

```
esm_enhanced_YYYYMMDD_HHMMSS/
├── wordpress_pages/              # HTML for each artwork page
│   ├── caviar_page.html
│   ├── convergence_page.html
│   └── ...
├── collection_pages/             # Collection landing pages
│   ├── pattern-oriented-abstract.html
│   ├── blue-indigo-abstract.html
│   └── ...
├── schema_markup/                # JSON-LD schema files
│   ├── caviar_schema.json
│   ├── convergence_schema.json
│   └── ...
├── images_optimized/             # WebP optimized images
│   ├── caviar-abstract-art-elliot-morgan.webp
│   ├── caviar-abstract-art-elliot-morgan-800w.webp
│   ├── caviar-abstract-art-elliot-morgan-1200w.webp
│   └── ...
├── export/                       # WordPress import files
│   ├── portfolio-export.xml      # WordPress XML import
│   └── artwork-data.csv          # CSV data export
├── artworks_raw_data.json        # Raw scraped data
└── IMPLEMENTATION_GUIDE.md       # Step-by-step instructions
```

## Next Steps After Running

1. **Review the output:**
   - Check `IMPLEMENTATION_GUIDE.md` for detailed instructions
   - Verify a few artwork pages look correct
   - Check schema files validate at https://search.google.com/test/rich-results

2. **Import to WordPress:**
   - Backup your WordPress site first!
   - Go to Tools → Import → WordPress
   - Upload `export/portfolio-export.xml`
   - Follow prompts

3. **Add schema markup:**
   - For each page, add the corresponding JSON-LD from `schema_markup/`
   - Use Schema Pro plugin or add manually

4. **Upload optimized images:**
   - Upload all files from `images_optimized/` to WordPress Media Library

5. **Create remaining pages:**
   - Trade Portal (`/trade`)
   - Commission page (`/commissions-austin`)
   - Expand About page
   - Update Contact page

## Troubleshooting

### "Module not found" errors
```bash
pip install requests beautifulsoup4 pillow
```

### Scraping fails
- Saatchi Art may block requests if too fast
- Script already has 2-second delays
- If still failing, increase delay in `wordpress_portfolio_generator.py` line 39

### Images too large
- Adjust target size: `--target-size 150`
- Lower quality: `--quality 80`

### WordPress import fails
- Import in smaller batches (use `--limit 25`)
- Increase PHP memory limit in WordPress
- Check WordPress version compatibility

## Manual Alternative

If automation doesn't work, you can:

1. Use the CSV export (`export/artwork-data.csv`) as reference
2. Manually create pages in WordPress
3. Copy HTML from `wordpress_pages/` directory
4. Add schema from `schema_markup/` directory
5. Upload images from `images_optimized/`

## Support

- **Strategic Plan:** `C:\Users\baron\.gemini\antigravity\brain\...\updated_strategic_plan.md`
- **Implementation Plan:** `C:\Users\baron\.gemini\antigravity\brain\...\implementation_plan.md`
- **Task List:** `C:\Users\baron\.gemini\antigravity\brain\...\task.md`

---

**Ready to start?** Run the test command above!
