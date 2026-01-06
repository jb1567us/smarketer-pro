<?php
// patch_theme_files.php
// Directly modify TwentyTwentyFour HTML templates

require_once($_SERVER['DOCUMENT_ROOT'] . '/wp-load.php');

$theme_dir = $_SERVER['DOCUMENT_ROOT'] . '/wp-content/themes/twentytwentyfour';
echo "<h1>🩹 Theme Patcher</h1>";

// 1. Get Navigation ID
$nav = get_page_by_path('main-navigation', OBJECT, 'wp_navigation');
$nav_id = $nav ? $nav->ID : 0;
echo "Navigation ID: $nav_id<br>";

// 2. CLEANUP DB OVERRIDES (To ensure file templates are used)
$overrides = new WP_Query([
    'post_type' => ['wp_template', 'wp_template_part'],
    'post_status' => 'any',
    'tax_query' => [['taxonomy' => 'wp_theme', 'field' => 'slug', 'terms' => 'twentytwentyfour']]
]);
if ($overrides->have_posts()) {
    while ($overrides->have_posts()) {
        $overrides->the_post(); // Necessary to setup post data, even if we just need ID
        $oid = get_the_ID();
        // Be careful not to delete standard posts if query is wrong, but tax_query protects us
        wp_delete_post($oid, true);
        echo "Deleted DB Override ID: $oid (" . get_the_title() . ")<br>";
    }
}
wp_reset_postdata();


// 3. Patch Header (Hamburger + Ref)
$header_file = $theme_dir . '/parts/header.html';
if (file_exists($header_file)) {
    $content = file_get_contents($header_file);
    // Regex to find existing navigation block
    // It looks like <!-- wp:navigation {...} /-->
    // We replace the JSON attributes.

    // New block HTML. We use 'ref' pointing to our nav post.
    // overlayMenu: always forces hamburger.
    $new_nav = '<!-- wp:navigation {"ref":' . $nav_id . ',"overlayMenu":"always","layout":{"type":"flex","justifyContent":"right","orientation":"horizontal"}} /-->';

    // Replace the block
    $pattern = '/<!-- wp:navigation .*? \/-->/s';
    $new_content = preg_replace($pattern, $new_nav, $content);

    if ($new_content && $new_content !== $content) {
        file_put_contents($header_file, $new_content);
        echo "✅ Patched header.html (Added Hamburger + Linked Menu)<br>";
    } else {
        echo "⚠️ Regex failed or content unchanged for header.html<br>";
    }
} else {
    echo "❌ header.html not found<br>";
}

// 4. Patch Page/Single (Remove Title)
$templates = [
    $theme_dir . '/templates/page.html',
    $theme_dir . '/templates/single.html'
];

foreach ($templates as $file) {
    if (file_exists($file)) {
        $content = file_get_contents($file);
        // Regex to remove post-title block
        // <!-- wp:post-title {"textAlign":"center","level":1} /-->
        $pattern = '/<!-- wp:post-title .*? \/-->/s';
        $new_content = preg_replace($pattern, '', $content);

        if ($new_content && $new_content !== $content) {
            file_put_contents($file, $new_content);
            echo "✅ Patched " . basename($file) . " (Removed Title Block)<br>";
        } else {
            // It might already be removed, or regex mismatch
            if (strpos($content, 'wp:post-title') === false) {
                echo "ℹ️ " . basename($file) . " has no title block (Already patched?)<br>";
            } else {
                echo "⚠️ Regex failed for " . basename($file) . "<br>";
            }
        }
    }
}

// 5. CACHE FLUSH
if (function_exists('opcache_reset')) {
    opcache_reset();
    echo "✅ OPCACHE RESET executed.<br>";
}

echo "<a href='/fireworks/'>Check /fireworks/</a>";
?>