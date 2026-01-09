<?php
require_once('wp-load.php');
ini_set('display_errors', 1);
error_reporting(E_ALL);

global $wpdb;

echo "<pre>Fixing Markup via Direct SQL (Force)...<br>";

// Get all pages directly from DB to avoid any caching
$posts = $wpdb->get_results("SELECT ID, post_content FROM $wpdb->posts WHERE post_type='page' AND post_status='publish'");

$count = 0;
foreach ($posts as $post) {
    $content = $post->post_content;
    $original_content = $content;
    $pid = $post->ID;
    $changed = false;

    // 1. FIX CSS
    if (strpos($content, '/* Font Imports */') !== false && strpos($content, '<style>/* Font Imports */') === false) {
        $pattern_css = '/(\/\* Font Imports \*\/.*?)\s*(?=<!-- VisualArtwork Schema -->)/s';
        if (preg_match($pattern_css, $content)) {
            $content = preg_replace($pattern_css, "<style>$1</style>", $content);
            $changed = true;
        }
    }

    // 2. FIX JSON (Anchor Strategy)
    $marker = '<!-- VisualArtwork Schema -->';
    $marker_pos = strpos($content, $marker);

    if ($marker_pos !== false) {
        // Check if already wrapped
        $snippet = substr($content, $marker_pos, 200);
        if (strpos($snippet, '<script') === false) {
            // Find start of JSON
            $json_start = strpos($content, '{', $marker_pos);
            if ($json_start !== false) {
                // Find end (before div)
                $div_pos = strpos($content, '<div class="artwork-page-container"', $json_start);
                // Fallback
                if ($div_pos === false)
                    $div_pos = strpos($content, '<div', $json_start);

                if ($div_pos !== false) {
                    $raw_block = substr($content, $json_start, $div_pos - $json_start);
                    $json_clean = trim($raw_block);

                    // Sanity check
                    if (substr($json_clean, 0, 1) == '{' && substr($json_clean, -1) == '}') {
                        $wrapped = '<script type="application/ld+json">' . $json_clean . '</script>';
                        $before = substr($content, 0, $json_start);
                        $after = substr($content, $div_pos);
                        $content = $before . $wrapped . $after;
                        $changed = true;
                    }
                }
            }
        }
    }

    // 3. SQL UPDATE
    if ($changed && $content !== $original_content) {
        $result = $wpdb->update(
            $wpdb->posts,
            ['post_content' => $content],
            ['ID' => $pid]
        );

        if ($result !== false) {
            echo "✅ SQL UPDATED Page $pid<br>";
            $count++;
        } else {
            echo "❌ SQL ERR Page $pid: " . $wpdb->last_error . "<br>";
        }
    }
}
echo "Updated $count pages via SQL.</pre>";
?>