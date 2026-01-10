<?php
$file = __DIR__ . '/wp-content/themes/esm-portfolio/page.php';
if (file_exists($file)) {
    echo "<h1>page.php Content</h1><pre>";
    echo htmlspecialchars(file_get_contents($file));
    echo "</pre>";
} else {
    echo "File not found";
}
?>