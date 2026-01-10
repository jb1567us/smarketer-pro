<?php
// fix_final_force.php
require_once($_SERVER['DOCUMENT_ROOT'] . '/wp-load.php');

$target_slug = 'pieces_of_redcollage';
$page = get_page_by_path($target_slug, OBJECT, 'page');

if ($page) {
    echo "<h1>Forcing: {$page->post_title} (ID: {$page->ID})</h1>";

    // 1. Prepare Content Remotely (Robust Logic)
    $content = $page->post_content;
    $updated = false;

    // CSS FIX
    if (strpos($content, '/* Font Imports */') !== false && strpos($content, '<style>') === false) {
        $split = strpos($content, '<div');
        if ($split === false)
            $split = strpos($content, '<img');

        if ($split !== false) {
            $css = substr($content, 0, $split);
            $rest = substr($content, $split);
            $css = strip_tags($css);
            $content = "<style>\n$css\n</style>\n$rest";
            $updated = true;
            echo "✅ Prepared CSS Wrap.<br>";
        }
    }

    // LINK FIX
    if (strpos($content, 'Pieces-of-Red_Sheet.pdf') !== false) {
        $content = str_replace('Pieces-of-Red_Sheet.pdf', 'Pieces_of_Red_Collage_Sheet.pdf', $content);
        $updated = true;
        echo "✅ Prepared Link Fix.<br>";
    }
    if (strpos($content, 'Pieces-of-Red_HighRes.zip') !== false) {
        $content = str_replace('Pieces-of-Red_HighRes.zip', 'Pieces_of_Red_Collage_HighRes.zip', $content);
        $updated = true;
    }

    if ($updated) {
        // DIRECT SQL UPDATE
        global $wpdb;
        $safe_content = esc_sql($content);
        $sql = "UPDATE {$wpdb->posts} SET post_content = '$safe_content' WHERE ID = {$page->ID}";
        $result = $wpdb->query($sql);

        if ($result !== false) {
            echo "<h2>🚀 SQL Update Success. Rows: $result</h2>";
            clean_post_cache($page->ID);
        } else {
            echo "❌ SQL Update Failed: " . $wpdb->last_error;
        }
    } else {
        echo "ℹ️ No changes needed in content string.<br>";
        // Maybe it's already fixed in DB but CACHED?

        // Let's print the first 100 chars from DB to be sure.
        $db_check = $wpdb->get_var("SELECT post_content FROM {$wpdb->posts} WHERE ID = {$page->ID}");
        echo "DB Content Start: " . htmlspecialchars(substr($db_check, 0, 100));
    }

} else {
    echo "❌ Slug not found.";
}
?>