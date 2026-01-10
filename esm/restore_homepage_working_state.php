<?php
// restore_homepage_working_state.php
// Remove broken plugins and check database

require_once($_SERVER['DOCUMENT_ROOT'] . '/wp-load.php');
echo "<h1>🔧 Restoring Homepage</h1>";

$mu_dir = $_SERVER['DOCUMENT_ROOT'] . '/wp-content/mu-plugins';

// Remove ALL portfolio plugins
$remove_files = [
    'esm-saatchi-portfolio.php',
    'esm-saatchi-direct.php',
    'esm-homepage-grid.php'
];

foreach ($remove_files as $file) {
    if (file_exists($mu_dir . '/' . $file)) {
        unlink($mu_dir . '/' . $file);
        echo "🧹 Removed $file<br>";
    }
}

// Check posts
$posts = get_posts([
    'post_type' => 'post',
    'posts_per_page' => 10,
    'post_status' => 'publish'
]);

echo "<br>Found " . count($posts) . " posts<br><br>";

foreach ($posts as $post) {
    $thumbnail_id = get_post_thumbnail_id($post->ID);
    $has_image = $thumbnail_id ? '✅' : '❌';
    echo "$has_image {$post->post_title}<br>";
}

if (function_exists('opcache_reset'))
    opcache_reset();
if (function_exists('wp_cache_flush'))
    wp_cache_flush();

echo "<br><a href='/'>Check Homepage</a>";
?>