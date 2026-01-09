<?php
// read_file_raw.php
// NO WP-LOAD.PHP

$files = [
    'config' => 'wp-config.php',
    'functions' => 'wp-content/themes/esm-portfolio/functions.php',
    'header' => 'wp-content/themes/esm-portfolio/header.php',
    'footer' => 'wp-content/themes/esm-portfolio/footer.php',
    'page' => 'wp-content/themes/esm-portfolio/page.php',
    'index' => 'wp-content/themes/esm-portfolio/index.php'
];

echo "<h1>Raw File Reader</h1>";

foreach ($files as $label => $path) {
    echo "<h2>$label: $path</h2>";
    if (file_exists($path)) {
        echo "Size: " . filesize($path) . " bytes<br>";
        echo "<textarea style='width:100%;height:200px;'>";
        echo htmlspecialchars(file_get_contents($path));
        echo "</textarea>";
    } else {
        echo "❌ File not found";
    }
    echo "<hr>";
}
?>