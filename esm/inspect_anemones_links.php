<?php
// inspect_anemones_links.php
// Get the links from the DB content

require_once($_SERVER['DOCUMENT_ROOT'] . '/wp-load.php');

$id = 213;
$post = get_post($id);

echo "<h1>🔍 Content Link Inspector</h1>";
if ($post) {
    $content = $post->post_content;

    // Look for hrefs
    preg_match_all('/href="([^"]+)"/i', $content, $matches);

    echo "<h3>Found Links:</h3><ul>";
    foreach ($matches[1] as $link) {
        echo "<li>$link</li>";
    }
    echo "</ul>";

    // Look for "Designer Specs" block keywords
    echo "<h3>Specs Check:</h3>";
    $keywords = ['Designer Specifications', 'Spec Sheet', 'High-Res', 'zip', 'pdf'];
    foreach ($keywords as $k) {
        if (stripos($content, $k) !== false) {
            echo "✅ Found '$k'<br>";
        } else {
            echo "❌ Missing '$k'<br>";
        }
    }

    // Dump a chunk around "Spec Sheet"
    $pos = stripos($content, 'Spec Sheet');
    if ($pos !== false) {
        echo "<h3>Context Chunk:</h3>";
        echo "<pre>" . htmlspecialchars(substr($content, $pos - 200, 500)) . "</pre>";
    }
}
?>