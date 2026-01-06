<?php
// check_zip_content.php
$zipPath = $_SERVER['DOCUMENT_ROOT'] . '/downloads/high_res/Pieces_of_Red_Collage_HighRes.zip';
echo "<h1>Checking Zip: " . basename($zipPath) . "</h1>";

$zip = new ZipArchive();
if ($zip->open($zipPath) === TRUE) {
    echo "File Count: " . $zip->numFiles . "<br><ul>";
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