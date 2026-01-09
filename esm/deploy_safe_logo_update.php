<?php
// deploy_safe_logo_update.php
// Re-applies the Header Template Update (DB Only - No Plugin Changes)

require_once($_SERVER['DOCUMENT_ROOT'] . '/wp-load.php');
echo "<h1>🎨 Re-Deploying Header w/ Logo</h1>";

$nav = get_page_by_path('main-navigation', OBJECT, 'wp_navigation');
$nav_id = $nav ? $nav->ID : 0;
// Use root-relative path which is safer than full URL sometimes
$logo_url = '/logo.png';

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

// 1. Update Existing 'header' parts
$headers = get_posts([
    'post_type' => 'wp_template_part',
    'post_status' => 'any',
    'numberposts' => -1,
    'tax_query' => [['taxonomy' => 'wp_template_part_area', 'field' => 'slug', 'terms' => 'header']]
]);

$found = false;
foreach ($headers as $h) {
    wp_update_post([
        'ID' => $h->ID,
        'post_content' => $header_content
    ]);
    echo "✅ Updated DB Header ID " . $h->ID . " (" . $h->post_name . ")<br>";
    $found = true;
}

// 2. Force Create specific slug if not found or just to be safe
if (!$found) {
    $args = [
        'post_title' => 'Header',
        'post_name' => 'twentytwentyfour//header',
        'post_content' => $header_content,
        'post_status' => 'publish',
        'post_type' => 'wp_template_part',
        'tax_input' => [
            'wp_theme' => ['twentytwentyfour'],
            'wp_template_part_area' => ['header']
        ]
    ];
    $id = wp_insert_post($args);
    if (!is_wp_error($id)) {
        wp_set_object_terms($id, 'twentytwentyfour', 'wp_theme');
        wp_set_object_terms($id, 'header', 'wp_template_part_area');
        echo "✅ Created New Header ID $id<br>";
    }
}

if (function_exists('opcache_reset'))
    opcache_reset();
echo "<a href='/fireworks/'>Check /fireworks/</a>";
?>