<?php
// force_fse_header.php
// Force override the Header Template Part to use our Navigation

require_once($_SERVER['DOCUMENT_ROOT'] . '/wp-load.php');

// 1. Get Navigation ID
$nav = get_page_by_path('main-navigation', OBJECT, 'wp_navigation');
if (!$nav) {
    die("❌ Main Navigation not found. Run fix_fse_menu.php first.");
}
$nav_id = $nav->ID;
echo "✅ Found Navigation ID: $nav_id<br>";

// 2. Prepare Header Content
// This is a simplified header structure matching Twenty Twenty-Four style
$header_content = <<<HTML
<!-- wp:group {"align":"full","style":{"spacing":{"padding":{"top":"var:preset|spacing|20","bottom":"var:preset|spacing|20","left":"var:preset|spacing|40","right":"var:preset|spacing|40"}}},"layout":{"type":"flex","justifyContent":"space-between","flexWrap":"wrap"}} -->
<div class="wp-block-group alignfull" style="padding-top:var(--wp--preset--spacing--20);padding-right:var(--wp--preset--spacing--40);padding-bottom:var(--wp--preset--spacing--20);padding-left:var(--wp--preset--spacing--40)">
    <!-- wp:group {"layout":{"type":"flex","flexWrap":"nowrap"}} -->
    <div class="wp-block-group">
        <!-- wp:site-title {"level":1,"style":{"typography":{"fontStyle":"normal","fontWeight":"400"}}} /-->
    </div>
    <!-- /wp:group -->

    <!-- wp:navigation {"ref":$nav_id,"layout":{"type":"flex","justifyContent":"end"}} /-->
</div>
<!-- /wp:group -->
HTML;

// 3. Insert/Update wp_template_part
// We need to set the taxonomy 'wp_theme' to 'twentytwentyfour'
$args = [
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

// Check existence
$existing = new WP_Query([
    'post_type' => 'wp_template_part',
    'name' => 'header',
    'tax_query' => [
        [
            'taxonomy' => 'wp_theme',
            'field' => 'slug',
            'terms' => 'twentytwentyfour'
        ]
    ]
]);

if ($existing->have_posts()) {
    $existing->the_post();
    $args['ID'] = get_the_ID();
    $id = wp_update_post($args);
    echo "✅ Updated Custom Header (ID: $id)<br>";
} else {
    $id = wp_insert_post($args);
    echo "✅ Inserted Custom Header (ID: $id)<br>";

    // Manually set term because wp_insert_post might fail with tax_input for non-admins?
    // Actually we are running as script, but let's be safe.
    if ($id && !is_wp_error($id)) {
        wp_set_object_terms($id, 'twentytwentyfour', 'wp_theme');
        wp_set_object_terms($id, 'header', 'wp_template_part_area');
    }
}

if (is_wp_error($id)) {
    echo "❌ Error: " . $id->get_error_message();
}

echo "<a href='/fireworks/'>Check /fireworks/</a>";
?>