<?php
// fix_all_force_sql.php
require_once($_SERVER['DOCUMENT_ROOT'] . '/wp-load.php');

global $wpdb;

$targets = [
    'pieces_of_redcollage' => [
        'css' => true,
        'bad_spec' => 'Pieces-of-Red_Sheet.pdf',
        'good_spec' => 'Pieces_of_Red_Collage_Sheet.pdf',
        'bad_zip' => 'Pieces-of-Red_HighRes.zip',
        'good_zip' => 'Pieces_of_Red_Collage_HighRes.zip'
    ],
    'city-at-night-mulch-series-collage' => [ // Check slug? Or title lookup
        'title' => 'City at Night Mulch Series',
        'bad_spec' => 'City-at-Night-Mulch-Series_Sheet.pdf',
        'good_spec' => 'City_at_Night_Mulch_Series_Sheet.pdf',
        'bad_zip' => 'City-at-Night-Mulch-Series_HighRes.zip',
        'good_zip' => 'City_at_Night_Mulch_Series_HighRes.zip'
    ],
    // "Close up – Mulch Series Collage"
    'close-up-mulch-series-collage' => [
        'title' => 'Close up Mulch Series',
        'bad_spec' => 'Close-up-Mulch-Series_Sheet.pdf',
        'good_spec' => 'Close_up_Mulch_Series_Sheet.pdf',
        'bad_zip' => 'Close-up-Mulch-Series_HighRes.zip',
        'good_zip' => 'Close_up_Mulch_Series_HighRes.zip'
    ],
    // "Red and Black – Mulch Series Collage"
    'red-and-black-mulch-series-collage' => [
        'title' => 'Red and Black Mulch Series',
        'bad_spec' => 'Red-and-Black-Mulch-Series_Sheet.pdf',
        'good_spec' => 'Red_and_Black_Mulch_Series_Sheet.pdf',
        'bad_zip' => 'Red-and-Black-Mulch-Series_HighRes.zip',
        'good_zip' => 'Red_and_Black_Mulch_Series_HighRes.zip'
    ]
];

foreach ($targets as $slug => $data) {
    if (isset($data['title'])) {
        $page = get_page_by_title($data['title'], OBJECT, 'page');
    } else {
        $page = get_page_by_path($slug, OBJECT, 'page');
    }

    if ($page) {
        $content = $page->post_content;
        $updated = false;

        // CSS Fix
        if (isset($data['css']) && $data['css']) {
            if (strpos($content, '/* Font Imports */') !== false && strpos($content, '<style>') === false) {
                // Heuristic split
                $split = strpos($content, '<div');
                if ($split === false)
                    $split = strpos($content, '<img');

                if ($split !== false) {
                    $css = substr($content, 0, $split);
                    $rest = substr($content, $split);
                    $css = strip_tags($css);
                    $content = "<style>\n$css\n</style>\n$rest";
                    $updated = true;
                }
            }
        }

        // Link Fixes
        if (strpos($content, $data['bad_spec']) !== false) {
            $content = str_replace($data['bad_spec'], $data['good_spec'], $content);
            $updated = true;
        }
        if (strpos($content, $data['bad_zip']) !== false) {
            $content = str_replace($data['bad_zip'], $data['good_zip'], $content);
            $updated = true;
        }

        if ($updated) {
            $safe_content = esc_sql($content);
            $sql = "UPDATE {$wpdb->posts} SET post_content = '$safe_content' WHERE ID = {$page->ID}";
            $res = $wpdb->query($sql);
            echo "✅ Corrected: {$page->post_title} (Affected: $res)<br>";
            clean_post_cache($page->ID);
        } else {
            echo "ℹ️ Verified: {$page->post_title}<br>";
        }
    } else {
        echo "⚠️ Target not found: $slug / " . ($data['title'] ?? '') . "<br>";
    }
}
?>