<?php
// Read wp-config.php lines 70-100 safely
$file = 'wp-config.php';
if (!file_exists($file)) {
    die("File not found");
}

$lines = file($file);
$start = 70;
$end = 100;

echo "<h2>Checking wp-config.php Lines $start-$end</h2>";
echo "<pre>";
for ($i = $start; $i < $end; $i++) {
    if (isset($lines[$i])) {
        echo ($i + 1) . ": " . htmlspecialchars($lines[$i]);
    }
}
echo "</pre>";
