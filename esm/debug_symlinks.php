<?php
$base = '/home/elliotspencermor/public_html';
$paths = [
    "$base/content",
    "$base/content/plugins",
    "$base/content/plugins/esm-trade-portal",
    "$base/wp-content",
    "$base/wp-content/plugins",
    "$base/wp-content/plugins/esm-trade-portal"
];

echo "<pre>";
foreach ($paths as $p) {
    if (file_exists($p)) {
        echo "Path: $p\n";
        echo "Type: " . filetype($p) . "\n";
        if (is_link($p)) {
            echo "LINK -> " . readlink($p) . "\n";
        }
        echo "Realpath: " . realpath($p) . "\n";
        echo "Owner: " . fileowner($p) . "\n";
        echo "Perms: " . substr(sprintf('%o', fileperms($p)), -4) . "\n";
        echo "--------------------------\n";
    } else {
        echo "Path: $p [NOT FOUND]\n";
    }
}
echo "</pre>";
?>
