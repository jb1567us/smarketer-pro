<?php
// unzip_debug.php
error_reporting(E_ALL);
ini_set('display_errors', 1);

require_once($_SERVER['DOCUMENT_ROOT'] . '/wp-load.php');

echo "<h1>Zip Debug</h1>";

// 1. Check Class
if (class_exists('ZipArchive')) {
    echo "✅ ZipArchive class exists.<br>";
} else {
    echo "❌ ZipArchive class MISSING.<br>";
}

// 2. Check Perms
$dest = WPMU_PLUGIN_DIR;
if (is_writable($dest)) {
    echo "✅ Writable: $dest<br>";
} else {
    echo "❌ Not Writable: $dest (Exists: " . (file_exists($dest) ? 'Yes' : 'No') . ")<br>";
}

// 3. Check File
$zip = $_SERVER['DOCUMENT_ROOT'] . '/esm-deploy.zip';
if (file_exists($zip)) {
    echo "✅ Zip found: $zip (" . filesize($zip) . " bytes)<br>";
} else {
    echo "❌ Zip NOT found: $zip<br>";
}

// 4. Try Extract
$z = new ZipArchive;
$res = $z->open($zip);
if ($res === TRUE) {
    echo "✅ Zip opened successfully.<br>";
    if ($z->extractTo($dest)) {
        echo "✅ Extracted!<br>";
        $z->close();
    } else {
        echo "❌ Extraction failed.<br>";
    }
} else {
    echo "❌ Failed to open zip. Code: $res<br>";
}
?>