<?php
ini_set('display_errors', 1);
error_reporting(E_ALL);

$file = 'wp-content/themes/esm-portfolio/functions.php';
$content = file_get_contents($file);

echo "File size: " . strlen($content) . "\n";
echo "Last 300 chars:\n";
echo "------------------------------------------------\n";
echo htmlspecialchars(substr($content, -300));
echo "\n------------------------------------------------\n";
?>