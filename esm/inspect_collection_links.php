<?php
// inspect_collection_links.php
require_once($_SERVER['DOCUMENT_ROOT'] . '/wp-load.php');

$ids = [2218, 2216, 2215]; // Sculpture, Blue, Gold

echo "<h1>Inspecting Collection Links</h1>";

foreach ($ids as $id) {
    $p = get_post($id);
    if (!$p)
        continue;

    echo "<h3>{$p->post_title} (ID: $id)</h3>";
    $content = $p->post_content;

    // Extract all links
    if (preg_match_all('/<a\s+[^>]*href=["\']([^"\']*)["\'][^>]*>(.*?)<\/a>/i', $content, $matches)) {
        echo "Found " . count($matches[0]) . " links.<br><ul>";
        foreach ($matches[1] as $i => $href) {
            $text = strip_tags($matches[2][$i]);
            echo "<li><strong>Href:</strong> $href <br><strong>Text:</strong> $text</li>";
        }
        echo "</ul>";
    } else {
        echo "No links found.<br>";
    }
    echo "<hr>";
}
?>