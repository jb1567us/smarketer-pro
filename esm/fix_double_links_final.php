<?php
// fix_double_links_final.php
require_once($_SERVER['DOCUMENT_ROOT'] . '/wp-load.php');
ini_set('max_execution_time', 300);

echo "<h1>Fixing Double Links (Final)</h1>";

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
    $original_len = strlen($content);

    // Pattern 1: Self-link with text "High-Res Images"
    // e.g. <a href="https://elliotspencermorgan.com/pieces_of_redcollage/">High-Res         Images</a>
    // Note: User content has lots of spaces in the anchor text based on previous output.

    $pattern = '/<a\s+[^>]*href="[^"]*"[^>]*>\s*High-Res\s+Images\s*<\/a>/i';

    // Only remove if we HAVE the valid zip link
    if (strpos($content, 'HighRes.zip') !== false) {
        $newContent = preg_replace($pattern, '', $content);

        // Also remove any breaks left behind? <br><br> -> <br>
        // $newContent = str_replace('<br><br>', '<br>', $newContent); 

        if (strlen($newContent) !== $original_len) {
            wp_update_post(['ID' => $p->ID, 'post_content' => $newContent]);
            echo "✅ Fixed: {$p->post_title}<br>";
            $fixed++;
        }
    }
}

echo "Done. Fixed $fixed pages.";
?>