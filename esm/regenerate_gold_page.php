<?php
// Regeneration Script for Gold Collection
require_once('wp-load.php');

$collection_key = 'gold-collection';
$json_path = 'collections_data.json';
// Page slug to find ID dynamically
$page_slug = 'gold-collection';

// Debug path
echo "Current dir: " . getcwd() . "\n";
if (!file_exists($json_path)) {
    die("JSON file '$json_path' not found."); 
}

$json_content = file_get_contents($json_path);
if (!$json_content) { die("Failed to read JSON."); }
$data = json_decode($json_content, true);

if (!isset($data[$collection_key])) { die("Collection key not found in JSON."); }

$collection = $data[$collection_key];
$artworks = $collection['artworks'];

// Find Page ID
$page = get_page_by_path($page_slug);
if (!$page) {
    die("Page '$page_slug' not found.");
}
$page_id = $page->ID;
echo "Found Page ID: $page_id for slug '$page_slug'\n";

echo "Regenerating page for: " . $collection['title'] . "\n";
echo "Found " . count($artworks) . " artworks (Data Source: JSON)\n";

// Filter out Gold Series 007-011 explicitly if they still exist for any reason
$exclude = [
    "Gold Series 007", 
    "Gold Series 008", 
    "Gold Series 009", 
    "Gold Series 010", 
    "Gold Series 011"
];

$artworks = array_filter($artworks, function($a) use ($exclude) {
    // Check cleanTitle or title
    $t = isset($a['title']) ? $a['title'] : '';
    $ct = isset($a['cleanTitle']) ? $a['cleanTitle'] : '';
    return !in_array($t, $exclude) && !in_array($ct, $exclude);
});

echo "Artworks after filtering: " . count($artworks) . "\n";

// Helper to build related links keys
$all_collections = $data;
$related_links_html = '';
foreach ($all_collections as $k => $c) {
    if ($k === $collection_key) continue;
    $related_links_html .= '<li><a href="/' . $c['slug'] . '">' . $c['title'] . '</a></li>' . "\n            ";
}

$artwork_cards_html = '';
foreach ($artworks as $artwork) {
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
            <a href="' . $link . '" style="display: block; width: 100%;">
                <img src="' . $image . '" alt="' . $title . '" class="no-lazy skip-lazy" data-no-lazy="1" style="width: 100%; aspect-ratio: 3/4; object-fit: cover; margin-bottom: 10px;">
            </a>
            <h3 style="font-size: 18px; margin: 10px 0;"><a href="' . $link . '" style="text-decoration: none; color: #000;">' . $title . '</a></h3>
            <p class="details" style="font-size: 14px; color: #666;">' . $dims . ' | ' . $medium . '</p>
        </div>';
        
    $artwork_cards_html .= $card;
}

$final_html = '
<div class="collection-page" style="margin-bottom: 60px;">
    <div class="collection-header" style="text-align: center; max-width: 800px; margin: 0 auto 50px auto;">
        <h1 style="font-family: \'Playfair Display\', serif; font-size: 3rem; margin-bottom: 20px;">' . $collection['title'] . '</h1>
        <p class="collection-intro" style="font-size: 1.1rem; line-height: 1.6; color: #555;">' . $collection['description'] . '</p>
    </div>
    
    <div class="gold-collection-grid">
        ' . $artwork_cards_html . '
    </div>
    
    <div class="collection-cta" style="text-align: center; margin: 80px 0; padding: 60px 20px; background: #fafafa; border-radius: 4px;">
        <h2 style="font-family: \'Playfair Display\', serif; margin-bottom: 15px;">Questions About This Collection?</h2>
        <p style="margin-bottom: 25px; color: #666;">I\'d love to help you find the perfect piece for your space.</p>
        <div style="display: flex; gap: 20px; justify-content: center; flex-wrap: wrap;">
            <a href="/contact" style="display: inline-block; background: #1a1a1a; color: #fff; padding: 15px 40px; text-decoration: none; text-transform: uppercase; letter-spacing: 1px; font-size: 14px; transition: opacity 0.3s;">Get in Touch</a>
            <a href="/trade" style="display: inline-block; border: 1px solid #1a1a1a; color: #1a1a1a; padding: 15px 40px; text-decoration: none; text-transform: uppercase; letter-spacing: 1px; font-size: 14px; transition: all 0.3s;">Trade Program</a>
        </div>
    </div>
    
    <div class="related-collections" style="margin: 60px 0; border-top: 1px solid #eee; padding-top: 60px;">
        <h2 style="text-align: center; font-family: \'Playfair Display\', serif; margin-bottom: 40px;">Explore More Collections</h2>
        <ul class="related-grid" style="list-style: none; padding: 0; display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; text-align: center;">
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
