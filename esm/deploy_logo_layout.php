<?php
// deploy_logo_layout.php
// 1. Update CSS for Right-Aligned Nav
// 2. Update Header Template with Logo

require_once($_SERVER['DOCUMENT_ROOT'] . '/wp-load.php');
echo "<h1>🎨 Deploying Logo & Right Nav</h1>";

$mu_dir = $_SERVER['DOCUMENT_ROOT'] . '/wp-content/mu-plugins';

// --- PART 1: HYBRID CSS (MU-Plugin) ---
$css_code = <<<'PHP'
<?php
/* Plugin Name: Nuclear Layout Styles V2 */
add_action('wp_head', function() {
    echo '<style>
    /* 1. Force Site Title (CENTER) */
    .wp-block-site-title {
        text-align: center !important;
        width: 100% !important;
        display: block !important;
        margin-bottom: 0.5rem !important;
    }
    .wp-block-site-title a {
        font-family: "Playfair Display", serif !important;
        font-weight: 400 !important;
        text-decoration: none !important;
        font-size: 2.2rem !important;
        display: block !important;
        width: 100% !important;
        text-align: center !important;
    }

    /* 2. Logo (CENTER) */
    .header-logo {
        display: block !important;
        margin: 0 auto 1.5rem auto !important;
        max-width: 150px;
        height: auto;
    }

    /* 3. Navigation (RIGHT) */
    /* We need the container to span full width so 'flex-end' works */
    .wp-block-navigation {
        width: 100% !important;
        display: flex !important;
        justify-content: flex-end !important; /* RIGHT ALIGN */
        padding-right: 2rem; /* Spacing from edge */
    }
    .wp-block-navigation__responsive-container-open {
        margin-left: auto !important; /* Push to right */
        display: flex !important;
    }
    
    /* 4. Utilities */
    .wp-block-post-title { display: none !important; }
    .wp-block-page-list { display: none !important; }
    </style>';
}, 999);
PHP;

file_put_contents($mu_dir . '/nuclear-styles.php', $css_code); // Overwrite previous
echo "✅ Updated CSS to V2 (Title Center, Nav Right).<br>";


// --- PART 2: HEADER TEMPLATE WITH LOGO ---

$nav = get_page_by_path('main-navigation', OBJECT, 'wp_navigation');
$nav_id = $nav ? $nav->ID : 0;
$logo_url = 'https://elliotspencermorgan.com/logo.png';

$header_content = <<<HTML
<!-- wp:group {"align":"full","style":{"spacing":{"padding":{"top":"var:preset|spacing|30","bottom":"var:preset|spacing|30"}}},"layout":{"type":"flex","orientation":"vertical","justifyContent":"center","alignItems":"center"}} -->
<div class="wp-block-group alignfull" style="padding-top:var(--wp--preset--spacing--30);padding-bottom:var(--wp--preset--spacing--30)">
    
    <!-- wp:site-title {"level":1,"textAlign":"center","style":{"typography":{"fontStyle":"normal","fontWeight":"400"}}} /-->

    <!-- wp:image {"sizeSlug":"medium","linkDestination":"none","className":"header-logo"} -->
    <figure class="wp-block-image size-medium header-logo"><img src="$logo_url" alt="Logo" /></figure>
    <!-- /wp:image -->

    <!-- wp:navigation {"ref":$nav_id,"overlayMenu":"always","layout":{"type":"flex","justifyContent":"right","orientation":"horizontal"}} /-->

</div>
<!-- /wp:group -->
HTML;

// Update ALL Header Template Parts (Nuclear Override)
$headers = get_posts([
    'post_type' => 'wp_template_part',
    'post_status' => 'any',
    'numberposts' => -1,
    'tax_query' => [['taxonomy' => 'wp_template_part_area', 'field' => 'slug', 'terms' => 'header']]
]);

if ($headers) {
    foreach ($headers as $h) {
        wp_update_post(['ID' => $h->ID, 'post_content' => $header_content]);
        echo "✅ Updated Header ID " . $h->ID . "<br>";
    }
} else {
    // Fallback Insert
    $id = wp_insert_post([
        'post_title' => 'Header',
        'post_name' => 'twentytwentyfour//header',
        'post_content' => $header_content,
        'post_status' => 'publish',
        'post_type' => 'wp_template_part',
        'tax_input' => ['wp_theme' => ['twentytwentyfour'], 'wp_template_part_area' => ['header']]
    ]);
    if (!is_wp_error($id)) {
        wp_set_object_terms($id, 'twentytwentyfour', 'wp_theme');
        wp_set_object_terms($id, 'header', 'wp_template_part_area');
        echo "✅ Created Header ID $id<br>";
    }
}

if (function_exists('opcache_reset'))
    opcache_reset();
echo "<a href='/fireworks/'>Check /fireworks/</a>";
?>