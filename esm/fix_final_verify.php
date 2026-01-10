<?php
// fix_final_verify.php
require_once($_SERVER['DOCUMENT_ROOT'] . '/wp-load.php');

$target_slug = 'pieces_of_redcollage';
$page = get_page_by_path($target_slug, OBJECT, 'page');

if ($page) {
    echo "<h1>Verification: {$page->post_title} (ID: {$page->ID})</h1>";

    // Force clean cache for this post
    clean_post_cache($page->ID);

    // Re-fetch raw
    $fresh = get_post($page->ID);
    $content = $fresh->post_content;

    echo "<h3>Current Content State:</h3>";

    // Check CSS
    if (strpos($content, '<style>/* Font Imports') !== false) {
        echo "✅ CSS is Wrapped in Style Tags.<br>";
    } else {
        echo "❌ CSS is NOT Wrapped (Raw text found?).<br>";
        echo "Snippet: " . htmlspecialchars(substr($content, 0, 100)) . "<br>";
    }

    // Check Link
    if (strpos($content, 'Pieces_of_Red_Collage_Sheet.pdf') !== false) {
        echo "✅ Spec Link is CORRECT (Pieces_of_Red_Collage_Sheet.pdf).<br>";
    } else {
        echo "❌ Spec Link is WRONG (Found: " . (strpos($content, 'Pieces-of-Red_Sheet.pdf') !== false ? "Pieces-of-Red_Sheet.pdf" : "Unknown") . ").<br>";
    }

    // Force Update if wrong (SQL method to bypass filters?)
    if (strpos($content, 'Pieces-of-Red_Sheet.pdf') !== false) {
        echo "⚠️ Attempting Direct SQL Update...<br>";
        global $wpdb;
        $sql = "UPDATE {$wpdb->posts} SET post_content = REPLACE(post_content, 'Pieces-of-Red_Sheet.pdf', 'Pieces_of_Red_Collage_Sheet.pdf') WHERE ID = {$page->ID}";
        $wpdb->query($sql);

        $sql2 = "UPDATE {$wpdb->posts} SET post_content = REPLACE(post_content, 'Pieces-of-Red_HighRes.zip', 'Pieces_of_Red_Collage_HighRes.zip') WHERE ID = {$page->ID}";
        $wpdb->query($sql2);

        echo "Executed SQL Link Fix.<br>";
    }

    // Force CSS Fix SQL
    if (strpos($content, '/* Font Imports */') === 0) {
        echo "⚠️ Attempting Direct SQL CSS Wrap...<br>";
        // Complex regex replace in SQL is hard.
        // We will use PHP and update via SQL

        // Logic: wrapped = <style> + content_prefix + </style> + suffix
        // We already successfully generated the string in fix_final_v2.php, so why did it fail?
        // Maybe it didn't fail. Maybe get_page_by_title returned a Draft revision?
        // We are using get_page_by_path('pieces_of_redcollage') which should return the publish version.
    }
} else {
    echo "❌ Slug not found.";
}
?>