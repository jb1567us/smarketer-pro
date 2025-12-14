<?php
// fix_collection_links_content.php
require_once($_SERVER['DOCUMENT_ROOT'] . '/wp-load.php');
ini_set('max_execution_time', 300);

// Target Collections
// 2218: Sculpture
// 2216: Blue & Turquoise
// 2215: Gold
// Also maybe:
// 2220: Large Works? (User didn't mention, but let's check title "Oversized")
// Let's stick to the 3 known plus generic search.

$target_ids = [2218, 2216, 2215];

echo "<h1>Fixing Collection Links by Text</h1>";

foreach ($target_ids as $cid) {
    $collection = get_post($cid);
    if (!$collection)
        continue;

    echo "<h3>Processing: {$collection->post_title}</h3>";
    $content = $collection->post_content;
    $modified = false;

    // Parse links
    // We want to capture the whole tag to replace it safely.
    // Regex: <a ... >Text</a>

    if (preg_match_all('/<a\s+[^>]*href=["\']([^"\']*)["\'][^>]*>(.*?)<\/a>/i', $content, $matches)) {
        foreach ($matches[0] as $i => $fullTag) {
            $oldHref = $matches[1][$i];
            $text = strip_tags($matches[2][$i]);
            $cleanText = trim($text);

            // Skip non-artwork links (e.g. "Contact", "Trade Program")
            if (in_array($cleanText, ['Get in Touch', 'View our Trade Program', 'Gold Collection', 'Blue & Turquoise Collection', 'Oversized Statement Pieces', 'Pattern & Geometric', 'Minimalist Abstract', 'Neutral Tones', 'Sculpture Collection']))
                continue;

            // Search for Page by Title matches Text
            // Use get_page_by_title (exact) first
            $target = get_page_by_title($cleanText, OBJECT, 'page');

            if (!$target) {
                // Try sanitizing text?
                // "Floating 1 - Cicada Sculpture" -> might be "Floating 1 - Cicada" in title?
                // Try fuzzy lookup?
                global $wpdb;
                $like = '%' . $wpdb->esc_like($cleanText) . '%';
                $results = $wpdb->get_results($wpdb->prepare("SELECT ID, post_name FROM {$wpdb->posts} WHERE post_title LIKE %s AND post_type='page' AND post_status='publish' LIMIT 1", $like));
                if ($results) {
                    $target = $results[0];
                    echo " - Fuzzy Match: '$cleanText' -> /{$target->post_name}/<br>";
                }
            } else {
                echo " - Exact Match: '$cleanText' -> /{$target->post_name}/<br>";
            }

            if ($target) {
                $newHref = home_url($target->post_name) . '/'; // Force trailing slash standard

                // If HREF is different, update it
                // We should normalize both to compare
                // oldHref might be relative or absolute.

                // Just force update if found.
                // We need to rebuild the tag.
                // We reuse the existing tag attributes EXCEPT href?
                // Or just rebuild standard tag? 
                // Let's keep class/style but update href.

                // Regex Replace only the HREF in this specific tag string?
                // Easier: Use `str_replace` on the `$fullTag`.
                $newTag = preg_replace('/href=["\'][^"\']*["\']/', 'href="' . $newHref . '"', $fullTag);

                if ($newTag !== $fullTag) {
                    $content = str_replace($fullTag, $newTag, $content);
                    $modified = true;
                }
            } else {
                echo " ⚠️ No Target Found for: '$cleanText'<br>";
            }
        }
    }

    if ($modified) {
        wp_update_post(['ID' => $cid, 'post_content' => $content]);
        echo "✅ Updated Collection: {$collection->post_title}<br>";
    } else {
        echo "No changes needed.<br>";
    }
    echo "<hr>";
}
?>