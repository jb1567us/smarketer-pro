<?php
// unzip_specs.php
header('Content-Type: text/plain');

$zipFile = 'spec_sheets_v3.zip';
$extractTo = '11-holdingspace-specsheets';

if (!file_exists($zipFile)) {
    die("Error: $zipFile not found.\n");
}

if (!is_dir($extractTo)) {
    if (!mkdir($extractTo, 0755, true)) {
        die("Error: Failed to create directory $extractTo.\n");
    }
    echo "Created directory $extractTo\n";
}

$zip = new ZipArchive;
if ($zip->open($zipFile) === TRUE) {
    $zip->extractTo($extractTo);
    $zip->close();
    echo "Successfully extracted $zipFile to $extractTo\n";
    
    // List some files to verify
    $files = scandir($extractTo);
    echo "Files extracted: " . (count($files) - 2) . "\n";
    echo "Sample: " . $files[2] . "\n";
} else {
    echo "Error: Failed to open $zipFile\n";
}
?>
