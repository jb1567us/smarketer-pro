<?php
// copy_root_index.php
// No WP Load
$src = 'index.php';
$dst = 'index_dump.txt';

if (copy($src, $dst)) {
    echo "<h1>Copied index.php to index_dump.txt</h1>";
    echo "Size: " . filesize($dst);
} else {
    echo "<h1>Failed to copy index.php</h1>";
}
?>