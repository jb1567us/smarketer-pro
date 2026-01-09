<?php
// investigate_collections.php
require_once($_SERVER['DOCUMENT_ROOT'] . '/wp-load.php');

echo "<h1>Listing Potential Collection Pages</h1>";

// Get all pages
$pages = get_posts([
    'post_type' => 'page',
    'numberposts' => -1,
    'post_status' => 'publish'
]);

foreach ($pages as $p) {
    // Filter for likely collection names
    if (
        stripos($p->post_title, 'Collection') !== false ||
        stripos($p->post_title, 'Series') !== false ||
        stripos($p->post_title, 'Portfolio') !== false ||
        in_array($p->post_title, ['Paintings', 'Collages', 'Sculptures', 'Abstract'])
    ) {

        echo "<h3>Found: {$p->post_title} (ID: {$p->ID})</h3>";
        echo "Slug: /{$p->post_name}/<br>";

        // Peek at links inside
        if (preg_match_all('/<a\s+[^>]*href=["\']([^"\']*)["\'][^>]*>(.*?)<\/a>/i', $p->post_content, $matches)) {
            echo "Contains " . count($matches[0]) . " links. Sample:<br>";
            for ($i = 0; $i < min(5, count($matches[0])); $i++) {
                echo " - " . htmlspecialchars($matches[1][$i]) . " (" . htmlspecialchars(strip_tags($matches[2][$i])) . ")<br>";
            }
        } else {
            echo "No links found in content.<br>";
        }
        echo "<hr>";
    }
}
?>