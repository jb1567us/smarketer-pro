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

    // 1. Load JSON Data
    $json_file = ABSPATH . 'artwork_data.json'; // Assuming it sits in root
    // Fallback locations if not in root
    if (!file_exists($json_file)) {
        $json_file = dirname(ABSPATH) . '/artwork_data.json'; 
    }
    
    $artwork_data = null;
    if (file_exists($json_file)) {
        $json_content = file_get_contents($json_file);
        $data_array = json_decode($json_content, true);
        
        // Find matching artwork by Slug or Title
        foreach ($data_array as $item) {
            // Check slug match (try both WP slug and simple slug)
            if (
                (isset($item['slug']) && $item['slug'] === $slug) ||
                (isset($item['wordpress_id']) && $item['wordpress_id'] == get_the_ID()) ||
                (isset($item['cleanTitle']) && strcasecmp($item['cleanTitle'], $title) === 0) ||
                (isset($item['title']) && strcasecmp($item['title'], $title) === 0)
            ) {
                $artwork_data = $item;
                break;
            }
        }
    }

    // 2. Initialize Meta with Defaults
    $meta = [
        'price' => '',
        'dimensions' => '',
        'styles' => [],
        'mediums' => [],
        'frame' => 'Not Framed',
        'packaging' => 'Ships Rolled',
        'shipping' => 'United States',
        'materials' => [],
        'saatchi_url' => ''
    ];

    // 3. Populate from JSON if found
    if ($artwork_data) {
        $meta['price'] = isset($artwork_data['price']) ? '$' . number_format((float)$artwork_data['price']) : '';
        
        // Dimensions: Prefer 'dimensions' field, else construct from w/h/d
        if (!empty($artwork_data['dimensions'])) {
            $meta['dimensions'] = $artwork_data['dimensions'];
        } elseif (!empty($artwork_data['width']) && !empty($artwork_data['height'])) {
            $d = isset($artwork_data['depth']) ? $artwork_data['depth'] : '1';
            $meta['dimensions'] = "{$artwork_data['width']} W x {$artwork_data['height']} H x {$d} D in";
        }

        // Styles
        if (!empty($artwork_data['styles'])) {
            // Can be string or array
            if (is_array($artwork_data['styles'])) {
                $meta['styles'] = $artwork_data['styles'];
            } else {
                $meta['styles'] = array_map('trim', explode(',', $artwork_data['styles']));
            }
        }

        // Mediums
        if (!empty($artwork_data['mediumsDetailed'])) {
            $meta['mediums'] = array_map('trim', explode(',', str_replace(chr(160), ' ', $artwork_data['mediumsDetailed']))); // Handle nbsp
            $meta['materials'] = $meta['mediums'];
        } elseif (!empty($artwork_data['medium'])) {
             $meta['mediums'][] = $artwork_data['medium'];
             $meta['materials'][] = $artwork_data['medium'];
        }

        // Frame
        if (!empty($artwork_data['frame'])) {
            $meta['frame'] = $artwork_data['frame'];
        }

        // Packaging
        if (!empty($artwork_data['packaging'])) {
            $meta['packaging'] = $artwork_data['packaging'];
        }

        // Shipping
        if (!empty($artwork_data['shippingFrom'])) {
            $meta['shipping'] = $artwork_data['shippingFrom'];
        }
        
        // Saatchi URL from JSON
        if (!empty($artwork_data['saatchi_url'])) {
            $meta['saatchi_url'] = $artwork_data['saatchi_url'];
        }
        
        // Image URL from JSON
        // The user explicitly requested to use the path from the JSON as the featured images are broken.
        if (!empty($artwork_data['image_url'])) {
            $meta['image_url'] = $artwork_data['image_url'];
        }
    }

    // 4. Fallback: Parse Tags if JSON failed (Optional, removing per request to use JSON, but good for safety? User said 'should be gathered from artwork data.json'. I will rely on JSON primarily).
    // If we strictly obey "not from tags", we skip tag parsing.
    
    // Fallback for Saatchi URL if JSON didn't have it (heuristic)
    if (empty($meta['saatchi_url'])) {
        // Check CF first
        $cf_saatchi = get_post_meta(get_the_ID(), 'saatchi_url', true);
        if ($cf_saatchi) {
             $meta['saatchi_url'] = $cf_saatchi;
        } else {
             // Heuristic
             $saatchi_slug = str_replace(array('-painting', '-sculpture', '-collage', '-installation', '-print'), '', $slug);
             $meta['saatchi_url'] = 'https://www.saatchiart.com/art/Painting-' . ucfirst($saatchi_slug);
        }
    }
    
    // Fallback for Image if JSON didn't have it
    if (empty($meta['image_url'])) {
        $meta['image_url'] = get_the_post_thumbnail_url(get_the_ID(), 'full');
    }

    // Downloads
    $spec_sheet = "/downloads/spec_sheets/" . ucfirst($slug) . "_spec.pdf";
    $high_res = "/downloads/high_res/" . ucfirst($slug) . "_HighRes.zip";

    // Image (Use Meta)
    $image_url_full = $meta['image_url'];
    
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
    <div class="artwork-hero-wrapper" style="text-align:center;">
        <img src="<?php echo esc_url($image_url_full); ?>" 
             alt="<?php the_title_attribute(); ?>" 
             class="artwork-hero-image skip-lazy no-lazy"
             loading="eager"
             decoding="sync"
             data-no-lazy="1"
             data-skip-lazy="1"
        >
        <noscript>
            <img src="<?php echo esc_url($image_url_full); ?>" alt="<?php the_title_attribute(); ?>" class="artwork-hero-image">
        </noscript>
        
        <!-- Direct Source Link (Visible for Debugging) -->
        <div style="margin-top: 10px; font-family: monospace; font-size: 11px; background: #f9f9f9; padding: 5px; display: inline-block;">
            Source: <a href="<?php echo esc_url($image_url_full); ?>" target="_blank"><?php echo esc_html($image_url_full); ?></a>
        </div>
    </div>
    <?php else: ?>
        <p style="text-align:center; color:red;">No image URL found in JSON or WordPress for this page.</p>
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
