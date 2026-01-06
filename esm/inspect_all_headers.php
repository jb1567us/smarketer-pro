<?php
// inspect_all_headers.php
require_once($_SERVER['DOCUMENT_ROOT'] . '/wp-load.php');
echo "<h1>🕵️ Header Template Inspector</h1>";

$headers = get_posts([
    'post_type' => 'wp_template_part',
    'post_status' => 'any',
    'numberposts' => -1,
    'tax_query' => [['taxonomy' => 'wp_template_part_area', 'field' => 'slug', 'terms' => 'header']]
]);

echo "<table border='1'><tr><th>ID</th><th>Slug/Name</th><th>Has Logo?</th><th>Content Snippet</th></tr>";

foreach ($headers as $h) {
    $has_logo = (strpos($h->post_content, 'header-logo') !== false) ? '✅ YES' : '❌ NO';
    echo "<tr>";
    echo "<td>" . $h->ID . "</td>";
    echo "<td>" . $h->post_name . "</td>";
    echo "<td>" . $has_logo . "</td>";
    echo "<td><pre>" . htmlspecialchars(substr($h->post_content, 0, 150)) . "...</pre></td>";
    echo "</tr>";
}
echo "</table>";

echo "<h2>Check URL for Logo file:</h2>";
$logo_url = 'https://elliotspencermorgan.com/logo.png';
$headers = @get_headers($logo_url);
echo ($headers && strpos($headers[0], '200')) ? "✅ Logo File Exists (200 OK)" : "❌ Logo File NOT Reachable ($headers[0])";
?>