<?php
// read_theme_templates.php
$root = $_SERVER['DOCUMENT_ROOT'] . '/wp-content/themes/twentytwentyfour';

$files = [
    '/parts/header.html',
    '/templates/page.html',
    '/templates/single.html' // Check this too
];

foreach ($files as $f) {
    if (file_exists($root . $f)) {
        echo "<h2>$f</h2>";
        $c = file_get_contents($root . $f);
        echo "<pre>" . htmlspecialchars($c) . "</pre>";
    } else {
        echo "<h2>$f NOT FOUND</h2>";
    }
}
?>