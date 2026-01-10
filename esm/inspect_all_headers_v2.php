<?php
// inspect_all_headers_v2.php
require_once($_SERVER['DOCUMENT_ROOT'] . '/wp-load.php');
header('Content-Type: text/plain'); // Force plain text

echo "--- HEADER INSPECTOR V2 ---\n";

$headers = get_posts([
    'post_type' => 'wp_template_part',
    'post_status' => 'any',
    'numberposts' => -1,
    'tax_query' => [['taxonomy' => 'wp_template_part_area', 'field' => 'slug', 'terms' => 'header']]
]);

foreach ($headers as $h) {
    $has_logo = (strpos($h->post_content, 'header-logo') !== false) ? 'YES_LOGO' : 'NO_LOGO';
    echo "ID: " . $h->ID . "\n";
    echo "Slug: " . $h->post_name . "\n";
    echo "Status: " . $has_logo . "\n";
    echo "--------------------------\n";
}

$logo_url = 'https://elliotspencermorgan.com/logo.png';
$headers = @get_headers($logo_url);
echo "File Check: " . (($headers && strpos($headers[0], '200')) ? "EXISTS" : "MISSING") . "\n";
?>