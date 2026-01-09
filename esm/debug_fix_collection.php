<?php
// debug_fix_collection.php
require_once($_SERVER['DOCUMENT_ROOT'] . '/wp-load.php');
ini_set('max_execution_time', 300);

$target_ids = [2218]; // Just Sculpture for now

echo "<h1>Debug Fix Collection</h1>";

foreach ($target_ids as $cid) {
    $collection = get_post($cid);
    if (!$collection)
        continue;

    echo "<h3>Processing: {$collection->post_title}</h3>";
    $content = $collection->post_content;

    // Regex
    if (preg_match_all('/<a\s+[^>]*href=["\']([^"\']*)["\'][^>]*>(.*?)<\/a>/i', $content, $matches)) {
        echo "Found " . count($matches[0]) . " links.<br><ul>";
        foreach ($matches[0] as $i => $fullTag) {
            $text = strip_tags($matches[2][$i]);
            $cleanText = trim($text);
            echo "<li><strong>Link:</strong> '$cleanText'";

            if (in_array($cleanText, ['Get in Touch', 'View our Trade Program'])) {
                echo " -> SKIPPED (Ignored List)</li>";
                continue;
            }

            // Search
            echo "<br>Searching for: '$cleanText'... ";
            $target = get_page_by_title($cleanText, OBJECT, 'page');

            if ($target) {
                echo "✅ FOUND ID {$target->ID} (/{$target->post_name}/)";
            } else {
                echo "❌ NOT FOUND";

                // Try Fuzzy
                global $wpdb;
                $like = '%' . $wpdb->esc_like($cleanText) . '%';
                $results = $wpdb->get_results($wpdb->prepare("SELECT ID, post_name FROM {$wpdb->posts} WHERE post_title LIKE %s AND post_type='page' AND post_status='publish' LIMIT 1", $like));
                if ($results) {
                    echo " -> Fuzzy Valid: /{$results[0]->post_name}/";
                }
            }
            echo "</li>";
        }
        echo "</ul>";
    } else {
        echo "Regex matched 0 links.<br>";
    }
}
?>