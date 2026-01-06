<?php
// fix_final_v2.php
require_once($_SERVER['DOCUMENT_ROOT'] . '/wp-load.php');

// Lookup by SLUG (definitive for user URL)
$target_slug = 'pieces_of_redcollage';
$page = get_page_by_path($target_slug, OBJECT, 'page');

if ($page) {
    echo "<h1>Target: {$page->post_title} (ID: {$page->ID})</h1>";
    $content = $page->post_content;

    echo "<h3>Raw Content Start (First 500 chars):</h3>";
    echo "<textarea style='width:100%;height:150px;'>" . htmlspecialchars(substr($content, 0, 500)) . "</textarea><br>";

    $updated = false;

    // 1. CSS Match
    // Look for ANY usage of "Font Imports"
    if (strpos($content, 'Font Imports') !== false && strpos($content, '<style>') === false) {
        // We have raw CSS.
        // Try to split at <div OR at the first image?
        // Or just find the end of the CSS block "}" ?
        // Usually: ... }<div ...

        $split = strpos($content, '<div');
        if ($split === false)
            $split = strpos($content, '<img');
        if ($split === false)
            $split = strpos($content, '[/caption]'); // If shortcode?

        if ($split !== false) {
            $css = substr($content, 0, $split);
            $rest = substr($content, $split);
            $css = strip_tags($css); // Clean it
            $content = "<style>\n$css\n</style>\n$rest";
            $updated = true;
            echo "✅ CSS Wrapped (Split at pos $split).<br>";
        } else {
            echo "⚠️ Found CSS text but no split anchor found.<br>";
        }
    } else {
        echo "ℹ️ CSS OK (Tags present or text missing).<br>";
    }

    // 2. Link Match
    // Old File: Pieces-of-Red_Sheet.pdf
    // New File: Pieces_of_Red_Collage_Sheet.pdf

    if (strpos($content, 'Pieces-of-Red_Sheet.pdf') !== false) {
        $content = str_replace('Pieces-of-Red_Sheet.pdf', 'Pieces_of_Red_Collage_Sheet.pdf', $content);
        $updated = true;
        echo "✅ Spec Link Updated.<br>";
    } else {
        echo "ℹ️ Old Spec Filename not found.<br>";
    }

    // Old Zip: Pieces-of-Red_HighRes.zip
    // New Zip: Pieces_of_Red_Collage_HighRes.zip
    if (strpos($content, 'Pieces-of-Red_HighRes.zip') !== false) {
        $content = str_replace('Pieces-of-Red_HighRes.zip', 'Pieces_of_Red_Collage_HighRes.zip', $content);
        $updated = true;
        echo "✅ Zip Link Updated.<br>";
    } else {
        echo "ℹ️ Old Zip Filename not found.<br>";
    }

    if ($updated) {
        wp_update_post(['ID' => $page->ID, 'post_content' => $content]);
        echo "<h2>💾 Saved Changes!</h2>";

        if (function_exists('w3tc_flush_all'))
            w3tc_flush_all();
        echo "Cache Flushed.";
    } else {
        echo "<h2>No Changes Needed.</h2>";
    }

} else {
    echo "❌ Page slug '$target_slug' not found.";
}
?>