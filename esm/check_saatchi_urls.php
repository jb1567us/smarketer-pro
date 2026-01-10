<?php
// check_saatchi_urls.php
// Find out where Saatchi URLs are stored

require_once($_SERVER['DOCUMENT_ROOT'] . '/wp-load.php');
echo "<h1>🔍 Checking Saatchi URLs</h1>";

// Get a sample post
$posts = get_posts([
    'post_type' => 'post',
    'posts_per_page' => 5,
    'post_status' => 'publish'
]);

foreach ($posts as $post) {
    echo "<h3>{$post->post_title}</h3>";

    // Check post meta
    $all_meta = get_post_meta($post->ID);
    echo "<strong>Post Meta:</strong><br>";
    foreach ($all_meta as $key => $value) {
        if (stripos($key, 'saatchi') !== false || stripos($key, 'url') !== false || stripos($key, 'link') !== false) {
            echo "- {$key}: " . print_r($value, true) . "<br>";
        }
    }

    // Check content for Saatchi links
    if (stripos($post->post_content, 'saatchi') !== false) {
        echo "<strong>Content has 'saatchi'</strong><br>";
        // Extract URL from content
        preg_match('/https?:\/\/[^\s<>"]+saatchi[^\s<>"]*/i', $post->post_content, $matches);
        if ($matches) {
            echo "Found URL: {$matches[0]}<br>";
        }
    }

    echo "<hr>";
}
?>