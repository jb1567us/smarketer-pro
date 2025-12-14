<?php
// fetch_tags.php
// Get the Tags for Post 213

require_once($_SERVER['DOCUMENT_ROOT'] . '/wp-load.php');

$id = 213;
$tags = wp_get_post_tags($id);

echo "<h1>🏷️ TAGS FOR ID $id</h1>";

if ($tags) {
    echo "<ul>";
    $tag_names = [];
    foreach ($tags as $t) {
        echo "<li>" . $t->name . " (ID: " . $t->term_id . ")</li>";
        $tag_names[] = $t->name;
    }
    echo "</ul>";

    // JSON for easy copy
    echo "<h3>JSON:</h3>";
    echo json_encode($tag_names);
} else {
    echo "❌ No Tags Found.";
}
?>