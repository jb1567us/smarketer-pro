<?php
// fix_blank_structure_final_sql.php
require_once($_SERVER['DOCUMENT_ROOT'] . '/wp-load.php');
global $wpdb;

echo "<h1>Final Structure Fix</h1>";

// Select all pages
$rows = $wpdb->get_results("SELECT ID, post_content FROM {$wpdb->posts} WHERE post_type='page' AND post_status='publish'");

foreach ($rows as $p) {
    $content = $p->post_content;
    $modified = false;

    // 1. Fix Double Class on Links
    // Pattern: <a ... class="First" ... class="Second" ...>
    // We want to remove the second class attribute and merge if needed, or just keep 'trade-button'.
    // The previous script injected `class="trade-button"` at start of attributes.
    // The existing class was likely `class="trade-link"`.

    // Regex: Matches `class="trade-button"` followed by anything, then `class="trade-link"`
    if (preg_match('/(<a\s+[^>]*?)class="trade-button"([^>]*?)class="trade-link"([^>]*>)/i', $content)) {
        // Replace with single class="trade-button trade-link"
        $content = preg_replace('/(<a\s+[^>]*?)class="trade-button"([^>]*?)class="trade-link"([^>]*>)/i', '$1class="trade-button trade-link"$2$3', $content);
        $modified = true;
    }

    // 2. Fix Raw CSS at End
    // Find unclosed .trade-button CSS at end
    // Checks if content contains `.trade-button` but NOT inside <style>
    // Just wrap the last occurrence?
    if (preg_match('/\.trade-button\s*\{[^}]+\}\s*$/', $content)) {
        // It's at the end. Wrap it.
        $content = preg_replace('/(\.trade-button\s*\{[^}]+\}\s*)$/', '<style>$1</style>', $content);
        $modified = true;
    }

    // 3. Fix Unclosed Header CSS
    if (strpos($content, '<style>/* Font Imports */') !== false) {
        // Check if proper closing exists before HTML body
        if (preg_match('/<style>\/\* Font Imports \*\/.*?<div/s', $content)) {
            // It's missing closing tag if it captures text up to <div
            // Insert </style> before <div
            // This is risky regex.
            // Better: explicitly replace `<style>/* Font Imports */` with itself? No.

            // Just find `<style>/* Font Imports */` and ensure `</style>` follows within 2000 chars?
            $start = strpos($content, '<style>/* Font Imports */');
            $chunk = substr($content, $start, 3000);
            if (strpos($chunk, '</style>') === false) {
                // Missing. Insert before first `<div` or `<p` or `<!--`
                if (preg_match('/(<div|<p|<!--)/', $chunk, $m, PREG_OFFSET_CAPTURE)) {
                    $pos = $start + $m[0][1];
                    $content = substr_replace($content, "</style>", $pos, 0);
                    $modified = true;
                }
            }
        }
    }

    if ($modified) {
        $wpdb->update($wpdb->posts, ['post_content' => $content], ['ID' => $p->ID]);
        echo "✅ Fixed ID {$p->ID}<br>";
    }
}
echo "Done.";
?>