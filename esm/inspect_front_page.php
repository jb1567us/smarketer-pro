<?php
// inspect_front_page.php
require_once('wp-load.php');

$front_page_id = get_option('page_on_front');
echo "Front Page ID: " . $front_page_id . "\n";

if ($front_page_id) {
    $page = get_post($front_page_id);
    echo "Title: " . $page->post_title . "\n";
    echo "Template: " . get_page_template_slug($front_page_id) . "\n";
    
    // Check content for "Waves"
    if (strpos($page->post_content, 'Painting-Waves') !== false) {
        echo "FOUND 'Painting-Waves' string in Front Page content!\n";
        echo "Sample context:\n";
        // Extract context
        preg_match('/.{50}Painting-Waves.{50}/s', $page->post_content, $m);
        print_r($m);
    } else {
        echo "String 'Painting-Waves' NOT found in Front Page content.\n";
    }
} else {
    echo "No static front page set (using index/posts).\n";
}
?>
