<?php
// deploy_clean.php
$zipFile = __DIR__ . '/sheets_v3.zip';
$extractPath = __DIR__ . '/downloads/spec_sheets/';

// 1. Ensure zip exists
if (!file_exists($zipFile)) {
    die("❌ Error: sheets_v3.zip not found.");
}

// 2. Ensure target dir exists
if (!is_dir($extractPath)) {
    mkdir($extractPath, 0755, true);
}

// 3. WIPE DIRECTORY
echo "🧹 Cleaning directory: $extractPath<br>";
$files = glob($extractPath . '*'); // get all files
foreach ($files as $file) {
    if (is_file($file)) {
        unlink($file); // delete file
        // echo "Deleted: " . basename($file) . "<br>"; // verbose?
    }
}
echo "✅ Directory wiped.<br>";

// 4. Extract Zip
$zip = new ZipArchive;
if ($zip->open($zipFile) === TRUE) {
    $zip->extractTo($extractPath);
    $zip->close();
    echo "✅ Extracted sheets_v3.zip to $extractPath<br>";

    // List counts
    $pdfCount = count(glob($extractPath . "*.pdf"));
    echo "📄 Total PDFs: $pdfCount<br>";

} else {
    echo "❌ Failed to open zip file.<br>";
}

// 5. Cleanup self?
// unlink(__FILE__);
?>