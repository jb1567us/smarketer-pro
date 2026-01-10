<?php
// deploy_final_fixes.php
// 1. Install MU-Plugin for CSS (Double Title)
// 2. Install DB Override for Header (Hamburger)

require_once($_SERVER['DOCUMENT_ROOT'] . '/wp-load.php');
echo "<h1>🔧 Deploying Final Fixes</h1>";

// --- PART 1: CSS Fix (MU-Plugin) ---
$mu_dir = $_SERVER['DOCUMENT_ROOT'] . '/wp-content/mu-plugins';
if (!is_dir($mu_dir)) {
    mkdir($mu_dir, 0755, true);
}

$css_fix = <<<'PHP'
<?php
/* Plugin Name: FSE Style Fix */
add_action('wp_head', function() {
    // Hide default Theme Title (Fixes Double Title)
    echo '<style>.wp-block-post-title { display: none !important; }</style>';
});
PHP;

file_put_contents($mu_dir . '/fse-style-fix.php', $css_fix);
echo "✅ Installed MU-Plugin (Double Title Fix)<br>";


// --- PART 2: Hamburger Fix (DB Override) ---

// Get Nav ID
$nav = get_page_by_path('main-navigation', OBJECT, 'wp_navigation');
$nav_id = $nav ? $nav->ID : 0;
echo "Nav ID: $nav_id<br>";

// Header Content with Hamburger Forced
// We use raw inner blocks just in case 'ref' is flaky in overrides
// No wait, 'ref' is better if Main Menu exists.
$header_content = <<<HTML
<!-- wp:group {"align":"full","style":{"spacing":{"padding":{"top":"var:preset|spacing|20","bottom":"var:preset|spacing|20","left":"var:preset|spacing|40","right":"var:preset|spacing|40"}}},"layout":{"type":"flex","justifyContent":"space-between","flexWrap":"wrap"}} -->
<div class="wp-block-group alignfull" style="padding-top:var(--wp--preset--spacing--20);padding-right:var(--wp--preset--spacing--40);padding-bottom:var(--wp--preset--spacing--20);padding-left:var(--wp--preset--spacing--40)">
    <!-- wp:group {"layout":{"type":"flex","flexWrap":"nowrap"}} -->
    <div class="wp-block-group">
        <!-- wp:site-title {"level":1,"style":{"typography":{"fontStyle":"normal","fontWeight":"400"}}} /-->
    </div>
    <!-- /wp:group -->

    <!-- wp:navigation {"ref":$nav_id,"overlayMenu":"always","layout":{"type":"flex","justifyContent":"end","orientation":"horizontal"}} /-->
</div>
<!-- /wp:group -->
HTML;

// Insert with SPECIFIC SLUG "twentytwentyfour//header"
$args = [
    'post_title' => 'Header',
    'post_name' => 'twentytwentyfour//header', // CRITICAL for FSE
    'post_content' => $header_content,
    'post_status' => 'publish',
    'post_type' => 'wp_template_part',
    'tax_input' => [
        'wp_theme' => ['twentytwentyfour'],
        'wp_template_part_area' => ['header']
    ]
];

// Check if exists
$query = new WP_Query([
    'post_type' => 'wp_template_part',
    'name' => 'twentytwentyfour//header',
    'post_status' => 'any'
]);

if ($query->have_posts()) {
    $query->the_post();
    $args['ID'] = get_the_ID();
    $id = wp_update_post($args);
    echo "✅ Updated DB Header Override (ID: $id)<br>";
} else {
    $id = wp_insert_post($args);
    echo "✅ Inserted DB Header Override (ID: $id)<br>";
}

if (!is_wp_error($id)) {
    // Force Terms again
    wp_set_object_terms($id, 'twentytwentyfour', 'wp_theme');
    wp_set_object_terms($id, 'header', 'wp_template_part_area');
}

// Flush
if (function_exists('opcache_reset'))
    opcache_reset();

echo "<a href='/fireworks/'>Check /fireworks/</a>";
?>