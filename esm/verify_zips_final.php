<?php
// verify_zips_final.php
$files = [
    'Pieces_of_Red_Collage_HighRes.zip',
    'Red_Planet_HighRes.zip',
    'Sunset_Glacier_Painting_HighRes.zip'
];

$dir = $_SERVER['DOCUMENT_ROOT'] . '/downloads/high_res/';
echo "<h1>Zip Verification</h1>";

foreach ($files as $f) {
    echo "<h3>Checking: $f</h3>";
    $path = $dir . $f;
    if (file_exists($path)) {
        echo "Size: " . filesize($path) . " bytes<br>";
        $zip = new ZipArchive();
        if ($zip->open($path) === TRUE) {
            echo "<b>Contains " . $zip->numFiles . " files:</b><ul>";
            for ($i = 0; $i < $zip->numFiles; $i++) {
                $stat = $zip->statIndex($i);
                echo "<li>" . $stat['name'] . " (" . $stat['size'] . ")</li>";
            }
            echo "</ul>";
            $zip->close();
        } else {
            echo "❌ Failed to Open Zip (Code: " . $zip->status . ")<br>";
        }
    } else {
        echo "❌ File Not Found.<br>";
    }
    echo "<hr>";
}
?>