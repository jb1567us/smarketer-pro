<?php
// fix_collection_links_final.php
require_once($_SERVER['DOCUMENT_ROOT'] . '/wp-load.php');
ini_set('max_execution_time', 300);

$target_ids = [2218, 2216, 2215];

echo "<h1>Final Link Fix Execution</h1>";

foreach ($target_ids as $cid) {
    $collection = get_post($cid);
    if (!$collection)
        continue;

    echo "<h3>Updating: {$collection->post_title}</h3>";
    $content = $collection->post_content;
    $modified = false;
    $count = 0;

    if (preg_match_all('/<a\s+[^>]*href=["\']([^"\']*)["\'][^>]*>(.*?)<\/a>/i', $content, $matches)) {
        foreach ($matches[0] as $i => $fullTag) {
            $text = strip_tags($matches[2][$i]);
            $cleanText = trim($text);

            // Ignore list
            if (in_array($cleanText, ['Get in Touch', 'View our Trade Program']))
                continue;

            // Search
            $target = get_page_by_title($cleanText, OBJECT, 'page');
            if (!$target) {
                // Fuzzy
                global $wpdb;
                $like = '%' . $wpdb->esc_like($cleanText) . '%';
                $results = $wpdb->get_results($wpdb->prepare("SELECT ID, post_name FROM {$wpdb->posts} WHERE post_title LIKE %s AND post_type='page' AND post_status='publish' LIMIT 1", $like));
                if ($results)
                    $target = $results[0];
            }

            if ($target) {
                $newHref = '/' . $target->post_name . '/'; // Relative URL standardized

                // Replace HREF in tag
                $newTag = preg_replace('/href=["\'][^"\']*["\']/', 'href="' . $newHref . '"', $fullTag);

                if ($newTag !== $fullTag) {
                    $content = str_replace($fullTag, $newTag, $content);
                    $modified = true;
                    $count++;
                }
            }
        }
    }

    if ($modified) {
        wp_update_post(['ID' => $cid, 'post_content' => $content]);
        echo "✅ Updated $count links in {$collection->post_title}<br>";
    } else {
        echo "No changes needed.<br>";
    }
}
?>