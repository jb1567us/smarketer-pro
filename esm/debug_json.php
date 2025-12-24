<?php
$file = __DIR__ . '/artwork_data.json';
if (!file_exists($file)) {
    echo "File not found\n";
    exit;
}

$content = file_get_contents($file);
$data = json_decode($content, true);

if (json_last_error() !== JSON_ERROR_NONE) {
    echo "JSON Error: " . json_last_error_msg() . "\n";
    // Try to find where it breaks?
    // simple heuristic: find where parsing stops?
} else {
    echo "JSON is valid.\n";
    echo "Count: " . count($data) . "\n";
    foreach ($data as $item) {
        if (isset($item['title'])) {
            echo "Title: " . $item['title'] . "\n";
            if (isset($item['description'])) {
                // Check if description looks suspicious (contains { or [ or ;)
                if (strpos($item['description'], '{') !== false || strpos($item['description'], 'function') !== false) {
                    echo "  WARNING: Suspicious description in " . $item['title'] . "\n";
                    echo "  Desc start: " . substr($item['description'], 0, 50) . "...\n";
                }
            }
        }
    }
}
?>
