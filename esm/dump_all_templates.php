<?php
// dump_all_templates.php
require_once($_SERVER['DOCUMENT_ROOT'] . '/wp-load.php');
$dir = get_stylesheet_directory();

$files = ['header.php', 'footer.php', 'page.php', 'single.php', 'index.php'];
$dump = "";

foreach ($files as $f) {
    $path = $dir . '/' . $f;
    $dump .= "\n\n---FILE: $f ---\n";
    if (file_exists($path)) {
        $dump .= "Size: " . filesize($path) . "\n";
        $dump .= "Content:\n" . file_get_contents($path);
    } else {
        $dump .= "NOT FOUND";
    }
}

file_put_contents('debug_templates_dump.txt', $dump);
echo "Dumped to debug_templates_dump.txt";
?>