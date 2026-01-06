<?php
// inspect_collection_images.php
require_once($_SERVER['DOCUMENT_ROOT'] . '/wp-load.php');

$ids = [2218, 2216, 2215]; // Sculpture, Blue, Gold

echo "<h1>Inspecting Collection Images</h1>";

foreach ($ids as $id) {
    $p = get_post($id);
    if (!$p) continue;
    
    echo "<h3>{$p->post_title} (ID: $id)</h3>";
    $content = $p->post_content;
    
    // Find anchors containing images
    // Regex: <a [^>]+>.*?<img [^>]+>.*?</a>
    
    if (preg_match_all('/(<a\s+[^>]*href=["\']([^"\']*)["\'][^>]*>)\s*(<img\s+[^>]*>)\s*<\/a>/is', $content, $matches)) {
        echo "Found " . count($matches[0]) . " image links.<br><ul>";
        foreach ($matches[0] as $i => $fullTag) {
            $href = $matches[2][$i];
            $imgTag = $matches[3][$i];
            
            // Extract Alt Text from Img
            preg_match('/alt=["\']([^"\']*)["\']/i', $imgTag, $altMatch);
            $alt = $altMatch[1] ?? 'No Alt';
            
            echo "<li><strong>Href:</strong> $href <br><strong>Alt:</strong> $alt</li>";
        }
        echo "</ul>";
    } else {
        echo "No image links found.<br>";
    }
    echo "<hr>";
}
?>
