<?php
// scan_originals.php
$dir = $_SERVER['DOCUMENT_ROOT'] . '/wp-content/uploads/2025/11-holdingspace-originals/';
echo "<h1>Scanning $dir</h1>";

if (is_dir($dir)) {
    $files = scandir($dir);
    echo "Count: " . count($files) . "<br><br>";

    $limit = 50;
    foreach ($files as $f) {
        if ($f == '.' || $f == '..')
            continue;
        echo "$f<br>";
        $limit--;
        if ($limit <= 0)
            break;
    }
} else {
    echo "Directory does not exist.";
}
?>