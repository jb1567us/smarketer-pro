<?php
require_once('wp-load.php');
ini_set('display_errors', 1);
error_reporting(E_ALL);

echo "<pre>Fixing Markup V3 (Anchor Strategy)...<br>";

// Get all pages
$args = ['post_type' => 'page', 'posts_per_page' => -1, 'post_status' => 'publish'];
$query = new WP_Query($args);

$count = 0;
foreach ($query->posts as $post) {
    $content = $post->post_content;
    $original_content = $content;
    $pid = $post->ID;

    // Debug specific page
    if ($pid == 1927) {
        // echo "DEBUG Page 1927 content length: " . strlen($content) . "<br>";
    }

    // Check if JSON exists but script tag is missing
    // We look for the COMMENT marker which is reliable
    $marker = '<!-- VisualArtwork Schema -->';
    $marker_pos = strpos($content, $marker);

    if ($marker_pos !== false) {
        // Check if already wrapped?
        // Look ahead for <script>
        $snippet = substr($content, $marker_pos, 50);
        if (strpos($snippet, '<script') !== false) {
            // Already wrapped?
            continue;
        }

        // Find start of JSON (first { after marker)
        $json_start = strpos($content, '{', $marker_pos);
        if ($json_start === false)
            continue;

        // Find end of JSON (look for <div which starts the next section)
        $div_pos = strpos($content, '<div class="artwork-page-container"', $json_start);
        if ($div_pos === false) {
            // Try generic div
            $div_pos = strpos($content, '<div', $json_start);
        }

        if ($div_pos !== false) {
            // Verify there is a closing brace before the div
            // We take everything from $json_start to $div_pos
            $raw_block = substr($content, $json_start, $div_pos - $json_start);
            // Trim it
            $json_clean = trim($raw_block);

            // Only wrap if it looks like JSON
            if (substr($json_clean, 0, 1) == '{' && substr($json_clean, -1) == '}') {
                $wrapped = '<script type="application/ld+json">' . $json_clean . '</script>';
                // Replace the raw block in the content
                // Be careful with exact position
                $before = substr($content, 0, $json_start);
                $after = substr($content, $div_pos);

                $content = $before . $wrapped . $after;
                // echo "✅ Wrapped JSON for Page $pid<br>";

                if ($content !== $original_content) {
                    wp_update_post(['ID' => $pid, 'post_content' => $content]);
                    echo "✅ FIX APPLIED Page $pid<br>";
                    $count++;
                }
            } else {
                if ($pid == 1927)
                    echo "⚠️ Page 1927 JSON block malformed: " . htmlspecialchars($json_clean) . "<br>";
            }
        }
    }
}
echo "Updated $count pages.</pre>";
?>