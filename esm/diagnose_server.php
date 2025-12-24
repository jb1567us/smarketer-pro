<?php
ini_set('display_errors', 1);
error_reporting(E_ALL);
require_once('wp-config.php'); // Fix: Load WP constants

$url_1 = "https://elliotspencermorgan.com/wp-content/uploads/2025/11/Purple_1_-_Mulch_SeriesCollage.jpg";
$file_1_server = WP_CONTENT_DIR . "/uploads/2025/11/Purple_1_-_Mulch_SeriesCollage.jpg";

$url_2 = "https://elliotspencermorgan.com/wp-content/uploads/2025/11-holdingspace-originals/Purple_1_-_Mulch_SeriesCollage.jpg";
$file_2_server = WP_CONTENT_DIR . "/uploads/2025/11-holdingspace-originals/Purple_1_-_Mulch_SeriesCollage.jpg";

// Check if file exists on disk
echo "<h1>Image Check</h1>";
echo "Checking: $file_1_server <br>";
if (file_exists($file_1_server)) {
    echo "<b>FOUND</b> at location 1<br>";
} else {
    echo "NOT FOUND at location 1<br>";
}

echo "Checking: $file_2_server <br>";
if (file_exists($file_2_server)) {
    echo "<b>FOUND</b> at location 2<br>";
} else {
    echo "NOT FOUND at location 2<br>";
}

// glob for it
$search = WP_CONTENT_DIR . "/uploads/2025/11-holdingspace-originals/*Purple*";
$matches = glob($search);
echo "<h2>Glob Search in holdingspace-originals</h2>";
if ($matches) {
    foreach($matches as $m) {
        echo basename($m) . "<br>";
    }
} else {
    echo "No matches found.";
}
?>
