<?php
// verify_full_images.php
header("Content-Type: text/plain");
require_once($_SERVER['DOCUMENT_ROOT'] . '/wp-load.php');

$problem_ids = [2153, 2152, 2150, 2107, 2106];

echo "Verifying Full Size Images...\n\n";

foreach ($problem_ids as $page_id) {
    $thumb_id = get_post_thumbnail_id($page_id);
    if (!$thumb_id) {
        echo "ID $page_id: No thumbnail ID set.\n";
        continue;
    }
    
    $full_src = wp_get_attachment_image_src($thumb_id, 'full');
    if (!$full_src) {
        echo "ID $page_id: Could not get attachment src.\n";
        continue;
    }
    
    $url = $full_src[0];
    echo "Checking URL: $url\n";
    
    $response = wp_remote_head($url, ['timeout' => 5]);
    if (is_wp_error($response)) {
        echo "  -> Error: " . $response->get_error_message() . "\n";
    } else {
        $code = wp_remote_retrieve_response_code($response);
        echo "  -> Status: $code\n";
    }
    echo "--------------------------------------------------\n";
}
?>
