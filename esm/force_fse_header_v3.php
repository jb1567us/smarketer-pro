<?php
// force_fse_header_v3.php
// 1. Force Hamburger Menu (overlayMenu: always)
// 2. Remove Title from Page Template (Fix Double Title)

require_once($_SERVER['DOCUMENT_ROOT'] . '/wp-load.php');

echo "<h1>🎨 FSE Layout Fixer</h1>";

// --- PART 1: HEADER (Hamburger) ---

// Get Nav ID
$nav = get_page_by_path('main-navigation', OBJECT, 'wp_navigation');
$nav_ref = $nav ? $nav->ID : 0;

$header_content = <<<HTML
<!-- wp:group {"align":"full","style":{"spacing":{"padding":{"top":"var:preset|spacing|20","bottom":"var:preset|spacing|20","left":"var:preset|spacing|40","right":"var:preset|spacing|40"}}},"layout":{"type":"flex","justifyContent":"space-between","flexWrap":"wrap"}} -->
<div class="wp-block-group alignfull" style="padding-top:var(--wp--preset--spacing--20);padding-right:var(--wp--preset--spacing--40);padding-bottom:var(--wp--preset--spacing--20);padding-left:var(--wp--preset--spacing--40)">
    <!-- wp:group {"layout":{"type":"flex","flexWrap":"nowrap"}} -->
    <div class="wp-block-group">
        <!-- wp:site-title {"level":1,"style":{"typography":{"fontStyle":"normal","fontWeight":"400"}}} /-->
    </div>
    <!-- /wp:group -->

    <!-- wp:navigation {"ref":$nav_ref,"overlayMenu":"always","layout":{"type":"flex","justifyContent":"end"}} /-->
</div>
<!-- /wp:group -->
HTML;

$args_header = [
    'post_title' => 'Header',
    'post_name' => 'header',
    'post_content' => $header_content,
    'post_status' => 'publish',
    'post_type' => 'wp_template_part',
    'tax_input' => [
        'wp_theme' => ['twentytwentyfour'],
        'wp_template_part_area' => ['header']
    ]
];

// Update Header
$existing_header = new WP_Query([
    'post_type' => 'wp_template_part',
    'name' => 'header',
    'tax_query' => [['taxonomy' => 'wp_theme', 'field' => 'slug', 'terms' => 'twentytwentyfour']]
]);

if ($existing_header->have_posts()) {
    $existing_header->the_post();
    $args_header['ID'] = get_the_ID();
    $id = wp_update_post($args_header);
    // Re-set terms just in case
    wp_set_object_terms($id, 'twentytwentyfour', 'wp_theme');
    wp_set_object_terms($id, 'header', 'wp_template_part_area');
    echo "✅ Header Updated (Hamburger Mode).<br>";
} else {
    echo "⚠️ Header Template Part not found to update (Expected if previously created).<br>";
}


// --- PART 2: PAGE TEMPLATE (Fix Double Title) ---

// The default Page template usually includes wp:post-title. We want to remove it.
$page_content = <<<HTML
<!-- wp:group {"layout":{"type":"constrained"}} -->
<div class="wp-block-group">
    <!-- wp:post-content {"layout":{"type":"constrained"}} /-->
</div>
<!-- /wp:group -->
HTML;

$args_page = [
    'post_title' => 'Page',
    'post_name' => 'page',
    'post_content' => $page_content,
    'post_status' => 'publish',
    'post_type' => 'wp_template', // Note: wp_template, not wp_template_part
    'tax_input' => [
        'wp_theme' => ['twentytwentyfour']
    ]
];

// Check if we need to override the Theme's file-based template
// FSE allows DB-based posts to override file templates.
// We search for an existing DB override for 'page'
$existing_page = new WP_Query([
    'post_type' => 'wp_template',
    'name' => 'page',
    'tax_query' => [['taxonomy' => 'wp_theme', 'field' => 'slug', 'terms' => 'twentytwentyfour']]
]);

if ($existing_page->have_posts()) {
    $existing_page->the_post();
    $args_page['ID'] = get_the_ID();
    $id = wp_update_post($args_page);
    echo "✅ Page Template Updated (DB Override exists).<br>";
} else {
    // Insert new override
    $id = wp_insert_post($args_page);
    if (!is_wp_error($id)) {
        wp_set_object_terms($id, 'twentytwentyfour', 'wp_theme');
        echo "✅ Page Template Override Created (No Title).<br>";
    } else {
        echo "❌ Error Creating Page Template: " . $id->get_error_message() . "<br>";
    }
}

echo "<a href='/fireworks/'>Check /fireworks/</a>";
?>