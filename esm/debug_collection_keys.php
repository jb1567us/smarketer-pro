<?php
$json = file_get_contents('c:/sandbox/esm/collections_data.json');
$data = json_decode($json, true);
if ($data) {
    echo "Found " . count($data) . " collections:\n";
    foreach (array_keys($data) as $key) {
        echo "- " . $key . "\n";
    }
} else {
    echo "Failed to decode JSON.\n";
}
?>
