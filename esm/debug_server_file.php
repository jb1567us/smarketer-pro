<?php
// debug_server_file.php
$files = [
    'wp-content/themes/caviar-premium/header.php',
    'wp-content/mu-plugins/esm-logo-injector.php'
];

foreach ($files as $file) {
    echo "--- START $file ---\n";
    if (file_exists($file)) {
        echo file_get_contents($file);
    } else {
        echo "FILE NOT FOUND";
    }
    echo "\n--- END $file ---\n";
}
?>
