<?php
// deploy_base64_logo_and_width.php
// 1. Convert Server Logo to Base64 (Bypass HTTP issues)
// 2. Force Body Width 100%

require_once($_SERVER['DOCUMENT_ROOT'] . '/wp-load.php');
echo "<h1>💎 Deploying Ultimate Fix (Base64 + Body 100%)</h1>";

$mu_dir = $_SERVER['DOCUMENT_ROOT'] . '/wp-content/mu-plugins';
if (!is_dir($mu_dir)) {
    mkdir($mu_dir, 0755, true);
}

// --- STEP 1: PREPARE BASE64 LOGO ---
$logo_path = $_SERVER['DOCUMENT_ROOT'] . '/logo.png';
$base64_logo = '';

if (file_exists($logo_path)) {
    $data = file_get_contents($logo_path);
    $base64_logo = 'data:image/png;base64,' . base64_encode($data);
    echo "✅ Converted Logo to Base64 (Length: " . strlen($base64_logo) . ")<br>";
} else {
    // Fallback to absolute URL if file missing (unlikely)
    $base64_logo = 'https://elliotspencermorgan.com/logo.png';
    echo "⚠️ Logo file not found on disk, using URL fallback.<br>";
}


// --- STEP 2: INSTALL V3 CSS (Body 100% + Fixed Logo) ---
$css_code = <<<'PHP'
<?php
/* Plugin Name: ESM Ultimate Style V3 */
/* Description: Body 100%, Base64 Logo Support, Fixed 180px */

add_action('wp_head', function() {
    echo '<style>
    /* 1. GLOBAL RESET & WIDTH FORCE (User Request) */
    html, body {
        width: 100% !important;
        max-width: 100vw !important;
        margin: 0 !important;
        padding: 0 !important;
        overflow-x: hidden !important; /* Prevent scrollbar from forced widths */
    }

    /* 2. HEADER CONTAINER */
    header .wp-block-group {
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        width: 100% !important;
        padding-left: 0 !important;
        padding-right: 0 !important;
    }

    /* 3. SITE TITLE */
    .wp-block-site-title {
        text-align: center !important;
        width: 100% !important;
        display: block !important;
        margin: 1rem 0 0.5rem 0 !important;
    }
    .wp-block-site-title a {
        font-family: "Playfair Display", serif !important;
        font-weight: 400 !important;
        font-size: 2.5rem !important;
        line-height: 1.2 !important;
        color: #1a1a1a !important;
        display: block !important;
        width: 100% !important;
        text-align: center !important;
        text-decoration: none !important;
    }

    /* 4. LOGO (FIXED 180px matches User Request) */
    .header-logo {
        display: block !important;
        margin: 0 auto 1.5rem auto !important;
        width: 180px !important; 
        max-width: 100% !important;
    }
    .header-logo img {
        display: block !important;
        margin: 0 auto !important;
        width: 100% !important;
        height: auto !important;
    }

    /* 5. NAVIGATION (RIGHT) */
    .wp-block-navigation {
        width: 100% !important;
        display: flex !important;
        flex-direction: row !important;
        justify-content: flex-end !important;
        padding-right: 2rem !important;
        box-sizing: border-box !important;
    }
    .wp-block-navigation__responsive-container,
    .wp-block-navigation__responsive-container-open {
        margin-left: auto !important;
        margin-right: 0 !important;
        display: flex !important;
    }

    /* UTILS */
    .wp-block-post-title { display: none !important; }
    .wp-block-page-list { display: none !important; }
    </style>';
}, 999);
PHP;

file_put_contents($mu_dir . '/esm-fixed-logo-v3.php', $css_code);
echo "✅ Installed: esm-fixed-logo-v3.php<br>";


// --- STEP 3: UPDATE DB HEADER with BASE64 IMAGE ---
$nav = get_page_by_path('main-navigation', OBJECT, 'wp_navigation');
$nav_id = $nav ? $nav->ID : 0;

$header_content = <<<HTML
<!-- wp:group {"align":"full","style":{"spacing":{"padding":{"top":"var:preset|spacing|30","bottom":"var:preset|spacing|30"}}},"layout":{"type":"flex","orientation":"vertical","justifyContent":"center","alignItems":"center"}} -->
<div class="wp-block-group alignfull" style="padding-top:var(--wp--preset--spacing--30);padding-bottom:var(--wp--preset--spacing--30)">
    
    <!-- wp:site-title {"level":1,"textAlign":"center","style":{"typography":{"fontStyle":"normal","fontWeight":"400"}}} /-->

    <!-- wp:image {"sizeSlug":"full","linkDestination":"none","className":"header-logo"} -->
    <figure class="wp-block-image size-full header-logo"><img src="$base64_logo" alt="Logo" /></figure>
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
    echo "✅ Updated Header ID " . $h->ID . " with Base64 Logo<br>";
}

// Clean up V2
if (file_exists($mu_dir . '/esm-fixed-logo-v2.php')) {
    unlink($mu_dir . '/esm-fixed-logo-v2.php');
    echo "🧹 Removed V2 CSS.<br>";
}

if (function_exists('opcache_reset'))
    opcache_reset();
if (function_exists('wp_cache_flush'))
    wp_cache_flush();

echo "<a href='/fireworks/'>Check /fireworks/</a>";
?>