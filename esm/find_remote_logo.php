<?php
// find_remote_logo.php
$root = $_SERVER['DOCUMENT_ROOT'];
echo "<h1>📂 Searching for Logo in $root</h1>";

$files = glob($root . '/logo*');
if ($files) {
    echo "<ul>";
    foreach ($files as $f) {
        echo "<li>" . basename($f) . " (Size: " . filesize($f) . " bytes)</li>";
    }
    echo "</ul>";
} else {
    echo "No logo files found in root.<br>";
}
echo "<a href='/logo.png'>Check Direct Link</a>";
?>