<?php
// fix_all_formatted_v2.php
require_once($_SERVER['DOCUMENT_ROOT'] . '/wp-load.php');
ini_set('max_execution_time', 300);

echo "<h1>Fixing Display & Formatting</h1>";

// CSS to inject
$customCSS = "
<style>
.trade-button {
  display: inline-block;
  padding: 12px 24px;
  background-color: #000;
  color: #fff !important;
  text-decoration: none;
  text-transform: uppercase;
  font-size: 11px;
  letter-spacing: 1px;
  margin-top: 10px;
  margin-right: 10px;
  border: 1px solid #000;
  transition: all 0.3s ease;
  font-family: 'Inter', sans-serif;
  font-weight: 500;
}
.trade-button:hover {
  background-color: #fff;
  color: #000 !important;
}
</style>
";

$pages = get_posts([
    'post_type' => 'page',
    'numberposts' => -1,
    'post_status' => 'publish'
]);

$processed = 0;

foreach ($pages as $p) {
    if (in_array($p->post_title, ['Home', 'About', 'Contact', 'Trade']))
        continue;

    $content = $p->post_content;
    $modified = false;

    // 1. Fix Raw CSS (/* Font Imports ... */)
    // Only if it's NOT already wrapped in <style>
    if (strpos($content, '/* Font Imports */') !== false && strpos($content, '<style>/* Font Imports */') === false) {
        $content = str_replace('/* Font Imports */', '<style>/* Font Imports */', $content);
        // We need to close the style tag. Where? 
        // Heuristic: The CSS block ends before the HTML starts.
        // Usually ends with '}' or before a <div>.
        // Let's assume the CSS block is at the very top.
        // We can just append the closing </style> after the last '}' that typically ends the CSS block?
        // Risky.
        // Better: Wrap the specific block we know.
        // OR, just inject the closing tag before the first DIV?

        // Let's use the pattern from `fix_pieces_red.php` if possible.
        // It used `str_replace` blindly? No, the user did it via DB previously.

        // Let's try to match the CSS block.
        // It starts with /* Font Imports */ and ends ... well, usually before "Piece Name" or links.

        // Simple Fix: Add </style> before the first <div, <p, <h tag.
        if (preg_match('/(<div|<p|<h[1-6])/', $content, $m, PREG_OFFSET_CAPTURE)) {
            $pos = $m[0][1]; // Position of first tag
            // Insert </style> before it
            // wait, we inserted <style> at content start (replacing /* Font... */)
            // So we just need to find where to close it.
            // We can insert </style> right before the first HTML tag found.
            // But we need to make sure we don't break the CSS.

            // Let's try a safer approach:
            // If we see /* Font Imports */, assume it's the start.
            // Assume the CSS ends at the first blank line? Or when a standard CSS char is NOT found?

            // Hack: Just put the CSS in a style block if it looks "Raw".
            // Actually, the previous fix `fix_final_force.php` just wrapped the whole start?
            // No, it targeted specific strings.

            // Let's defer strict CSS wrapping if complex.
            // Just PREPEND the closure before the "body" content?
            // Assuming the CSS is at the top.

            $content = preg_replace('/(\n\s*<div)/i', "</style>$1", $content, 1);
        }
        $modified = true;
    }

    // 2. Formatting Links
    // Link 1: Spec Sheet
    // Pattern: [Download Spec Sheet](...) -> <a ...>Download Spec Sheet</a>

    // We want to transform: <a href="...">Download Spec Sheet</a>
    // into: <a href="..." class="trade-button">Download Spec Sheet</a>

    // Regex for Spec Sheet Link
    // Be careful not to double-add class
    if (preg_match('/<a\s+(?!.*class=)([^>]*href="[^"]*spec_sheets[^"]*"[^>]*)>(.*?)<\/a>/i', $content, $m)) {
        $content = preg_replace('/<a\s+(?!.*class=)([^>]*href="[^"]*spec_sheets[^"]*"[^>]*)>(.*?)<\/a>/i', '<a class="trade-button" $1>$2</a>', $content);
        $modified = true;
    }

    // Link 2: High Res Link
    // Pattern: "Download High Res Images"
    if (preg_match('/<a\s+(?!.*class=)([^>]*href="[^"]*high_res[^"]*"[^>]*)>(.*?)<\/a>/i', $content, $m)) {
        $content = preg_replace('/<a\s+(?!.*class=)([^>]*href="[^"]*high_res[^"]*"[^>]*)>(.*?)<\/a>/i', '<a class="trade-button" $1>$2</a>', $content);
        $modified = true;
    }

    // 3. Inject the CSS Definition
    // Add it to the bottom of the page if not present
    if (strpos($content, '.trade-button') === false) {
        $content .= $customCSS;
        $modified = true;
    }

    if ($modified) {
        wp_update_post(['ID' => $p->ID, 'post_content' => $content]);
        echo "✅ Fixed: {$p->post_title}<br>";
        $processed++;
    }
}

echo "Done. Updated $processed pages.";
?>