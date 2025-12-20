<?php
// load WP environment
require_once($_SERVER['DOCUMENT_ROOT'] . '/wp-load.php');

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

    // 2. Build HTML
    $artwork_cards_html = '';

    foreach ($artworks as $aw) {
        $title = htmlspecialchars($aw['title']);
        $image = !empty($aw['image_url']) ? $aw['image_url'] : '';
        // Fix relative URLs if needed, but usually full URLs in JSON
        
        $link = !empty($aw['link']) ? $aw['link'] : '#';

        // Dimensions
        $dims = '';
        if (isset($aw['dimensions'])) {
            $dims = htmlspecialchars($aw['dimensions']);
        } elseif (isset($aw['width'], $aw['height'])) {
            $dims = $aw['width'] . ' W x ' . $aw['height'] . ' H x ' . (isset($aw['depth']) ? $aw['depth'] : '0.1') . ' D in';
        }

        // Medium
        $medium = isset($aw['mediumsDetailed']) ? htmlspecialchars($aw['mediumsDetailed']) : (isset($aw['medium']) ? htmlspecialchars($aw['medium']) : '');

        // Description - truncate if too long? No, user wants full text likely.
        $description = isset($aw['description']) ? $aw['description'] : '';
        // Convert newlines to breaks
        $description = nl2br(htmlspecialchars($description));

        // Card HTML
        $card = '
        <div class="artwork-card" style="text-align: center; margin-bottom: 50px;">
            <a href="' . $link . '" style="display: block; width: 100%;">
                <img src="' . $image . '" alt="' . $title . '" class="no-lazy skip-lazy" data-no-lazy="1" style="width: 100%; aspect-ratio: 3/4; object-fit: cover; margin-bottom: 10px;">
            </a>
            <h3 style="font-size: 18px; margin: 15px 0 5px 0;"><a href="' . $link . '" style="text-decoration: none; color: #000;">' . $title . '</a></h3>
            <p class="details" style="font-size: 14px; color: #666; margin-bottom: 10px;">' . $dims . ' | ' . $medium . '</p>
        </div>';
        
        $artwork_cards_html .= $card;
    }

    // 3. Build Related Links (Generic)
    // We can just hardcode the list of ALL collections here for navigation
    // Or reuse the existing "Explore More" list pattern
    $all_collections = [
        'blue-turquoise-collection' => 'Blue & Turquoise Collection',
        'oversized-statement-pieces' => 'Oversized Statement Pieces',
        'sculpture-collection' => 'Sculpture Collection',
        'pattern-geometric' => 'Pattern & Geometric',
        'minimalist-abstract' => 'Minimalist Abstract',
        'neutral-tones' => 'Neutral Tones',
        'gold-collection' => 'Gold Collection'
    ];

    $related_links_html = '';
    foreach ($all_collections as $k => $t) {
        if ($k === $slug) continue; // Skip self
        $related_links_html .= '<li><a href="/' . $k . '/">' . $t . '</a></li>';
    }

    // 4. Final HTML Structure (The "Gold Standard" Template)
    $final_html = '
<div class="collection-page" style="margin-bottom: 60px;">
    <div class="collection-header" style="text-align: center; max-width: 800px; margin: 0 auto 50px auto;">
        <h1 style="font-family: \'Playfair Display\', serif; font-size: 3rem; margin-bottom: 20px;">' . $collection['title'] . '</h1>
        <p class="collection-intro" style="font-size: 1.1rem; line-height: 1.6; color: #555;">' . (isset($collection['description']) ? $collection['description'] : '') . '</p>
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
