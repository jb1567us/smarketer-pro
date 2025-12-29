<?php
// verify_saatchi_links.php
header("Content-Type: text/plain");
require_once($_SERVER['DOCUMENT_ROOT'] . '/wp-load.php');

$target_titles = [
    "Right Way Limited Edition of 1",
    "Start Sign Limited Edition of 1",
    "No Public Shrooms Limited Edition of 1",
    "Mushroom Exclamation",
    "Excited Bird"
];

foreach ($target_titles as $title_search) {
    $page = get_page_by_title($title_search, OBJECT, 'page');
    if (!$page) {
         // Try exact match or like match query if get_page_by_title fails for some reason or if it's not exact
         global $wpdb;
         $pid = $wpdb->get_var($wpdb->prepare("SELECT ID FROM $wpdb->posts WHERE post_type='page' AND post_title LIKE %s LIMIT 1", '%' . $wpdb->esc_like($title_search) . '%'));
         if ($pid) $page = get_post($pid);
    }

    if (!$page) {
        echo "Page not found for: $title_search\n";
        continue;
    }

    $title = $page->post_title;
    $slug = sanitize_title($title);
    $slug_clean = str_replace(array('-painting', '-sculpture', '-collage', '-installation', '-print'), '', $slug);
    
    // Try multiple prefixes
    $prefixes = ['Painting-', 'Print-', 'Photography-', 'Sculpture-', 'Drawing-', 'Mixed-Media-', ''];
    $found = false;

    echo "Checking: '$title' (ID: {$page->ID})\n";

    foreach ($prefixes as $prefix) {
        $test_url = 'https://www.saatchiart.com/art/' . $prefix . ucfirst($slug_clean) . '/1295487/0000000/view'; // view might be needed or not, sticking to simple first
        // Simple URL:
        $test_url_simple = 'https://www.saatchiart.com/art/' . $prefix . ucfirst($slug_clean);

        $response = wp_remote_head($test_url_simple, ['redirection' => 5, 'timeout' => 5]);
        if (!is_wp_error($response) && wp_remote_retrieve_response_code($response) == 200) {
             echo "VALID URL FOUND: $test_url_simple\n";
             $found = true;
             break;
        }
    }

    if (!$found) {
        echo "FAILED: Could not find valid Saatchi URL for '$title'\n";
    }
    echo "--------------------------------------------------\n";
}
?>
