<?php
// fix_all_double_links.php
require_once($_SERVER['DOCUMENT_ROOT'] . '/wp-load.php');
ini_set('max_execution_time', 300);

echo "<h1>Fixing All Double Links</h1>";

$pages = get_posts([
    'post_type' => 'page',
    'numberposts' => -1,
    'post_status' => 'publish'
]);

$fixed = 0;

foreach ($pages as $p) {
    if (in_array($p->post_title, ['Home', 'About', 'Contact', 'Trade']))
        continue;

    $content = $p->post_content;
    $id = $p->ID;

    // Pattern: 
    // Find Zip Link
    // Find matching link after it that references page itself OR contains "High-Res" text

    if (strpos($content, 'HighRes.zip') !== false) {

        // Regex logic from the successful force script
        // Match <a ...>High-Res...</a> that appears AFTER the zip link?
        // Or just match ANY link with text "High-Res Images" (suspicious formatted)

        // The bad link looks often like: <a href="...">High-Res         Images</a>

        $pattern = '/(<br\s*\/?>\s*)*<a\s+[^>]*>.*?High-Res\s+Images.*?<\/a>/is';

        // We only want to remove it if it's NOT the zip link itself.
        // The Zip Link text is "Download High Res Images".
        // The Bad Link text is "High-Res         Images" or similar.

        // We can be safer: Find all links. Check text.

        if (preg_match_all('/<a\s+[^>]*>(.*?)<\/a>/is', $content, $matches)) {
            foreach ($matches[0] as $fullLink) {
                // Check text inside
                $linkText = strip_tags($fullLink);
                // If text is "High-Res Images" (bad) vs "Download High Res Images" (good)

                // Normalize spaces
                $cleanText = trim(preg_replace('/\s+/', ' ', $linkText));

                if ($cleanText === 'High-Res Images' || $cleanText === 'High-ResImages') {
                    // Verify href does NOT end in .zip
                    if (strpos($fullLink, '.zip') === false) {
                        // Removing Bad Link
                        $content = str_replace($fullLink, '', $content);
                        // Also remove preceding <br> if it exists?
                        // The regex replacement is better for context.
                    }
                }
            }
        }

        // Also run the aggressive Regex from before just in case
        $newContent = preg_replace('/(<br\s*\/?>\s*)*<a\s+[^>]*href=[^>]*' . $p->post_name . '[^>]*>.*?High-Res.*?<\/a>/is', '', $content);

        if ($newContent !== $p->post_content) {
            wp_update_post(['ID' => $id, 'post_content' => $newContent]);
            echo "✅ Fixed: {$p->post_title}<br>";
            $fixed++;
        }
    }
}

echo "Done. Fixed $fixed pages.";
?>