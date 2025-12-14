<?php
// fix_double_links_final_v2.php
require_once($_SERVER['DOCUMENT_ROOT'] . '/wp-load.php');
ini_set('max_execution_time', 300);

echo "<h1>Fixing Double Links (Targeted HREF)</h1>";

$pages = get_posts([
    'post_type' => 'page',
    'numberposts' => -1,
    'post_status' => 'publish'
]);

$fixed = 0;

foreach ($pages as $p) {
    if (in_array($p->post_title, ['Home', 'About', 'Contact', 'Trade'])) continue;

    $content = $p->post_content;
    $permalink = get_permalink($p->ID);
    
    // We are looking for a link that points to THIS page's permalink.
    // e.g. <a href="https://elliotspencermorgan.com/pieces_of_redcollage/">...</a>
    
    // Normalize permalink (remove trailing slash for comparison?)
    $link_url = rtrim($permalink, '/');
    
    // Regex: <a href="$link_url/?">...</a>
    // We want to remove it IF it contains "High-Res"
    
    // Construct regex safely
    $quoted_url = preg_quote($link_url, '/');
    $pattern = '/<a\s+[^>]*href=["\']' . $quoted_url . '\/?["\'][^>]*>.*?High-Res.*?<\/a>/is';
    
    if (preg_match($pattern, $content)) {
        $newContent = preg_replace($pattern, '', $content);
        
        // Remove left-over breaks
        // $newContent = preg_replace('/<br\s*\/?>\s*$/i', '', trim($newContent));
        
        if ($newContent !== $content) {
            wp_update_post(['ID' => $p->ID, 'post_content' => $newContent]);
            echo "✅ Fixed (Self-Link Removal): {$p->post_title}<br>";
            $fixed++;
        }
    }
}

echo "Done. Fixed $fixed pages.";
?>
