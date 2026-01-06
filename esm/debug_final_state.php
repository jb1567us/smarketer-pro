<?php
// debug_final_state.php
header('Content-Type: text/plain'); // Force text output

$root = __DIR__;
echo "Root: $root\n";

$index = $root . '/index.php';
$v4 = $root . '/anemones_v4.html';

if (file_exists($index)) {
    echo "index.php exists. Content Preview:\n";
    $content = file_get_contents($index);
    echo substr($content, 0, 500) . "\n...\n";

    if (strpos($content, 'anemones_v4.html') !== false) {
        echo "✅ index.php points to v4\n";
    } else {
        echo "❌ index.php does NOT point to v4\n";
    }
} else {
    echo "❌ index.php MISSING\n";
}

if (file_exists($v4)) {
    echo "anemones_v4.html exists.\n";
} else {
    echo "❌ anemones_v4.html MISSING\n";
}

echo "Current Time: " . date('Y-m-d H:i:s') . "\n";
?>