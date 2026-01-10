<?php
// debug_portfolio_html.php
// Check what's actually in the portfolio.html file

$html_content = file_get_contents($_SERVER['DOCUMENT_ROOT'] . '/portfolio.html');

echo "<h1>🔍 Portfolio HTML Debug</h1>";

// Check if file exists and has content
if ($html_content) {
    echo "✅ File exists<br>";
    echo "File size: " . strlen($html_content) . " bytes<br><br>";

    // Count artwork items
    $count = substr_count($html_content, 'class="artwork-item"');
    echo "Artwork items in HTML: $count<br><br>";

    // Show first artwork item if it exists
    if (preg_match('/<div class="artwork-item">(.*?)<\/div>/s', $html_content, $match)) {
        echo "<h3>First Artwork Item HTML:</h3>";
        echo "<pre>" . htmlspecialchars($match[0]) . "</pre>";
    } else {
        echo "❌ No artwork items found in HTML<br>";
    }

    // Check if there are any image tags
    $img_count = substr_count($html_content, '<img');
    echo "<br>Total &lt;img&gt; tags: $img_count<br>";

} else {
    echo "❌ File not found or empty<br>";
}

// Also check posts directly
require_once($_SERVER['DOCUMENT_ROOT'] . '/wp-load.php');

echo "<hr><h3>WordPress Posts Check:</h3>";

$posts = get_posts([
    'post_type' => 'post',
    'posts_per_page' => 5,
    'post_status' => 'publish'
]);

echo "Found " . count($posts) . " posts in WordPress<br><br>";

foreach ($posts as $post) {
    $thumbnail_id = get_post_thumbnail_id($post->ID);
    $image_url = $thumbnail_id ? wp_get_attachment_image_url($thumbnail_id, 'large') : 'NONE';

    echo ($thumbnail_id ? '✅' : '❌') . " {$post->post_title}<br>";
    echo "   Image: $image_url<br>";
}
?>