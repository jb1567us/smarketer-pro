<?php
// fix_posts_to_pages.php
require_once($_SERVER['DOCUMENT_ROOT'] . '/wp-load.php');
ini_set('max_execution_time', 300);
global $wpdb;

$target_ids = [2218, 2216, 2215]; // Sculpture, Blue, Gold

echo "<h1>Fixing Posts to Pages Links</h1>";

foreach ($target_ids as $cid) {
    // Get raw content
    $row = $wpdb->get_row("SELECT post_title, post_content FROM {$wpdb->posts} WHERE ID = $cid");
    if (!$row)
        continue;

    echo "<h3>Processing: {$row->post_title}</h3>";
    $content = $row->post_content;
    $modified = false;
    $count = 0;

    // Find all links
    if (preg_match_all('/<a\s+[^>]*href=["\']([^"\']*)["\'][^>]*>(.*?)<\/a>/is', $content, $matches)) {
        foreach ($matches[0] as $i => $fullTag) {
            $href = $matches[1][$i];
            $inner = $matches[2][$i];

            // Check if it looks like a Post Link (Date based or ID based)
            // e.g. /2025/09/25/... or ?page_id=...
            if (strpos($href, '/2025/') === false && strpos($href, '/2024/') === false && strpos($href, 'page_id') === false) {
                // Determine if it matches a known "Post" pattern?
                // Or acts as a catch-all for anything pointing to saatchi (if external)?
                // User said "directs to saatchi". This implies the POST redirects there, or the link IS directly to saatchi.
                // Inspection showed internal links mostly. The POST likely has a redirect plugin or JS.
                // We just want to fix the link here.
                continue;
            }

            // Determine Title to Search
            $titleToSearch = '';

            // 1. Text Content
            $text = trim(strip_tags($inner));
            if (!empty($text)) {
                $titleToSearch = $text;
            }
            // 2. Image Alt
            elseif (preg_match('/<img\s+[^>]*alt=["\']([^"\']*)["\']/i', $inner, $imgMatch)) {
                $titleToSearch = $imgMatch[1];
            }

            if (empty($titleToSearch))
                continue;

            echo "Found Post Link: '$titleToSearch' ($href)<br>";

            // Find the PAGE
            $target = get_page_by_title($titleToSearch, OBJECT, 'page');

            if (!$target) {
                // Fuzzy
                $like = '%' . $wpdb->esc_like($titleToSearch) . '%';
                $results = $wpdb->get_results($wpdb->prepare("SELECT ID, post_name FROM {$wpdb->posts} WHERE post_title LIKE %s AND post_type='page' AND post_status='publish' LIMIT 1", $like));
                if ($results)
                    $target = $results[0];
            }

            if ($target) {
                $newHref = '/' . $target->post_name . '/'; // Relative standardized

                // Replace HREF
                $newTag = preg_replace('/href=["\'][^"\']*["\']/', 'href="' . $newHref . '"', $fullTag);

                if ($newTag !== $fullTag) {
                    $content = str_replace($fullTag, $newTag, $content);
                    $modified = true;
                    $count++;
                    echo " -> Replaced with: $newHref<br>";
                }
            } else {
                echo " -> ⚠️ Page Not Found.<br>";
            }
        }
    }

    if ($modified) {
        $wpdb->update($wpdb->posts, ['post_content' => $content], ['ID' => $cid]);
        echo "✅ SAVED ($count updates)<br>";

        // Flush W3TC
        if (function_exists('w3tc_flush_all'))
            w3tc_flush_all();
        if (function_exists('wp_cache_flush'))
            wp_cache_flush();
    }
    echo "<hr>";
}
?>