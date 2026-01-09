<?php
// upgrade_zips_batch.php
require_once($_SERVER['DOCUMENT_ROOT'] . '/wp-load.php');
ini_set('max_execution_time', 300);
ini_set('memory_limit', '512M');

$jsonFile = $_SERVER['DOCUMENT_ROOT'] . '/artwork_data.json';
if (!file_exists($jsonFile))
    die("JSON file not found.");
$artworks = json_decode(file_get_contents($jsonFile), true);

$offset = isset($_GET['offset']) ? intval($_GET['offset']) : 0;
$limit = 50;
$current = 0;
$processed = 0;
$zip_dir = $_SERVER['DOCUMENT_ROOT'] . '/downloads/high_res/';

echo "<h1>Batch Process (Offset $offset, Limit $limit)</h1>";

foreach ($artworks as $art) {
    if ($current < $offset) {
        $current++;
        continue;
    }
    if ($processed >= $limit)
        break;

    $title = $art['title'];
    $imgUrl = $art['image_url'] ?? '';

    if (empty($imgUrl)) {
        $current++;
        continue;
    }

    $relPath = str_replace('https://elliotspencermorgan.com/', '', $imgUrl);
    $localPath = $_SERVER['DOCUMENT_ROOT'] . '/' . $relPath;

    if (file_exists($localPath)) {
        $pathInfo = pathinfo($localPath);
        $dir = $pathInfo['dirname'];
        $filename = $pathInfo['filename'];
        $ext = $pathInfo['extension'];

        // Glob for variants
        // Careful with case sensitivity
        $matches = glob($dir . '/' . $filename . '*.' . $ext);

        // Filter
        $valid_files = [];
        if ($matches) {
            foreach ($matches as $m) {
                // Ensure it's a true variant (starts with filename)
                if (strpos(basename($m), $filename) === 0) {
                    $valid_files[basename($m)] = $m;
                }
            }
        }

        if (count($valid_files) > 0) {
            // Create Zip
            $cleanTitle = preg_replace('/[^\w\s-]/', '', $title);
            $cleanTitle = str_replace(' ', '_', trim($cleanTitle));
            $zipName = $cleanTitle . '_HighRes.zip';
            $zipPath = $zip_dir . $zipName;

            $zip = new ZipArchive();
            // Open with OVERWRITE
            if ($zip->open($zipPath, ZipArchive::CREATE | ZipArchive::OVERWRITE) === TRUE) {
                foreach ($valid_files as $name => $path) {
                    $zip->addFile($path, $name);
                }
                $zip->close();
                echo "✅ Zipped " . count($valid_files) . " items: $zipName<br>";
                $processed++;
            } else {
                echo "❌ Zip Fail: $zipName<br>";
            }
        }
    }
    $current++;
}

echo "<hr>Batch Done. Processed $processed items.<br>";
$next = $offset + $limit;
if ($next < count($artworks)) {
    echo "<a href='?offset=$next'>Next Batch</a>";
} else {
    echo "All Done.";
}
?>