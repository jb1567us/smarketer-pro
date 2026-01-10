<?php
// verify_saatchi_links_v2.php
header("Content-Type: text/plain");
header("Cache-Control: no-store, no-cache, must-revalidate, max-age=0");
require_once($_SERVER['DOCUMENT_ROOT'] . '/wp-load.php');

$target_titles = [
    "Right Way", // "Right Way Limited Edition of 1" might be the full title, check partial
    "Start Sign",
    "No Public Shrooms",
    "Mushroom Exclamation",
    "Excited Bird"
];

echo "Verifying Saatchi Links for Target Titles (v2)...\n\n";

global $wpdb;

foreach ($target_titles as $base_title) {
    echo "SEARCHING FOR: '$base_title'\n";
    
    // Find the page
    $query = $wpdb->prepare("SELECT ID, post_title FROM $wpdb->posts WHERE post_type='page' AND post_title LIKE %s LIMIT 1", '%' . $wpdb->esc_like($base_title) . '%');
    $page = $wpdb->get_row($query);

    if (!$page) {
        echo "  -> Page NOT FOUND.\n";
        continue;
    }
    
    echo "  -> Found Page ID: $page->ID | Title: $page->post_title\n";
    
    // Generate clean slug
    $slug = sanitize_title($page->post_title);
    $slug_clean = str_replace(array('-painting', '-sculpture', '-collage', '-installation', '-print', '-limited-edition-of-1'), '', $slug);
    // Note: 'limited-edition-of-1' might need to be stripped for the Saatchi URL if Saatchi just uses the base name. 
    // Or maybe Saatchi includes it. We will test both.
    
    $slugs_to_test = [$slug_clean];
    if (strpos($slug, 'limited-edition') !== false) {
        $slugs_to_test[] = str_replace('-limited-edition-of-1', '', $slug); // try removing just that suffix
        $slugs_to_test[] = $slug; // try full slug
    }
    
    $prefixes = ['Painting-', 'Print-', 'Photography-', 'Sculpture-', ''];
    $valid_url = false;

    foreach ($slugs_to_test as $test_slug) {
        if ($valid_url) break;
        foreach ($prefixes as $prefix) {
            $url = 'https://www.saatchiart.com/art/' . $prefix . ucfirst($test_slug);
            // Quick check
            $response = wp_remote_head($url, ['redirection' => 5, 'timeout' => 5]);
            if (!is_wp_error($response)) {
                $code = wp_remote_retrieve_response_code($response);
                if ($code == 200) {
                    echo "  -> VALID URL: $url\n";
                    $valid_url = true;
                    break;
                }
            }
        }
    }

    if (!$valid_url) {
        echo "  -> FAILED: No valid Saatchi URL found.\n";
    }
    echo "--------------------------------------------------\n";
}
?>
