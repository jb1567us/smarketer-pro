<?php
// inspect_and_fix_work_party.php
require_once($_SERVER['DOCUMENT_ROOT'] . '/wp-load.php');

echo "<h1>Debugging Work Party</h1>";

// 1. Find Page
$args = [
    'post_type' => 'page',
    's' => 'Mulch',
    'post_status' => 'publish'
];
$query = new WP_Query($args);

if ($query->have_posts()) {
    while ($query->have_posts()) {
        $query->the_post();
        echo "Found: " . get_the_title() . " (ID: " . get_the_ID() . ") Slug: " . $post->post_name . "<br>";

        if ($post->post_title == "Work Party Mulch Series Collage") {
            $id = get_the_ID();
            $content = $post->post_content;
            echo "<h3>Raw Content Dump (Start):</h3>";
            echo "<textarea style='width:100%;height:150px;'>" . htmlspecialchars(substr($content, 0, 500)) . "</textarea><br>";

            // Check for /* Font Imports */
            if (strpos($content, '/* Font Imports */') !== false) {
                echo "✅ Found '/* Font Imports */'<br>";
            } else {
                echo "❌ '/* Font Imports */' NOT found exactly.<br>";
                echo "Hex Dump: " . bin2hex(substr($content, 0, 50)) . "<br>";
            }

            // Check for Link
            if (strpos($content, 'spec_sheets') !== false) {
                echo "✅ Found 'spec_sheets'<br>";
            }

            // Attempt Fix Validation
            // CSS Wrap
            // We need to match the START of the file usually.

            // Fix Strategy:
            // If content starts with `@import` or `/*`, wrap it.
            // Look for end of CSS block?

            // Regex Replace Link for Button
            // <a href="...spec_sheets..." ...>

            $newContent = $content;

            // 1. Apply CSS Wrap
            if (strpos($newContent, '<style>/* Font Imports */') === false) {
                // Replace literal string
                $newContent = str_replace('/* Font Imports */', '<style>/* Font Imports */', $newContent);
                // Close style before first HTML element?

                if (preg_match('/(\n\s*<(div|p|h[1-6]))/i', $newContent, $m, PREG_OFFSET_CAPTURE)) {
                    $pos = $m[0][1];
                    $newContent = substr_replace($newContent, "</style>", $pos, 0);
                    echo "✅ Injected &lt;/style&gt; at pos $pos<br>";
                } else {
                    echo "⚠️ Could not find place to close style tag.<br>";
                }
            }

            // 2. Apply Button Class
            // Regex: (<a\s+[^>]*href="[^"]*spec_sheets[^"]*")([^>]*>)
            // Insert class="trade-button"
            $newContent = preg_replace('/(<a\s+[^>]*href="[^"]*(spec_sheets|high_res)[^"]*")([^>]*>)/i', '$1 class="trade-button"$3', $newContent);

            // 3. Inject Button CSS
            if (strpos($newContent, '.trade-button') === false) {
                $css = "<style>.trade-button { display: inline-block; padding: 12px 24px; background-color: #000; color: #fff !important; text-decoration: none; text-transform: uppercase; font-size: 11px; letter-spacing: 1px; margin-top: 10px; margin-right: 10px; border: 1px solid #000; transition: all 0.3s ease; font-family: 'Inter', sans-serif; font-weight: 500; } .trade-button:hover { background-color: #fff; color: #000 !important; }</style>";
                $newContent .= $css;
            }

            if ($newContent !== $content) {
                wp_update_post(['ID' => $id, 'post_content' => $newContent]);
                echo "<h2>✅ UPDATE APPLIED to Work Party</h2>";
            } else {
                echo "<h2>⚠️ No Changes Made (Regex Mismatch?)</h2>";
            }
        }
    }
} else {
    echo "No Mulch posts found.";
}
?>