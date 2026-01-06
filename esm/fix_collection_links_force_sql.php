<?php
// fix_collection_links_force_sql.php
require_once($_SERVER['DOCUMENT_ROOT'] . '/wp-load.php');
ini_set('max_execution_time', 300);
global $wpdb;

$target_ids = [2218, 2216, 2215];

echo "<h1>Force SQL Link Fix</h1>";

foreach ($target_ids as $cid) {
    // Get Raw Content from DB to avoid WP filtering
    $row = $wpdb->get_row("SELECT post_title, post_content FROM {$wpdb->posts} WHERE ID = $cid");
    if (!$row)
        continue;

    echo "<h3>Updating: {$row->post_title}</h3>";
    $content = $row->post_content;
    $modified = false;
    $count = 0;

    // We need to match EXACT strings for replacement
    // Use preg_match_all with OFFSET capture? No, simpler string checking.

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
                $like = '%' . $wpdb->esc_like($cleanText) . '%';
                $results = $wpdb->get_results($wpdb->prepare("SELECT ID, post_name FROM {$wpdb->posts} WHERE post_title LIKE %s AND post_type='page' AND post_status='publish' LIMIT 1", $like));
                if ($results)
                    $target = $results[0];
            }

            if ($target) {
                // Build new HREF
                $newHref = '/' . $target->post_name . '/';

                // Replace HREF in tag
                $newTag = preg_replace('/href=["\'][^"\']*["\']/', 'href="' . $newHref . '"', $fullTag);

                // Replace in Content if different
                // $fullTag comes from preg_match on $content, so it should match exactly unless duplicate tags exist.
                // If duplicate tags exist, we replace ALL occurrences. Which is fine if they point to the same text.
                // BUT what if text matches but href differs? (Unlikely for same text).

                if ($newTag !== $fullTag) {
                    // Check if replacement actually happens
                    $before = strlen($content);
                    $content = str_replace($fullTag, $newTag, $content);

                    if (strlen($content) !== $before || strpos($content, $newHref) !== false) {
                        $modified = true;
                        $count++;
                        echo " - Fixed: '$cleanText' -> $newHref<br>";
                    }
                }
            } else {
                echo " - ⚠️ No Target: '$cleanText'<br>";
            }
        }
    }

    if ($modified) {
        $wpdb->update($wpdb->posts, ['post_content' => $content], ['ID' => $cid]);
        echo "✅ SAVED DB: $count links updated.<br>";

        // Flush Cache
        if (function_exists('w3tc_flush_all'))
            w3tc_flush_all();
        if (function_exists('wp_cache_flush'))
            wp_cache_flush();

    } else {
        echo "No changes needed.<br>";
    }
    echo "<hr>";
}
?>