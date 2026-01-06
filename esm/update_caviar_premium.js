
(function () {
    console.log("Starting premium layout update...");

    const pageContent = `<!-- Premium Artwork Page Styles -->
<style>
/* Font Imports */
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,600;1,400&family=Inter:wght@300;400;500;600&display=swap');

/* Container Reset */
.artwork-page-container {
    font-family: 'Inter', sans-serif;
    color: #2c3e50;
    max-width: 100%;
    margin: 0 auto;
    line-height: 1.6;
}

/* Typography */
.artwork-header {
    text-align: center;
    margin-bottom: 2rem;
}

.artwork-title {
    font-family: 'Playfair Display', serif;
    font-size: 2.5rem; /* Large size */
    margin-bottom: 0.5rem;
    font-weight: 400;
    color: #1a1a1a;
}

.artwork-price {
    font-size: 1.25rem;
    color: #666;
    font-weight: 300;
}

/* Image Styling */
.artwork-hero-image {
    width: 100%;
    height: auto;
    border-radius: 4px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.08);
    margin-bottom: 2rem;
}

/* Action Buttons */
.artwork-actions {
    display: flex;
    flex-direction: column;
    gap: 1rem;
    margin-bottom: 2.5rem;
}

.btn-premium {
    display: flex;
    justify-content: center;
    align-items: center;
    padding: 1rem 1.5rem;
    border-radius: 4px;
    text-decoration: none;
    font-weight: 500;
    transition: all 0.3s ease;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    font-size: 0.9rem;
}

.btn-saatchi {
    background-color: #1a1a1a;
    color: #ffffff !important;
    border: 1px solid #1a1a1a;
}

.btn-saatchi:hover {
    background-color: #333;
    transform: translateY(-1px);
}

.btn-trade {
    background-color: transparent;
    color: #1a1a1a !important;
    border: 1px solid #1a1a1a;
}

.btn-trade:hover {
    background-color: #f8f9fa;
    color: #000 !important;
}

/* Details Card */
.details-card {
    background-color: #f8f9fa;
    padding: 1.5rem;
    border-radius: 8px;
    margin-bottom: 2.5rem;
    border-left: 4px solid #1a1a1a;
}

.details-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1rem;
}

.detail-item {
    display: flex;
    flex-direction: column;
}

.detail-label {
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 1px;
    color: #666;
    margin-bottom: 0.25rem;
}

.detail-value {
    font-weight: 500;
    color: #1a1a1a;
}

/* Content Sections */
.artwork-description {
    font-size: 1.05rem;
    margin-bottom: 3rem;
    color: #4a4a4a;
}

.section-divider {
    height: 1px;
    background: #e0e0e0;
    margin: 3rem 0;
    border: none;
}

/* Designer Specs Box (Refined) */
.designer-specs-premium {
    border: 1px solid #e0e0e0;
    padding: 2rem;
    border-radius: 8px;
    background: #fff;
    position: relative;
    overflow: hidden;
}

.designer-specs-premium::before {
    content: "TRADE ONLY";
    position: absolute;
    top: 1rem;
    right: 1rem;
    font-size: 0.6rem;
    font-weight: 700;
    border: 1px solid #1a1a1a;
    padding: 0.25rem 0.5rem;
    border-radius: 2px;
}

.specs-title {
    font-family: 'Playfair Display', serif;
    font-size: 1.5rem;
    margin-bottom: 1.5rem;
}

.specs-list {
    list-style: none;
    padding: 0;
    margin: 0;
}

.specs-list li {
    padding: 0.75rem 0;
    border-bottom: 1px solid #f0f0f0;
    display: flex;
    align-items: center;
}

.specs-list li:last-child {
    border-bottom: none;
}

.check-icon {
    color: #27ae60;
    margin-right: 0.75rem;
}

</style>

<!-- VisualArtwork Schema -->
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "VisualArtwork",
  "name": "Caviar",
  "artMedium": "Mixed media on canvas",
  "artform": "Painting",
  "artworkSurface": "Canvas",
  "artist": { "@type": "Person", "@id": "https://elliotspencermorgan.com/about#artist", "name": "Elliot Spencer Morgan" },
  "height": {"@type": "Distance", "value": "48", "unitCode": "INH"},
  "width": {"@type": "Distance", "value": "48", "unitCode": "INH"},
  "depth": {"@type": "Distance", "value": "1.5", "unitCode": "INH"},
  "artEdition": "1",
  "image": "https://elliotspencermorgan.com/wp-content/uploads/2025/11/CaviarPainting.jpg",
  "dateCreated": "2024",
  "sameAs": "https://www.saatchiart.com/art/Painting-Caviar/1295487/12292979/view",
  "offers": { "@type": "Offer", "availability": "https://schema.org/InStock", "url": "https://www.saatchiart.com/art/Painting-Caviar/1295487/12292979/view", "price": "2500", "priceCurrency": "USD" }
}
<\/script>

<div class="artwork-page-container">

    <!-- Header -->
    <header class="artwork-header">
        <h1 class="artwork-title">Caviar</h1>
        <div class="artwork-price">$2,500</div>
    </header>

    <!-- Main Image -->
    <img src="https://elliotspencermorgan.com/wp-content/uploads/2025/11/CaviarPainting.jpg" 
         alt="Caviar - Mixed media abstract painting" 
         class="artwork-hero-image">

    <!-- Actions -->
    <div class="artwork-actions">
        <a href="https://www.saatchiart.com/art/Painting-Caviar/1295487/12292979/view" 
           class="btn-premium btn-saatchi"
           onclick="gtag('event', 'saatchi_click', {'artwork': 'Caviar'});">
           Purchase on Saatchi Art
        </a>
        <a href="/trade" 
           class="btn-premium btn-trade"
           onclick="gtag('event', 'trade_click', {'artwork': 'Caviar'});">
           Request Trade Pricing
        </a>
    </div>

    <!-- Details Card -->
    <div class="details-card">
        <div class="details-grid">
            <div class="detail-item">
                <span class="detail-label">Medium</span>
                <span class="detail-value">Mixed Media</span>
            </div>
            <div class="detail-item">
                <span class="detail-label">Dimensions</span>
                <span class="detail-value">48" × 48"</span>
            </div>
            <div class="detail-item">
                <span class="detail-label">Year</span>
                <span class="detail-value">2024</span>
            </div>
            <div class="detail-item">
                <span class="detail-label">Authenticity</span>
                <span class="detail-value">Signed Original</span>
            </div>
        </div>
    </div>

    <!-- Description -->
    <div class="artwork-description">
        <h3>About the Work</h3>
        <p>A striking pattern-oriented abstract painting featuring intricate geometric compositions in rich blues and indigos. The layered mixed media technique creates depth and visual rhythm, making this piece perfect for modern interiors seeking sophisticated, contemporary art.</p>
        <p><em>This piece explores the intersection of organic flow and rigid structure, creating a dynamic visual experience that changes with the light.</em></p>
    </div>

    <hr class="section-divider">

    <!-- Designer Specs (Premium Box) -->
    <div class="designer-specs-premium"
         data-size-category="oversized"
         data-color-palette="blue-indigo">
        
        <h3 class="specs-title">Designer Specifications</h3>
        
        <ul class="specs-list">
            <li><span class="check-icon">✓</span> <strong>Installation:</strong> Wired & Ready to Hang</li>
            <li><span class="check-icon">✓</span> <strong>Weight:</strong> 5 lbs (Lightweight)</li>
            <li><span class="check-icon">✓</span> <strong>Framing:</strong> Gallery Wrapped (Unframed)</li>
            <li><span class="check-icon">✓</span> <strong>Lead Time:</strong> Ships in 5-7 Days</li>
        </ul>

        <div style="margin-top: 1.5rem; display: flex; gap: 1rem;">
             <a href="/downloads/caviar-spec-sheet.pdf" style="font-size: 0.9rem; color: #666; text-decoration: none; border-bottom: 1px dotted #999;">Download Spec Sheet</a>
             <a href="/downloads/caviar-high-res.zip" style="font-size: 0.9rem; color: #666; text-decoration: none; border-bottom: 1px dotted #999;">High-Res Images</a>
        </div>
    </div>

    <hr class="section-divider">

    <!-- Artist Short Bio -->
    <div style="display: flex; align-items: center; gap: 1rem; margin-top: 2rem;">
        <div style="width: 60px; height: 60px; background: #eee; border-radius: 50%;"></div> <!-- Placeholder for Artist Photo -->
        <div>
            <h4 style="margin: 0; font-family: 'Playfair Display', serif;">Elliot Spencer Morgan</h4>
            <p style="margin: 0; font-size: 0.9rem; color: #666;">Austin, TX</p>
        </div>
        <a href="/about" style="margin-left: auto; text-decoration: none; font-size: 0.9rem; font-weight: 600;">View Profile →</a>
    </div>

</div>`;

    if (typeof wp !== 'undefined' && wp.data) {
        wp.data.dispatch('core/editor').editPost({ content: pageContent });
        wp.data.dispatch('core/editor').savePost();
        return "Update initiated";
    } else {
        return "wp.data failed";
    }
})();
