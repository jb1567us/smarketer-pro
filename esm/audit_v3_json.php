<?php
// audit_v3_json.php
require_once($_SERVER['DOCUMENT_ROOT'] . '/wp-load.php');
ini_set('max_execution_time', 300);
header('Content-Type: application/json');

$response = [
    'total_pages' => 0,
    'missing_link_but_zip_exists' => [],
    'missing_zip_for_artwork' => [],
    'fixed_count' => 0
];

// Get ALL published pages
$pages = get_posts([
    'post_type' => 'page',
    'numberposts' => -1,
    'post_status' => 'publish'
]);

$response['total_pages'] = count($pages);
$zip_dir = $_SERVER['DOCUMENT_ROOT'] . '/downloads/high_res/';

foreach ($pages as $p) {
    if (in_array($p->post_title, ['Cart', 'Checkout', 'My account', 'Shop', 'Home', 'About', 'Contact', 'Trade']))
        continue;

    $content = $p->post_content;
    $title = $p->post_title;

    // Validate Zip Filename
    $cleanTitle = preg_replace('/[^\w\s-]/', '', $title);
    $cleanTitle = str_replace(' ', '_', trim($cleanTitle));
    $zipName = $cleanTitle . '_HighRes.zip';
    $zipPath = $zip_dir . $zipName;

    $hasLink = (strpos($content, 'HighRes.zip') !== false);
    $isArtwork = (strpos($content, 'spec_sheet') !== false); // Heuristic

    if (file_exists($zipPath)) {
        if (!$hasLink) {
            // FIX IT
            $zipUrl = "https://elliotspencermorgan.com/downloads/high_res/$zipName";
            $linkHtml = '<br><a href="' . $zipUrl . '" class="trade-link" style="display:inline-block; margin-top:8px;">Download High Res Images</a>';

            // Inject
            if ($isArtwork && preg_match('/<a[^>]+spec_sheet[^>]+>.*?<\/a>/i', $content, $m)) {
                $newContent = str_replace($m[0], $m[0] . $linkHtml, $content);
            } else {
                $newContent = $content . $linkHtml;
            }

            wp_update_post(['ID' => $p->ID, 'post_content' => $newContent]);
            $response['fixed_count']++;
            $response['missing_link_but_zip_exists'][] = $title . " (Fixed)";
        }
    } else {
        if ($isArtwork) {
            $response['missing_zip_for_artwork'][] = $title;
        }
    }
}

echo json_encode($response);
?>