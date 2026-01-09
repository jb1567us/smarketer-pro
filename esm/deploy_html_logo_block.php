<?php
// deploy_html_logo_block.php
// USE RAW HTML BLOCK to bypass Image Block validation (Fake ID issue)

require_once($_SERVER['DOCUMENT_ROOT'] . '/wp-load.php');
echo "<h1>🧱 Deploying HTML Block Logo</h1>";

// 1. GET NAVIGATION ID
$nav = get_page_by_path('main-navigation', OBJECT, 'wp_navigation');
$nav_id = $nav ? $nav->ID : 0;

// 2. DEFINE SAFE CONTENT (Raw HTML Block)
$logo_url = 'https://elliotspencermorgan.com/logo.png?v=HTML_BLOCK';

$header_content = <<<HTML
<!-- wp:group {"align":"full","style":{"spacing":{"padding":{"top":"var:preset|spacing|30","bottom":"var:preset|spacing|30"}}},"layout":{"type":"flex","orientation":"vertical","justifyContent":"center","alignItems":"center"}} -->
<div class="wp-block-group alignfull" style="padding-top:var(--wp--preset--spacing--30);padding-bottom:var(--wp--preset--spacing--30)">
    
    <!-- wp:site-title {"level":1,"textAlign":"center","style":{"typography":{"fontStyle":"normal","fontWeight":"400"}}} /-->

    <!-- wp:html -->
    <div class="header-logo" style="width: 180px; margin: 0 auto 1.5rem auto;">
        <img src="$logo_url" alt="Elliot Spencer Morgan Logo" style="width: 100%; height: auto; display: block;">
    </div>
    <!-- /wp:html -->

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
    wp_update_post(['ID' => $h->ID, 'post_content' => $header_content]);
    echo "✅ Updated Header " . $h->ID . " with HTML Block<br>";
}

if (function_exists('opcache_reset'))
    opcache_reset();
if (function_exists('wp_cache_flush'))
    wp_cache_flush();

echo "<a href='/fireworks/'>Check HTML Block</a>";
?>