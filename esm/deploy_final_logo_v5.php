<?php
// deploy_final_logo_v5.php
// 1. Re-insert COMPLETE header template with ABSOLUTE URL
// 2. Re-enable esm-core-v2.php for Hamburger Logic

require_once($_SERVER['DOCUMENT_ROOT'] . '/wp-load.php');
echo "<h1>🚑 Restoring Header + Core (V5)</h1>";

$mu_dir = $_SERVER['DOCUMENT_ROOT'] . '/wp-content/mu-plugins';

// 1. RE-ENABLE CORE LOGIC
if (file_exists($mu_dir . '/esm-core-v2.php.off')) {
    rename($mu_dir . '/esm-core-v2.php.off', $mu_dir . '/esm-core-v2.php');
    echo "✅ Re-enabled esm-core-v2.php<br>";
} else {
    echo "✅ esm-core-v2.php was already enabled.<br>";
}

// 2. Re-enable V4 CSS
if (file_exists($mu_dir . '/esm-fixed-logo-v4.php.off')) {
    rename($mu_dir . '/esm-fixed-logo-v4.php.off', $mu_dir . '/esm-fixed-logo-v4.php');
    echo "✅ Re-enabled esm-fixed-logo-v4.php<br>";
} else {
    echo "✅ esm-fixed-logo-v4.php was already enabled.<br>";
}

// 3. GET NAVIGATION ID
$nav = get_page_by_path('main-navigation', OBJECT, 'wp_navigation');
$nav_id = $nav ? $nav->ID : 0;
echo "Navigation ID: $nav_id<br>";

// 4. DEFINE SAFE CONTENT (No Base64)
// Use Absolute URL + time cache buster
$logo_url = 'https://elliotspencermorgan.com/logo.png?v=' . time();

$header_content = <<<HTML
<!-- wp:group {"align":"full","style":{"spacing":{"padding":{"top":"var:preset|spacing|30","bottom":"var:preset|spacing|30"}}},"layout":{"type":"flex","orientation":"vertical","justifyContent":"center","alignItems":"center"}} -->
<div class="wp-block-group alignfull" style="padding-top:var(--wp--preset--spacing--30);padding-bottom:var(--wp--preset--spacing--30)">
    
    <!-- wp:site-title {"level":1,"textAlign":"center","style":{"typography":{"fontStyle":"normal","fontWeight":"400"}}} /-->

    <!-- wp:image {"id":99999,"sizeSlug":"full","linkDestination":"none","className":"header-logo"} -->
    <figure class="wp-block-image size-full header-logo"><img src="$logo_url" alt="Elliot Spencer Morgan Logo - V5" class="wp-image-99999"/></figure>
    <!-- /wp:image -->

    <!-- wp:navigation {"ref":$nav_id,"overlayMenu":"always","layout":{"type":"flex","justifyContent":"right","orientation":"horizontal"}} /-->

</div>
<!-- /wp:group -->
HTML;

// 5. UPDATE TEMPLATES
$headers = get_posts([
    'post_type' => 'wp_template_part',
    'post_status' => 'any',
    'numberposts' => -1,
    'tax_query' => [['taxonomy' => 'wp_template_part_area', 'field' => 'slug', 'terms' => 'header']]
]);

foreach ($headers as $h) {
    wp_update_post(['ID' => $h->ID, 'post_content' => $header_content]);
    echo "✅ Updated Header " . $h->ID . " (Clean URL + ID)<br>";
}

if (function_exists('opcache_reset'))
    opcache_reset();
if (function_exists('wp_cache_flush'))
    wp_cache_flush();

echo "<a href='/fireworks/'>Check Recovery V5</a>";
?>