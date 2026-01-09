<?php
// Regeneration Script for Sculpture Collection
require_once('wp-load.php');

$collection_key = 'sculpture-collection';
// On server, the file is collections_data.json
$json_path = 'collections_data.json'; 
$page_id = 2218; 

// Debug path
echo "Current dir: " . getcwd() . "\n";
if (!file_exists($json_path)) {
    echo "Files in dir:\n";
    $files = scandir('.');
    foreach ($files as $f) {
        if (strpos($f, 'json') !== false) {
            echo "- $f\n";
        }
    }
    die("JSON file '$json_path' not found."); 
}

$json_content = file_get_contents($json_path);
if (!$json_content) { die("Failed to read JSON."); }
$data = json_decode($json_content, true);

if (!isset($data[$collection_key])) { die("Collection key not found in JSON."); }

$collection = $data[$collection_key];
$artworks = $collection['artworks'];

echo "Regenerating page for: " . $collection['title'] . "\n";
echo "Found " . count($artworks) . " artworks (Data Source: JSON)\n";

// Filter out Floating Leaves just in case
$artworks = array_filter($artworks, function($a) {
    return $a['title'] !== 'Floating Leaves';
});

// Helper to build related links keys
$all_collections = $data;
$related_links_html = '';
foreach ($all_collections as $k => $c) {
    if ($k === $collection_key) continue;
    $related_links_html .= '<li><a href="/' . $c['slug'] . '">' . $c['title'] . '</a></li>' . "\n            ";
}

$artwork_cards_html = '';
foreach ($artworks as $artwork) {
    // Logic from JS
    $dims = isset($artwork['dimensions']) ? $artwork['dimensions'] : '? W x ? H in';
    $medium = isset($artwork['mediumsDetailed']) ? $artwork['mediumsDetailed'] : (isset($artwork['medium']) ? $artwork['medium'] : 'Mixed Media');
    
    $link = '';
    if (isset($artwork['link']) && strpos($artwork['link'], 'elliotspencermorgan.com') !== false) {
        $link = $artwork['link'];
    } elseif (isset($artwork['slug'])) {
        $link = '/' . $artwork['slug'];
    } else {
        $slug = strtolower(preg_replace('/[^a-z0-9]+/i', '-', $artwork['title']));
        $slug = trim($slug, '-');
        $link = '/' . $slug;
    }
    
    $image = isset($artwork['image_url']) ? $artwork['image_url'] : '';
    $title = $artwork['title'];
    
    $card = '
        <div class="artwork-card" style="text-align: center;">
            <a href="' . $link . '">
                <img src="' . $image . '" alt="' . $title . '" style="width: 100%; height: auto; margin-bottom: 10px;">
            </a>
            <h3 style="font-size: 18px; margin: 10px 0;"><a href="' . $link . '" style="text-decoration: none; color: #000;">' . $title . '</a></h3>
            <p class="details" style="font-size: 14px; color: #666;">' . $dims . ' | ' . $medium . '</p>
        </div>';
        
    $artwork_cards_html .= $card;
}

$final_html = '
<div class="collection-page">
    <h1>' . $collection['title'] . '</h1>
    <p class="collection-intro">' . $collection['description'] . '</p>
    
    <div class="collection-grid" style="display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 30px; margin: 40px 0;">
        ' . $artwork_cards_html . '
    </div>
    
    <div class="collection-cta" style="text-align: center; margin: 60px 0; padding: 40px; background: #f5f5f5;">
        <h2>Questions About This Collection?</h2>
        <p>I\'d love to help you find the perfect piece for your space.</p>
        <p><a href="/contact" style="display: inline-block; background: #000; color: #fff; padding: 12px 30px; text-decoration: none; margin: 10px;">Get in Touch</a></p>
        <p>Interior Designer? <a href="/trade">View our Trade Program</a></p>
    </div>
    
    <div class="related-collections" style="margin: 40px 0;">
        <h2>Explore More Collections</h2>
        <ul style="list-style: none; padding: 0;">
            ' . $related_links_html . '
        </ul>
    </div>
</div>';

$updated_post = array(
    'ID'           => $page_id,
    'post_content' => $final_html
);

$result = wp_update_post($updated_post);

if (is_wp_error($result)) {
    echo "ERROR updating post: " . $result->get_error_message() . "\n";
} else {
    echo "SUCCESS: Page regenerated. Content length: " . strlen($final_html) . " bytes.\n";
}
