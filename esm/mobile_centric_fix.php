<?php
// mobile_centric_fix.php
// 1. Update Header Template -> ABSOLUTE Image URL
// 2. Update CSS -> Fluid Widths (No Fixed PX)

require_once($_SERVER['DOCUMENT_ROOT'] . '/wp-load.php');
echo "<h1>📱 Mobile Centric Fix</h1>";

$mu_dir = $_SERVER['DOCUMENT_ROOT'] . '/wp-content/mu-plugins';
if (!is_dir($mu_dir)) {
    mkdir($mu_dir, 0755, true);
}

// --- PART 1: CSS (Mobile Centric / Fluid) ---
$css_code = <<<'PHP'
<?php
/* Plugin Name: ESM CSS Overrides (Mobile) */
add_action('wp_head', function() {
    echo '<style>
    /* 1. HEADER CONTAINER (Vertical & Full Width) */
    header .wp-block-group {
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        width: 100% !important; /* User requested 100% */
        max-width: 100% !important;
        padding-left: 0 !important;
        padding-right: 0 !important;
        overflow-x: hidden !important;
    }

    /* 2. SITE TITLE (Centered) */
    .wp-block-site-title {
        text-align: center !important;
        width: 100% !important;
        display: block !important;
        margin: 1rem 0 0.5rem 0 !important;
    }
    .wp-block-site-title a {
        font-family: "Playfair Display", serif !important;
        font-weight: 400 !important;
        text-decoration: none !important;
        font-size: clamp(1.8rem, 5vw, 2.5rem) !important; /* Responsive Font */
        line-height: 1.2 !important;
        color: #1a1a1a !important;
        display: block !important;
        width: 100% !important;
        text-align: center !important;
    }

    /* 3. LOGO (Fluid - No Fixed Width) */
    .header-logo {
        display: block !important;
        margin: 0 auto 1.5rem auto !important;
        width: auto !important;
        max-width: 100% !important; /* Ensure it fits container */
    }
    .header-logo img {
        display: block !important;
        margin: 0 auto !important;
        width: auto !important; /* Natural size */
        max-width: 80vw !important; /* Cap at 80% of viewport width so it's not huge on desktop but safe on mobile */
        height: auto !important;
    }

    /* 4. NAVIGATION (Right Aligned & Responsive) */
    .wp-block-navigation {
        width: 100% !important;
        display: flex !important;
        flex-direction: row !important;
        justify-content: flex-end !important; 
        padding-right: 1.5rem !important; /* Safe padding */
        box-sizing: border-box !important;
    }
    .wp-block-navigation__responsive-container {
        margin-left: auto !important; 
        margin-right: 0 !important;
    }
    .wp-block-navigation__responsive-container-open {
        display: flex !important;
        margin-left: auto !important;
        margin-right: 0 !important;
    }
    
    /* Utilities */
    .wp-block-post-title { display: none !important; }
    .wp-block-page-list { display: none !important; }
    </style>';
}, 999);
PHP;

file_put_contents($mu_dir . '/esm-css-fixes.php', $css_code);
echo "✅ Updated CSS (Fluid/Mobile Rules).<br>";


// --- PART 2: HEADER TEMPLATE (Absolute Link) ---

$nav = get_page_by_path('main-navigation', OBJECT, 'wp_navigation');
$nav_id = $nav ? $nav->ID : 0;
// CRITICAL: Absolute URL to prevent relative path issues
$logo_url = 'https://elliotspencermorgan.com/logo.png';

$header_content = <<<HTML
<!-- wp:group {"align":"full","style":{"spacing":{"padding":{"top":"var:preset|spacing|30","bottom":"var:preset|spacing|30"}}},"layout":{"type":"flex","orientation":"vertical","justifyContent":"center","alignItems":"center"}} -->
<div class="wp-block-group alignfull" style="padding-top:var(--wp--preset--spacing--30);padding-bottom:var(--wp--preset--spacing--30)">
    
    <!-- wp:site-title {"level":1,"textAlign":"center","style":{"typography":{"fontStyle":"normal","fontWeight":"400"}}} /-->

    <!-- wp:image {"sizeSlug":"full","linkDestination":"none","className":"header-logo"} -->
    <figure class="wp-block-image size-full header-logo"><img src="$logo_url" alt="Logo" /></figure>
    <!-- /wp:image -->

    <!-- wp:navigation {"ref":$nav_id,"overlayMenu":"always","layout":{"type":"flex","justifyContent":"right","orientation":"horizontal"}} /-->

</div>
<!-- /wp:group -->
HTML;

$headers = get_posts([
    'post_type' => 'wp_template_part',
    'post_status' => 'any',
    'numberposts' => -1,
    'tax_query' => [['taxonomy' => 'wp_template_part_area', 'field' => 'slug', 'terms' => 'header']]
]);

foreach ($headers as $h) {
    wp_update_post(['ID' => $h->ID, 'post_content' => $header_content]);
    echo "✅ Updated Header Template " . $h->ID . " (Absolute URL)<br>";
}

if (function_exists('opcache_reset'))
    opcache_reset();
echo "<a href='/fireworks/'>Check /fireworks/</a>";
?>