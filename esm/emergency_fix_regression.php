<?php
// emergency_fix_regression.php
// REVERT Base64 (Caused Block Validation Failure)
// RESTORE Absolute URL + Fix Menu

require_once($_SERVER['DOCUMENT_ROOT'] . '/wp-load.php');
echo "<h1>🚑 Fix Regression (Revert Base64)</h1>";

// 1. GET NAVIGATION ID
$nav = get_page_by_path('main-navigation', OBJECT, 'wp_navigation');
$nav_id = $nav ? $nav->ID : 0;
echo "Navigation ID: $nav_id<br>";

// 2. DEFINE SAFE CONTENT (No Base64)
// Use Absolute URL for reliability
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

// 3. UPDATE TEMPLATES
$headers = get_posts([
    'post_type' => 'wp_template_part',
    'post_status' => 'any',
    'numberposts' => -1,
    'tax_query' => [['taxonomy' => 'wp_template_part_area', 'field' => 'slug', 'terms' => 'header']]
]);

foreach ($headers as $h) {
    // Force direct update
    $updated = wp_update_post(['ID' => $h->ID, 'post_content' => $header_content]);
    if ($updated) {
        echo "✅ Restored Header " . $h->ID . " (Clean URL)<br>";
    } else {
        echo "❌ Failed to update Header " . $h->ID . "<br>";
    }
}

// 4. VERIFY LOGO FILE ACCESSIBILITY
$headers = @get_headers($logo_url);
echo "Logo URL Check: " . ($headers && strpos($headers[0], '200') ? "✅ 200 OK" : "❌ " . $headers[0]) . "<br>";

if (function_exists('opcache_reset'))
    opcache_reset();
if (function_exists('wp_cache_flush'))
    wp_cache_flush();

echo "<a href='/fireworks/'>Check Recovery</a>";
?>