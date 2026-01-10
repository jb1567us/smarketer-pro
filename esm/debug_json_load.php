<?php
// debug_json_load.php
// Place this in your public_html folder and visit it in your browser

define('WP_USE_THEMES', false);
require('wp-load.php');

echo "<h1>🔍 JSON Loader Debugger</h1>";

$json_path = ABSPATH . 'artwork_data.json';
echo "<strong>Checking path:</strong> " . $json_path . "<br>";

if (file_exists($json_path)) {
    echo "✅ <strong>File Found!</strong><br>";
    $content = file_get_contents($json_path);
    echo "<strong>File Size:</strong> " . strlen($content) . " bytes<br>";
    
    $data = json_decode($content, true);
    if ($data) {
        echo "✅ <strong>JSON Valid!</strong> Parsed " . count($data) . " items.<br><br>";
        
        echo "<h3>Checking First 3 Items:</h3>";
        $i = 0;
        foreach ($data as $item) {
            echo "Item: <strong>" . (isset($item['title']) ? $item['title'] : 'No Title') . "</strong><br>";
            echo "Slug: " . (isset($item['slug']) ? $item['slug'] : 'No Slug') . "<br>";
            echo "Type: " . (isset($item['type']) ? $item['type'] : 'No Type') . "<br>";
            echo "<hr>";
            $i++;
            if ($i >= 3) break;
        }
        
        echo "<h3>Checking Current Page Mismatch</h3>";
        echo "Trying to match a sample page...<br>";
        // Try to get a real page ID
        $page = get_page_by_path('caviar'); // Try a known slug
        if ($page) {
             $slug = $page->post_name;
             echo "Found real WP Page: <strong>$slug</strong> (ID: {$page->ID})<br>";
             
             // Try logic from theme
             $found = false;
             foreach ($data as $item) {
                if (
                    (isset($item['slug']) && $item['slug'] === $slug) ||
                    (isset($item['wordpress_id']) && $item['wordpress_id'] == $page->ID) ||
                    (isset($item['title']) && strcasecmp($item['title'], $page->post_title) === 0)
                ) {
                    echo "✅ <strong>MATCH FOUND in JSON!</strong><br>";
                    echo "Price in JSON: " . ($item['price'] ?? 'MISSING') . "<br>";
                    echo "Image in JSON: " . ($item['image_url'] ?? 'MISSING') . "<br>";
                    $found = true;
                    break;
                }
             }
             if (!$found) echo "❌ <strong>NO MATCH FOUND</strong> in JSON for slug: $slug<br>";
        } else {
            echo "Could not find 'caviar' page to test. Try editing this script with a known slug.<br>";
        }
        
    } else {
        echo "❌ <strong>JSON Error:</strong> Failed to decode JSON. Error: " . json_last_error_msg() . "<br>";
    }
} else {
    echo "❌ <strong>File Not Found:</strong> The file is not at the expected path.<br>";
    echo "Current Dir: " . __DIR__ . "<br>";
    echo "Files in this dir: <pre>" . print_r(scandir(__DIR__), true) . "</pre>";
}
?>
