<?php
// cleanup.php
header('Content-Type: text/plain');

$filesToDelete = [
    'unzip_specs.php',
    'spec_sheets_v3.zip',
    'cleanup.php'
];

foreach ($filesToDelete as $file) {
    if (file_exists($file)) {
        if (unlink($file)) {
            echo "Deleted $file\n";
        } else {
            echo "Failed to delete $file\n";
        }
    } else {
        echo "$file not found, skipping.\n";
    }
}
?>
