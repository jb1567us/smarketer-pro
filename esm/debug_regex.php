<?php
require_once('wp-load.php');
$id = 1927;
$post = get_post($id);
$c = $post->post_content;

echo "<h1>Debug Regex for Page $id</h1>";

// Find position of @context
$pos = strpos($c, '{ "@context"');
if ($pos === false) {
    echo "Could not find '{ \"@context\"' in content.<br>";
    // Maybe verify_portal_state used htmlspecialchars and confused me?
    // Let's dump the 500 chars around the Schema comment
    $schema_pos = strpos($c, 'VisualArtwork Schema');
    if ($schema_pos !== false) {
        echo "Found Schema Comment at $schema_pos.<br>";
        $chunk = substr($c, $schema_pos, 200);
        echo "Chunk: <pre>" . htmlspecialchars($chunk) . "</pre>";
        echo "Hex: " . bin2hex($chunk) . "<br>";
    } else {
        echo "Schema comment not found either.<br>";
    }
} else {
    echo "Found '{ \"@context\"' at $pos.<br>";
    $chunk = substr($c, $pos, 300);
    echo "Chunk: <pre>" . htmlspecialchars($chunk) . "</pre>";

    // Test Regex
    $pattern = '/(\{ "@context".*?\})\s*(?=<div)/s';
    if (preg_match($pattern, $c, $m)) {
        echo "REGEX MATCHED!<br>";
        echo "Match: <pre>" . htmlspecialchars($m[0]) . "</pre>";
    } else {
        echo "REGEX FAILED.<br>";
        echo "Preg Last Error: " . preg_last_error() . "<br>";
    }
}
?>