<?php
header('Content-Type: text/plain');

$files = [
    $_SERVER['DOCUMENT_ROOT'] . '/artwork_data.json',
    $_SERVER['DOCUMENT_ROOT'] . '/wp-content/plugins/esm-trade-portal/artwork_data.json',
    $_SERVER['DOCUMENT_ROOT'] . '/wp-content/mu-plugins/artwork_data.json'
];

foreach ($files as $file) {
    echo "Checking: $file\n";
    if (file_exists($file)) {
        echo " - Found. Size: " . filesize($file) . " bytes\n";
        echo " - Last Modified: " . date("F d Y H:i:s.", filemtime($file)) . "\n";
        
        $json = file_get_contents($file);
        $data = json_decode($json, true);
        
        if ($data) {
            $found = false;
            foreach ($data as $item) {
                if ($item['title'] === 'Microscope 5 Painting') {
                    echo " - KEY MATCH FOUND!\n";
                    echo " - image_url: " . ($item['image_url'] ?? 'MISSING') . "\n";
                    echo " - slug: " . ($item['slug'] ?? 'MISSING') . "\n";
                    print_r($item);
                    $found = true;
                    break;
                }
            }
            if (!$found) {
                echo " - ERROR: 'Microscope 5 Painting' NOT FOUND in this file.\n";
            }
        } else {
            echo " - ERROR: Invalid JSON.\n";
        }
    } else {
        echo " - ERROR: File not found.\n";
    }
    echo "--------------------------------------------------\n";
}
?>
