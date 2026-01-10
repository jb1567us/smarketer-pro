<?php
// verify_zip_content.php
// Check Red Planet
$zipPath = $_SERVER['DOCUMENT_ROOT'] . '/downloads/high_res/Red_Planet_HighRes.zip';

echo "<h1>Verifying Zip: " . basename($zipPath) . "</h1>";

$zip = new ZipArchive();
if ($zip->open($zipPath) === TRUE) {
    echo "Files found: " . $zip->numFiles . "<br><ul>";
    for ($i = 0; $i < $zip->numFiles; $i++) {
        $stat = $zip->statIndex($i);
        echo "<li>" . $stat['name'] . " (" . $stat['size'] . " bytes)</li>";
    }
    echo "</ul>";
    $zip->close();
} else {
    echo "Failed to open zip.";
}
?>