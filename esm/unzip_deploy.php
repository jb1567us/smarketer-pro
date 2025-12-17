<?php
// unzip_deploy.php
$zip_file = $_SERVER['DOCUMENT_ROOT'] . '/esm-deploy.zip';
$dest_dir = WPMU_PLUGIN_DIR;

echo "<h1>Zip Deployment System</h1>";

if (!file_exists($dest_dir))
    mkdir($dest_dir, 0755, true);

if (file_exists($zip_file)) {
    $zip = new ZipArchive;
    if ($zip->open($zip_file) === TRUE) {
        $zip->extractTo($dest_dir);
        $zip->close();
        echo "✅ Extracted zip to $dest_dir<br>";
        unlink($zip_file); // Clean up
    } else {
        echo "❌ Failed to open zip.<br>";
    }
} else {
    echo "❌ Zip file not found: $zip_file<br>";
}

// Verification
if (shortcode_exists('esm_artwork_layout')) {
    echo "<h2>🎉 SUCCESS: Shortcode Active!</h2>";
} else {
    echo "<h2>⚠️ Shortcode NOT verified yet.</h2>";
}
?>