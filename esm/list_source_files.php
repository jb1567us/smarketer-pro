<?php
// list_source_files.php
$dir = $_SERVER['DOCUMENT_ROOT'] . '/wp-content/uploads/2025/11-holdingspace-originals/';
$files = scandir($dir);
echo "<h1>Files in $dir</h1>";
$count = 0;
foreach ($files as $f) {
    if ($f == '.' || $f == '..')
        continue;
    echo "$f<br>";
    $count++;
    if ($count > 100)
        break; // Limit output
}
?>