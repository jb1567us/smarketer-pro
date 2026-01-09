<?php
// hide_artworks_remote.php
// Hides specific artworks by setting them to 'draft'

require_once('wp-load.php');

$ids_to_hide = [1704, 2070, 1912, 1913];
$results = [];

foreach ($ids_to_hide as $id) {
    $post = get_post($id);
    if ($post) {
        $updated = wp_update_post([
            'ID' => $id,
            'post_status' => 'draft'
        ]);

        if ($updated) {
            $results[$id] = "Success: Set to draft.";
        } else {
            $results[$id] = "Error: Failed to update.";
        }
    } else {
        $results[$id] = "Error: Post not found.";
    }
}

header('Content-Type: application/json');
echo json_encode($results);
?>
