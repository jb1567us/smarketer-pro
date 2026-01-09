<?php
// load WP environment
require_once(__DIR__ . '/wp-load.php');

// Enable error reporting
ini_set('display_errors', 1);
ini_set('display_startup_errors', 1);
error_reporting(E_ALL);

// Load JSON data
$json_content = file_get_contents(__DIR__ . '/collections_data.json');
if (!$json_content) {
    die("ERROR: Could not read collections_data.json\n");
}

$data = json_decode($json_content, true);
if (!$data) {
    die("ERROR: invalid JSON\n");
}

// Function to regenerate a single collection page
function regenerate_collection_page($slug, $collection) {
    echo "Regenerating page for: " . $collection['title'] . " (Slug: $slug)\n";

    // 1. Get artworks
    $artworks = isset($collection['artworks']) ? $collection['artworks'] : [];
    if (empty($artworks) && isset($collection['artwork_ids'])) {
         // Fallback logic if needed, but currently we consume full objects
    }

    echo "Found " . count($artworks) . " artworks.\n";

    // 4. Final HTML Structure - NOW HANDLED BY esm-collection-template.php
    $final_html = '<!-- ESM Collection Template Active -->';

    // 5. Update WordPress Page
    $page = get_page_by_path($slug);
    if (!$page) {
        echo "WARNING: Page not found for slug '$slug'. Creating it...\n";
        $page_id = wp_insert_post([
            'post_title' => $collection['title'],
            'post_name' => $slug,
            'post_content' => $final_html,
            'post_status' => 'publish',
            'post_type' => 'page'
        ]);
    } else {
        $page_id = $page->ID;
        echo "Found Page ID: $page_id for slug '$slug'\n";
        
        $updated_post = array(
            'ID'           => $page_id,
            'post_content' => $final_html
        );
    
        $result = wp_update_post($updated_post);
        if (is_wp_error($result)) {
            echo "ERROR updating post: " . $result->get_error_message() . "\n";
        } else {
            echo "SUCCESS: Page updated.\n";
        }
    }
}

// MAIN LOOP
$target_collections = [
    'gold-collection',
    'blue-turquoise-collection',
    'oversized-statement-pieces',
    'sculpture-collection',
    'pattern-geometric',
    'minimalist-abstract',
    'neutral-tones'
];

foreach ($target_collections as $slug) {
    if (isset($data[$slug])) {
        regenerate_collection_page($slug, $data[$slug]);
    } else {
        echo "Skipping $slug - not found in JSON.\n";
    }
}
?>
