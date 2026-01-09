<?php
// deploy_logo_cache_bust.php
// 1. CHMOD logo.png (Fix Permissions)
// 2. Update Header Template with CACHE-BUSTED URL (?v=FIX)

require_once($_SERVER['DOCUMENT_ROOT'] . '/wp-load.php');
echo "<h1>🧹 Logo Cache Bust & Permission Fix</h1>";

// --- STEP 1: PERMISSIONS ---
$logo_path = $_SERVER['DOCUMENT_ROOT'] . '/logo.png';
if (file_exists($logo_path)) {
    chmod($logo_path, 0644);
    echo "✅ Set logo.png permissions to 644 (World Readable)<br>";
} else {
    echo "⚠️ logo.png not found on disk!<br>";
}

// --- STEP 2: CACHE BUST URL ---
$nav = get_page_by_path('main-navigation', OBJECT, 'wp_navigation');
$nav_id = $nav ? $nav->ID : 0;

// Unique Version String
$force_url = 'https://elliotspencermorgan.com/logo.png?v=FINAL_FIX_' . time();

$header_content = <<<HTML
<!-- wp:group {"align":"full","style":{"spacing":{"padding":{"top":"var:preset|spacing|30","bottom":"var:preset|spacing|30"}}},"layout":{"type":"flex","orientation":"vertical","justifyContent":"center","alignItems":"center"}} -->
<div class="wp-block-group alignfull" style="padding-top:var(--wp--preset--spacing--30);padding-bottom:var(--wp--preset--spacing--30)">
    
    <!-- wp:site-title {"level":1,"textAlign":"center","style":{"typography":{"fontStyle":"normal","fontWeight":"400"}}} /-->

    <!-- wp:image {"sizeSlug":"full","linkDestination":"none","className":"header-logo"} -->
    <figure class="wp-block-image size-full header-logo"><img src="$force_url" alt="Elliot Spencer Morgan Logo - If seeing this text, image blocked" /></figure>
    <!-- /wp:image -->

    <!-- wp:navigation {"ref":$nav_id,"overlayMenu":"always","layout":{"type":"flex","justifyContent":"right","orientation":"horizontal"}} /-->

</div>
<!-- /wp:group -->
HTML;

// Update ALL headers
$headers = get_posts([
    'post_type' => 'wp_template_part',
    'post_status' => 'any',
    'numberposts' => -1,
    'tax_query' => [['taxonomy' => 'wp_template_part_area', 'field' => 'slug', 'terms' => 'header']]
]);

foreach ($headers as $h) {
    wp_update_post(['ID' => $h->ID, 'post_content' => $header_content]);
    echo "✅ Updated Header " . $h->ID . " with Cache-Busted URL<br>";
}

if (function_exists('opcache_reset'))
    opcache_reset();
if (function_exists('wp_cache_flush'))
    wp_cache_flush();

echo "<a href='/fireworks/'>Check Forced Update</a>";
?>