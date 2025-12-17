<?php
/**
 * Template Name: Artwork Page
 * The template for displaying single artwork pages
 */

get_header();

while ( have_posts() ) :
    the_post();
    
    // --- Data Extraction -- //
    $slug = get_post_field( 'post_name', get_post() );
    $title = get_the_title();
    
    // Generate Saatchi URL (Heuristic from build script)
    // Adjust logic if actual custom field exists
    $saatchi_slug = str_replace(array('-painting', '-sculpture', '-collage', '-installation', '-print'), '', $slug);
    $saatchi_url = 'https://www.saatchiart.com/art/Painting-' . ucfirst($saatchi_slug); // Placeholder ID not needed usually for search, but deep link might need ID. using search or just base structure.
    // Note: Saatchi URLs usually need an ID. e.g. /art/Painting-Slug/123/456. 
    // If we don't have the ID, this link might fallback to 404. 
    // BETTER: If we have a 'saatchi_url' custom field, use it. Else, maybe just link to profile?
    // For this template, I will use a custom field 'saatchi_link' if present, else #.
    $saatchi_link_cf = get_post_meta(get_the_ID(), 'saatchi_url', true);
    if (!$saatchi_link_cf) {
        $saatchi_link_cf = $saatchi_url; // Tentative fallback
    }

    // Parse Tags for Metadata
    $tags = get_the_tags();
    $meta = [
        'price' => '',
        'dimensions' => '',
        'styles' => [],
        'mediums' => [],
        'frame' => 'Not Framed', // Default
        'packaging' => 'Ships Rolled', // Default
        'shipping' => 'United States',
        'materials' => []
    ];

    if ($tags) {
        foreach ($tags as $tag) {
            $name = $tag->name;
            if (strpos($name, '$') === 0) {
                $meta['price'] = $name;
            } elseif (strpos($name, ' x ') !== false || strpos($name, ' cm') !== false || strpos($name, ' in') !== false) {
                $meta['dimensions'] = $name;
            } elseif (stripos($name, 'framed') !== false) {
                $meta['frame'] = $name;
            } elseif (stripos($name, 'ship') !== false || stripos($name, 'box') !== false || stripos($name, 'tube') !== false) {
                $meta['packaging'] = $name;
            } elseif (in_array(strtolower($name), ['ink', 'paper', 'canvas', 'acrylic', 'oil'])) {
                $meta['mediums'][] = $name;
                $meta['materials'][] = $name; // for schema
            } else {
                $meta['styles'][] = $name; // Assign rest to styles
            }
        }
    }

    // Downloads
    $spec_sheet = "/downloads/spec_sheets/" . ucfirst($slug) . "_spec.pdf";
    $high_res = "/downloads/high_res/" . ucfirst($slug) . "_HighRes.zip";

    // Image
    $image_url_full = get_the_post_thumbnail_url(get_the_ID(), 'full');
    
    // Schema Logic
    $schema_price = str_replace(['$', ','], '', $meta['price']);
    $schema_materials = implode(', ', $meta['mediums']);
?>

<div class="artwork-page-container">

    <!-- Artwork Header -->
    <header class="artwork-header">
        <h1 class="artwork-title"><?php the_title(); ?></h1>
    </header>

    <!-- Main Image -->
    <?php if ($image_url_full) : ?>
    <img src="<?php echo esc_url($image_url_full); ?>" 
         alt="<?php the_title_attribute(); ?>" 
         class="artwork-hero-image">
    <?php endif; ?>

    <?php if ($meta['price']) : ?>
    <div class="artwork-price"><?php echo esc_html($meta['price']); ?></div>
    <?php endif; ?>

    <!-- Actions -->
    <div class="artwork-actions">
        <a href="<?php echo esc_url($saatchi_link_cf); ?>" class="btn-premium btn-saatchi" target="_blank">
            Purchase on Saatchi Art
        </a>
        <a href="/trade" class="btn-premium btn-trade">
            Request Trade Pricing
        </a>
    </div>

    <!-- Details Section -->
    <div class="central-block details-section">
        <h3>Details & Dimensions</h3>

        <div class="details-grid">
            <?php if ($meta['dimensions']) : ?>
            <div><strong>Dimensions:</strong></div>
            <div><?php echo esc_html($meta['dimensions']); ?></div>
            <?php endif; ?>

            <?php if (!empty($meta['styles'])) : ?>
            <div><strong>Styles:</strong></div>
            <div><?php echo esc_html(implode(', ', $meta['styles'])); ?></div>
            <?php endif; ?>

            <?php if (!empty($meta['mediums'])) : ?>
            <div><strong>Mediums:</strong></div>
            <div><?php echo esc_html(implode(', ', $meta['mediums'])); ?></div>
            <?php endif; ?>

            <div><strong>Frame:</strong></div>
            <div><?php echo esc_html($meta['frame']); ?></div>

            <div><strong>Packaging:</strong></div>
            <div><?php echo esc_html($meta['packaging']); ?></div>

            <div><strong>Shipping:</strong></div>
            <div><?php echo esc_html($meta['shipping']); ?></div>
        </div>
    </div>

    <!-- Description -->
    <div class="central-block" style="margin-top: 2rem; margin-bottom: 3rem; color: #4a4a4a;">
        <h3>About the Work</h3>
        <div class="artwork-description">
            <?php the_content(); ?>
        </div>
    </div>

    <hr class="section-divider">

    <!-- Designer Specs (Premium Box) -->
    <div class="designer-specs-premium">
        <h3 class="specs-title">Designer Specifications</h3>

        <ul class="specs-list">
            <li><span class="check-icon">✓</span> <strong>Installation:</strong> Requires Framing (Standard)</li>
            <li><span class="check-icon">✓</span> <strong>Framing:</strong> <?php echo esc_html($meta['frame']); ?></li>
            <li><span class="check-icon">✓</span> <strong>Lead Time:</strong> Ships in 5-7 Days</li>

            <li style="border-bottom: none; padding-top: 1rem; margin-top: 0.5rem; border-top: 1px dashed #eee;">
                <span style="font-size: 0.75rem; color: #999; text-transform: uppercase; letter-spacing: 1px; margin-right: 0.5rem;">Tags:</span>
                <span style="font-size: 0.85rem; color: #666;">
                    <?php echo caviar_get_tags_list(get_the_ID()); ?>
                </span>
            </li>
        </ul>

        <div class="specs-actions">
            <!-- Note: 'download' attribute only works for same-origin or explicit headers -->
            <a href="<?php echo esc_url($spec_sheet); ?>" class="btn-spec-download" download>Download Spec Sheet</a>
            <a href="<?php echo esc_url($high_res); ?>" class="btn-spec-download" download>High-Res Images</a>
        </div>
    </div>

    <hr class="section-divider">

    <!-- Artist Short Bio (Hardcoded for now as per template) -->
    <div class="central-block" style="display: flex; align-items: center; gap: 1rem; margin-top: 2rem;">
        <!-- Placeholder Avatar if no user avatar -->
        <div style="width: 60px; height: 60px; background: #eee; border-radius: 50%; overflow:hidden;">
             <?php echo get_avatar( get_the_author_meta( 'ID' ), 60 ); ?>
        </div>
        <div>
            <h4 style="margin: 0; font-family: 'Playfair Display', serif;">Elliot Spencer Morgan</h4>
            <p style="margin: 0; font-size: 0.9rem; color: #666;">Austin, TX</p>
        </div>
        <a href="/about" style="margin-left: auto; text-decoration: none; font-size: 0.9rem; font-weight: 600; color: #1a1a1a;">View Profile →</a>
    </div>

</div>

<!-- JSON-LD Schema -->
<script type="application/ld+json">
{
  "@context": "https://schema.org/",
  "@type": "VisualArtwork",
  "name": "<?php echo esc_js($title); ?>",
  "image": "<?php echo esc_js($image_url_full); ?>",
  "artist": {
    "@type": "Person",
    "name": "Elliot Spencer Morgan"
  },
  "artMedium": "<?php echo esc_js($schema_materials); ?>",
  "artform": "Painting",
  "description": "<?php echo esc_js(wp_strip_all_tags(get_the_excerpt())); ?>",
  <?php if ($meta['dimensions']) : ?>
  "width": "<?php echo esc_js($meta['dimensions']); ?>",
  <?php endif; ?>
  "offers": {
    "@type": "Offer",
    "price": "<?php echo esc_js($schema_price); ?>",
    "priceCurrency": "USD",
    "availability": "https://schema.org/InStock",
    "url": "<?php echo esc_js(get_permalink()); ?>"
  }
}
</script>

<?php
endwhile; // End of the loop.

get_footer();
