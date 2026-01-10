<?php
require_once('wp-load.php');
ini_set('display_errors', 1);
error_reporting(E_ALL);

echo "<pre>Fixing Markup V2 (JSON Only)...<br>";

// Get all pages again
$args = ['post_type' => 'page', 'posts_per_page' => -1, 'post_status' => 'publish'];
$query = new WP_Query($args);

$count = 0;
foreach ($query->posts as $post) {
    $content = $post->post_content;
    $original_content = $content;
    $pid = $post->ID;

    // Check if JSON exists but script tag is missing
    if (strpos($content, '{ "@context"') !== false && strpos($content, '<script type="application/ld+json">{ "@context"') === false) {

        // Robust manual extraction using strpos
        $schema_start_marker = '{ "@context"';
        $div_start_marker = '<div class="artwork-page-container"';

        $start_pos = strpos($content, $schema_start_marker);
        if ($start_pos !== false) {
            $end_pos = strpos($content, $div_start_marker, $start_pos);
            if ($end_pos !== false) {
                // Extract the JSON block
                $length = $end_pos - $start_pos;
                $json_block = substr($content, $start_pos, $length);

                // Trim whitespace from end of JSON block just in case
                $json_clean = trim($json_block);

                // Wrap it
                $wrapped = '<script type="application/ld+json">' . $json_clean . '</script>';

                // Reassemble
                // Be careful not to lose whitespace before the div if needed (usually block level)
                $before = substr($content, 0, $start_pos);
                $after = substr($content, $end_pos);

                $content = $before . $wrapped . $after;
                echo "✅ MATCHED via strpos for Page $pid. Wrapped JSON.<br>";
            } else {
                echo "⚠️ Start found but End marker not found for Page $pid<br>";
                // Search for just "<div" ?
                $end_pos_loose = strpos($content, '<div', $start_pos);
                if ($end_pos_loose !== false) {
                    $length = $end_pos_loose - $start_pos;
                    $json_block = substr($content, $start_pos, $length);
                    $wrapped = '<script type="application/ld+json">' . trim($json_block) . '</script>';
                    $content = substr($content, 0, $start_pos) . $wrapped . substr($content, $end_pos_loose);
                    echo "✅ Loose Match via strpos for Page $pid<br>";
                }
            }
        }
    }

    if ($content !== $original_content) {
        wp_update_post(['ID' => $pid, 'post_content' => $content]);
        echo "✅ Fixed JSON for Page $pid<br>";
        $count++;
    }
}
echo "Updated $count pages.</pre>";
?>