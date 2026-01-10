# Artwork Pages + Trade Portal Integration Guide

## Key Considerations for Interior Designers

### 1. **Secondary CTA on Every Artwork Page**

**Why it matters:**
- Designers often find artwork through Google search (not homepage)
- They need a clear path to trade resources from any page
- Captures high-value leads at point of interest

**Implementation:**

```html
<!-- Primary CTA (for collectors) -->
<a href="https://saatchiart.com/art/..." class="btn-primary">
  View/Purchase on Saatchi Art →
</a>

<!-- Secondary CTA (for designers) -->
<a href="/trade" class="btn-secondary">
  Interior Designer Resources →
</a>
```

**Placement:** Below artwork details, above description

---

### 2. **Designer-Specific Metadata in Schema**

**Add to VisualArtwork schema:**

```json
{
  "@context": "https://schema.org",
  "@type": "VisualArtwork",
  "name": "Caviar",
  // ... standard fields ...
  
  // Designer-relevant additions:
  "width": {"@type": "Distance", "value": "48", "unitCode": "INH"},
  "height": {"@type": "Distance", "value": "48", "unitCode": "INH"},
  "depth": {"@type": "Distance", "value": "1.5", "unitCode": "INH"},
  "weight": {"@type": "QuantitativeValue", "value": "5", "unitCode": "LBR"},
  
  // Installation details
  "additionalProperty": [
    {
      "@type": "PropertyValue",
      "name": "Ready to Hang",
      "value": "Yes"
    },
    {
      "@type": "PropertyValue",
      "name": "Framing",
      "value": "Unframed"
    }
  ]
}
```

**Why:** Designers search for specific dimensions and installation details

---

### 3. **Filterable Attributes (for Trade Portal)**

**Add these data attributes to artwork pages:**

```html
<div class="artwork-page" 
     data-size-category="oversized"
     data-color-palette="blue-indigo"
     data-style="pattern-oriented"
     data-width="48"
     data-height="48"
     data-price-range="2000-3000">
  
  <!-- Page content -->
  
</div>
```

**Purpose:** Allows Trade Portal to filter/display artworks dynamically

**Categories to include:**

**Size:**
- `small` (under 24")
- `medium` (24-40")
- `large` (40-60")
- `oversized` (60"+)

**Color Palette:**
- `blue-indigo`
- `neutral-tones`
- `earth-warm`
- `vibrant-colorful`
- `black-white`

**Style:**
- `pattern-oriented`
- `minimalist`
- `geometric`
- `organic`
- `abstract-expressionist`

**Price Range:**
- `under-1000`
- `1000-2000`
- `2000-3000`
- `3000-5000`
- `5000-plus`

---

### 4. **Designer-Friendly Content Sections**

**Add to each artwork page:**

```html
<!-- Standard content -->
<h2>Caviar</h2>
<img src="..." alt="...">

<!-- Collector details -->
<ul class="artwork-details">
  <li><strong>Medium:</strong> Mixed media on canvas</li>
  <li><strong>Dimensions:</strong> 48 × 48 × 1.5 in (121.9 × 121.9 × 3.8 cm)</li>
  <li><strong>Year:</strong> 2024</li>
  <li><strong>Price:</strong> $2,500</li>
</ul>

<!-- NEW: Designer-specific section -->
<div class="designer-specs" style="background: #f8f9fa; padding: 1.5rem; border-radius: 8px; margin: 2rem 0;">
  <h3>For Interior Designers</h3>
  <ul style="list-style: none; padding: 0;">
    <li>✓ <strong>Installation:</strong> Ready to hang, wire included</li>
    <li>✓ <strong>Weight:</strong> 5 lbs (easy wall mounting)</li>
    <li>✓ <strong>Framing:</strong> Unframed (custom framing available)</li>
    <li>✓ <strong>Lead Time:</strong> Ships within 5-7 business days</li>
    <li>✓ <strong>Trade Pricing:</strong> Available - <a href="/trade">Contact for details</a></li>
  </ul>
  
  <p><strong>Perfect for:</strong> Modern residential spaces, corporate lobbies, hospitality projects</p>
  
  <a href="/trade" style="display: inline-block; padding: 0.75rem 1.5rem; background: #34495e; color: white; text-decoration: none; border-radius: 4px; margin-top: 1rem;">
    View Trade Resources →
  </a>
</div>
```

---

### 5. **Downloadable Resources Section**

**Add download links for designers:**

```html
<div class="designer-downloads">
  <h4>Designer Resources</h4>
  <ul>
    <li><a href="/downloads/caviar-spec-sheet.pdf" download>📄 Spec Sheet (PDF)</a></li>
    <li><a href="/downloads/caviar-high-res.zip" download>🖼️ High-Res Images (ZIP)</a></li>
    <li><a href="/downloads/caviar-room-mockups.zip" download>🏠 Room Mockups (ZIP)</a></li>
  </ul>
  <p><small>For trade professionals only. <a href="/trade">Register for access</a></small></p>
</div>
```

**Files to prepare:**
- **Spec Sheet:** PDF with dimensions, weight, materials, installation notes
- **High-Res Images:** 300 DPI images for client presentations
- **Room Mockups:** Artwork in various interior settings

---

### 6. **Trade Portal Integration Points**

**On Trade Portal page (`/trade`):**

```html
<h2>Browse by Category</h2>

<!-- Dynamic filtering -->
<div class="trade-filters">
  <select id="size-filter">
    <option value="">All Sizes</option>
    <option value="oversized">Oversized (60"+)</option>
    <option value="large">Large (40-60")</option>
    <option value="medium">Medium (24-40")</option>
  </select>
  
  <select id="color-filter">
    <option value="">All Colors</option>
    <option value="blue-indigo">Blue & Indigo</option>
    <option value="neutral-tones">Neutral Tones</option>
    <option value="earth-warm">Earth & Warm</option>
  </select>
  
  <select id="style-filter">
    <option value="">All Styles</option>
    <option value="pattern-oriented">Pattern-Oriented</option>
    <option value="minimalist">Minimalist</option>
    <option value="geometric">Geometric</option>
  </select>
</div>

<!-- Artwork grid (filtered dynamically) -->
<div id="trade-artwork-grid">
  <!-- Populated via JavaScript based on data attributes -->
</div>
```

**JavaScript to filter:**

```javascript
// Simple filtering based on artwork page data attributes
function filterArtworks() {
  const size = document.getElementById('size-filter').value;
  const color = document.getElementById('color-filter').value;
  const style = document.getElementById('style-filter').value;
  
  // Fetch artwork data (from API or embedded JSON)
  // Filter based on selected criteria
  // Display matching artworks
}
```

---

### 7. **SEO Keywords for Designer Discovery**

**Include these phrases in artwork descriptions:**

- "Perfect for **interior design projects**"
- "Ideal for **commercial spaces**"
- "**Statement piece** for modern interiors"
- "**Hospitality-grade** artwork"
- "Available for **trade professionals**"

**Why:** Designers search differently than collectors:
- "large abstract art for office lobby"
- "blue artwork for hotel project"
- "statement piece commercial space"

---

### 8. **Cross-Linking Strategy**

**On each artwork page:**

```html
<!-- Related artworks for designers -->
<div class="related-for-designers">
  <h3>Designers Also Viewed</h3>
  <p>Similar pieces for your project:</p>
  <ul>
    <li><a href="/artwork/convergence">Convergence</a> - Similar size, complementary colors</li>
    <li><a href="/artwork/night-sky">Night Sky</a> - Same series, different palette</li>
  </ul>
  
  <p><a href="/collections/oversized-statement-pieces">View all oversized pieces →</a></p>
</div>
```

**On Trade Portal:**

```html
<!-- Featured artwork -->
<div class="featured-for-trade">
  <h3>This Month's Featured Pieces</h3>
  <div class="featured-grid">
    <a href="/artwork/caviar">
      <img src="..." alt="Caviar">
      <p>Caviar - 48×48" - $2,500</p>
    </a>
    <!-- More featured pieces -->
  </div>
</div>
```

---

### 9. **Analytics Tracking (Designer vs. Collector)**

**Track different user paths:**

```html
<!-- On artwork page -->
<script>
  // Track which CTA was clicked
  document.querySelector('.btn-primary').addEventListener('click', function() {
    gtag('event', 'saatchi_referral_click', {
      'artwork_title': 'Caviar',
      'user_type': 'collector'
    });
  });
  
  document.querySelector('.btn-secondary').addEventListener('click', function() {
    gtag('event', 'trade_portal_click', {
      'artwork_title': 'Caviar',
      'user_type': 'designer'
    });
  });
</script>
```

**Measure:**
- What % of artwork page visitors are designers?
- Which artworks drive most trade inquiries?
- Designer conversion rate vs. collector conversion rate

---

### 10. **Mobile Optimization for Designers**

**Designers often browse on tablets/phones at job sites:**

```css
/* Ensure designer specs are mobile-friendly */
.designer-specs {
  font-size: 16px; /* Readable on mobile */
}

.designer-specs ul li {
  padding: 0.5rem 0;
  border-bottom: 1px solid #ddd;
}

/* Make CTAs thumb-friendly */
.btn-secondary {
  min-height: 44px; /* iOS touch target size */
  display: block;
  width: 100%;
  margin: 0.5rem 0;
}

@media (min-width: 768px) {
  .btn-secondary {
    display: inline-block;
    width: auto;
  }
}
```

---

## Implementation Checklist

For each artwork page, ensure:

- [ ] **Primary CTA** to Saatchi (for collectors)
- [ ] **Secondary CTA** to Trade Portal (for designers)
- [ ] **Data attributes** for filtering (size, color, style, price)
- [ ] **Designer specs section** (installation, weight, lead time)
- [ ] **Downloadable resources** (spec sheet, high-res images)
- [ ] **Designer-friendly keywords** in description
- [ ] **Related artworks** for cross-selling
- [ ] **Analytics tracking** (separate designer/collector events)
- [ ] **Mobile-optimized** layout
- [ ] **Schema includes** dimensions and installation details

---

## Trade Portal Page Structure

```html
<h1>Interior Designer & Trade Resources</h1>

<!-- Value proposition -->
<section class="trade-benefits">
  <h2>Why Work With Us</h2>
  <ul>
    <li>Trade pricing on all original works</li>
    <li>High-resolution images for client presentations</li>
    <li>Custom sizing and commissions available</li>
    <li>Fast turnaround (5-7 days standard)</li>
    <li>Installation support in Austin area</li>
  </ul>
</section>

<!-- Filtering interface -->
<section class="trade-filters">
  <h2>Browse Artwork</h2>
  <!-- Size/Color/Style filters -->
</section>

<!-- Artwork grid -->
<section class="trade-artwork-grid">
  <!-- Dynamically filtered artworks -->
</section>

<!-- Trade inquiry form -->
<section class="trade-inquiry">
  <h2>Start a Project</h2>
  <form>
    <input type="text" name="project_name" placeholder="Project Name">
    <select name="project_type">
      <option>Residential</option>
      <option>Commercial</option>
      <option>Hospitality</option>
    </select>
    <input type="text" name="budget_range" placeholder="Budget Range">
    <input type="text" name="size_requirements" placeholder="Size Requirements">
    <textarea name="notes" placeholder="Project Details"></textarea>
    <button type="submit">Submit Inquiry</button>
  </form>
</section>
```

---

## Summary: Designer-Optimized Artwork Pages

**Every artwork page serves dual purposes:**

1. **For Collectors (via Google search):**
   - Beautiful presentation
   - VisualArtwork schema
   - Direct link to Saatchi purchase

2. **For Designers (via Google or Trade Portal):**
   - Technical specifications
   - Installation details
   - Trade pricing access
   - Downloadable resources
   - Easy inquiry path

**Result:** One page, two audiences, maximum conversion!
