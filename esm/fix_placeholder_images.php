<?php
// fix_placeholder_images.php
header("Content-Type: text/plain");
require_once($_SERVER['DOCUMENT_ROOT'] . '/wp-load.php');

echo "Starting Image Restoration & Fixes...\n\n";

// 1. Hide "In the Dark Painting" (ID 2256)
$hide_id = 2256;
echo "Updating Status for 'In the Dark' (ID $hide_id)...\n";
$hide_post = array(
    'ID' => $hide_id,
    'post_status' => 'draft'
);
$res = wp_update_post($hide_post);
if ($res == 0 || is_wp_error($res)) {
    echo "  -> Error: Could not update post $hide_id.\n";
} else {
    echo "  -> Success: Post $hide_id set to 'draft'.\n";
}
echo "--------------------------------------------------\n";

// 2. Restore Images for Placeholders
$updates = [
    2153 => 1543, // Right Way
    2152 => 1556, // Start Sign
    2150 => 1522, // No Public Shrooms
    2107 => 1518, // Mushroom Exclamation
    2106 => 1474  // Excited Bird
];

foreach ($updates as $page_id => $attach_id) {
    echo "Restoring Image for Page ID $page_id (Image ID $attach_id)...\n";
    
    // Check if attachment exists
    if (!get_post($attach_id)) {
        echo "  -> Error: Attachment $attach_id does not exist.\n";
        continue;
    }
    
    // Set Thumbnail
    $result = set_post_thumbnail($page_id, $attach_id);
    
    if ($result) {
        $title = get_the_title($page_id);
        echo "  -> Success: Image restored for '$title'.\n";
    } else {
        echo "  -> Failed: Could not set thumbnail.\n";
    }
    echo "--------------------------------------------------\n";
}

echo "\nDone.\n";
?>
