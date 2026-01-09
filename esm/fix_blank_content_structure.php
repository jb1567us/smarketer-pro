<?php
// fix_blank_content_structure.php
require_once($_SERVER['DOCUMENT_ROOT'] . '/wp-load.php');
ini_set('max_execution_time', 300);
global $wpdb;

echo "<h1>Fixing Broken HTML/CSS Structure</h1>";

// Target all pages or just the corrupted ones?
// Let's target ALL pages that contain the broken pattern.
// Pattern: CSS at end of file without <style> tags OR double class attributes.

$rows = $wpdb->get_results("SELECT ID, post_title, post_content FROM {$wpdb->posts} WHERE post_type='page' AND post_status='publish'");

$count = 0;
foreach ($rows as $p) {
    if (in_array($p->post_title, ['Home', 'About', 'Contact']))
        continue;

    $content = $p->post_content;
    $modified = false;
    $log = "";

    // 1. Fix Double Class Attribute
    // e.g. class="trade-button" ... class="trade-link"
    // We want to merge them or remove the second.
    // Regex: class="([^"]*)"([^>]*)class="([^"]*)"
    // This is tricky. simpler to direct replace specific known corruption.
    // The previous script added `class="trade-button"` to the beginning of the tag attributes.
    // If `class="trade-link"` was already there later.

    // Pattern A: class="trade-button" ... class="
    if (preg_match('/class="trade-button"\s+([^>]*)\s+class="([^"]*)"/i', $content)) {
        // Merge classes: class="trade-button $2" $1
        $content = preg_replace('/class="trade-button"\s+([^>]*)\s+class="([^"]*)"/i', 'class="trade-button $2" $1', $content);
        $modified = true;
        $log .= "[Merged Double Class] ";
    }
    // Check reverse?
    if (preg_match('/class="([^"]*)"\s+([^>]*)\s+class="trade-button"/i', $content)) {
        $content = preg_replace('/class="([^"]*)"\s+([^>]*)\s+class="trade-button"/i', 'class="$1 trade-button" $2', $content);
        $modified = true;
        $log .= "[Merged Double Class Rev] ";
    }

    // 2. Fix Raw CSS at end of file
    // The previous script appended `.trade-button { ... }` w/o check? 
    // Wait, the previous script `fix_all_formatted_sql_final.php` DID wrap it in <style>...
    // But verify: 
    // $css = "<style>.trade-button {...}</style>";
    // IF the inspection shows it raw, maybe the <style> tags were stripped? or I am misreading.
    // Inspection: `.trade-button { ... }` appeared at end.
    // Let's check for `.trade-button {` appearing OUTSIDE of a style tag? Hard to regex.
    // Simpler: Check if content ENDS with `}` and contains `.trade-button {`.
    // If the last chars are `}` and NOT `</style>`, wrap it.

    $tail = substr(trim($content), -1000);
    if (strpos($tail, '.trade-button {') !== false && substr(trim($content), -8) !== '</style>') {
        // It seems the style tag is missing.
        // Identify the start of the raw CSS
        $pos = strrpos($content, '.trade-button {');
        if ($pos !== false) {
            // Check if <style> is immediately before it?
            if (substr($content, $pos - 7, 7) !== '<style>') {
                // Insert <style> before and </style> at end
                $cssBlock = substr($content, $pos);
                $newCss = "<style>" . $cssBlock . "</style>";
                $content = substr($content, 0, $pos) . $newCss;
                $modified = true;
                $log .= "[Wrapped Tail CSS] ";
            }
        }
    }

    // 3. Fix Raw CSS at START (/* Font Imports */)
    // Inspection showed: <style>/* Font Imports */ ... but maybe unclosed?
    // "Found unclosed style tag!" warning in inspection.
    // We need to Find `<style>/* Font Imports */` and ensure there is a `</style>` before the first HTML tag.

    if (strpos($content, '<style>/* Font Imports */') !== false) {
        // Check closure
        // If content has <style> but NO </style> until the very end?
        // Or if the </style> is missing entirely.

        // Find position of start
        $startPos = strpos($content, '<style>/* Font Imports */');
        // Find next </style>
        $endPos = strpos($content, '</style>', $startPos);

        if ($endPos === false) {
            // Missing closure!
            // Close it before first <div> or HTML tag?
            if (preg_match('/(<div|<p|<h)/i', $content, $m, PREG_OFFSET_CAPTURE, $startPos + 25)) {
                $insertPos = $m[0][1];
                $content = substr_replace($content, "</style>", $insertPos, 0);
                $modified = true;
                $log .= "[Closed Header CSS] ";
            }
        }
    }

    if ($modified) {
        $wpdb->update($wpdb->posts, ['post_content' => $content], ['ID' => $p->ID]);
        echo "✅ Fixed ID {$p->ID}: $log<br>";
        $count++;
    }
}
echo "Done. Fixed $count pages.";
?>