<?php
// check_id_robust.php
require_once($_SERVER['DOCUMENT_ROOT'] . '/wp-load.php');
$id = 213;

echo "<pre>";
echo "Checking ID $id\n";
try {
    $p = get_post($id);
    if ($p) {
        echo "ID Found.\n";
        echo "Title: " . $p->post_title . "\n";
        echo "Status: " . $p->post_status . "\n";
        echo "Content Size: " . strlen($p->post_content) . "\n";

        // Check Memory
        echo "Memory: " . memory_get_usage() . "\n";

        // Try simple filter
        // $c = apply_filters('the_content', $p->post_content);
        // echo "Filter Size: " . strlen($c) . "\n";
    } else {
        echo "Get Post returned invalid\n";
    }
} catch (Exception $e) {
    echo "Caught Exception: " . $e->getMessage() . "\n";
}
echo "Done.\n";
echo "</pre>";
?>