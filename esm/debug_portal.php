<?php
ini_set('display_errors', 1);
error_reporting(E_ALL);

$target_path = $_SERVER['DOCUMENT_ROOT'] . '/downloads/high_res/Portal_2_HighRes.zip';

echo "<h1>Portal 2 Debug</h1>";
echo "Checking specific path: " . $target_path . "\n";

if (file_exists($target_path)) {
    echo "SUCCESS: File EXISTS at exact path.\n";
    echo "Size: " . filesize($target_path) . " bytes\n";
    echo "Permissions: " . substr(sprintf('%o', fileperms($target_path)), -4) . "\n";
} else {
    echo "FAILURE: File does NOT exist at exact path.\n";
}

echo "\nDirectory Scan (Hex Check):\n";
$dir = $_SERVER['DOCUMENT_ROOT'] . '/downloads/high_res/';
$files = scandir($dir);
foreach ($files as $f) {
    if (stripos($f, 'Portal') !== false) {
        echo "Found candidate: '$f'\n";
        echo "Hex: ";
        for ($i = 0; $i < strlen($f); $i++) {
            echo dechex(ord($f[$i])) . " ";
        }
        echo "\n";
    }
}

echo "\nChecking 'Portal 2' title in JSON:\n";
$json_path = $_SERVER['DOCUMENT_ROOT'] . '/artwork_data.json';
$data = json_decode(file_get_contents($json_path), true);
foreach ($data as $item) {
    if (isset($item['title']) && stripos($item['title'], 'Portal') !== false) {
        echo "Found JSON Title: '{$item['title']}'\n";
        echo "Hex: ";
        for ($i = 0; $i < strlen($item['title']); $i++) {
            echo dechex(ord($item['title'][$i])) . " ";
        }
        echo "\n";
    }
}
?>
