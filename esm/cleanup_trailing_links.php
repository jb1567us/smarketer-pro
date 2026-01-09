<?php
// cleanup_trailing_links.php
require_once($_SERVER['DOCUMENT_ROOT'] . '/wp-load.php');
ini_set('max_execution_time', 300);

echo "<h1>Cleaning Duplicate Links</h1>";

$pages = get_posts([
    'post_type' => 'page',
    'numberposts' => -1,
    'post_status' => 'publish'
]);

$fixed = 0;

foreach ($pages as $p) {
    $content = $p->post_content;

    // Pattern: 
    // <a href=".../high_res/...">Download High Res Images</a> [Link to self with text "High-Res Images"]
    // OR just <a href="...page-slug/">High-Res Images</a>

    // Regex for the broken link:
    // <a href="[^"]+">High-Res\s+Images<\/a>
    // Note: User screenshot shows "High-Res Images" as the text of the second link.

    $pattern = '/<a\s+[^>]*href="[^"]*"[^>]*>\s*High-Res\s+Images\s*<\/a>/i';

    // We only want to remove it IF it follows a valid "Download High Res Images" link? 
    // Or just remove it entirely if it points to self/invalid?
    // Let's be safe: If we see the VALID link, we remove the INVALID one.

    if (strpos($content, 'HighRes.zip') !== false) {
        // Valid link exists. Safe to remove the phantom one.
        if (preg_match($pattern, $content)) {
            $newContent = preg_replace($pattern, '', $content);
            if ($newContent !== $content) {
                // Also remove trailing <br>s if any?
                wp_update_post(['ID' => $p->ID, 'post_content' => $newContent]);
                echo "✅ Fixed: {$p->post_title}<br>";
                $fixed++;
            }
        }
    }
}

echo "Done. Fixed $fixed pages.";
?>