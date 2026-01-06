<?php
$source = __DIR__ . '/esm-trade-portal.php';
$dest = __DIR__ . '/wp-content/mu-plugins/esm-trade-portal.php';

echo "Source: $source\n";
echo "Dest: $dest\n";

if (!file_exists($source)) {
    die("ERROR: Source file /public_html/esm-trade-portal.php not found. Did the previous upload succeed?\n");
}

// Try using copy
if (copy($source, $dest)) {
    echo "SUCCESS: File copied to mu-plugins.\n";
    // Optional: unlink($source); 
} else {
    $err = error_get_last();
    echo "ERROR: Failed to copy. permission denied? Details: " . print_r($err, true) . "\n";
    
    // Try chmod if needed?
    // chmod($dest, 0644);
}
?>
