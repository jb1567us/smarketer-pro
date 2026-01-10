<?php
$zip = new ZipArchive;
if ($zip->open('spec_sheets.zip') === TRUE) {
    if ($zip->extractTo('downloads/')) {
        echo 'Extracted successfully to downloads/';
    } else {
        echo 'Failed to extract';
    }
    $zip->close();
} else {
    echo 'Failed to open spec_sheets.zip';
}
?>