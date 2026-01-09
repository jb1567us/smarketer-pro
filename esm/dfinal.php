<?php
// cln3.php - Split Deploy
$extractPath = __DIR__ . '/downloads/spec_sheets/';
$zips = ['sheets_v3_1.zip', 'sheets_v3_2.zip'];

// 1. Wipe Directory
if (!is_dir($extractPath))
    mkdir($extractPath, 0755, true);
echo "🧹 Wiping $extractPath<br>";
$files = glob($extractPath . '*');
foreach ($files as $file) {
    if (is_file($file))
        unlink($file);
}

// 2. Extract Zips
$zip = new ZipArchive;
foreach ($zips as $zipFile) {
    $fullPath = __DIR__ . '/' . $zipFile;
    if (file_exists($fullPath)) {
        if ($zip->open($fullPath) === TRUE) {
            $zip->extractTo($extractPath);
            $zip->close();
            echo "✅ Extracted $zipFile<br>";
            unlink($fullPath); // Cleanup zip after
        } else {
            echo "❌ Failed to open $zipFile<br>";
        }
    } else {
        echo "⚠️ Missing $zipFile<br>";
    }
}

// 3. Count
$pdfCount = count(glob($extractPath . "*.pdf"));
echo "📄 Total PDFs Verified: $pdfCount<br>";
?>