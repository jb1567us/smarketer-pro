<?php
// activate_esm.php
require_once('wp-load.php');
header('Content-Type: text/plain');

$to_activate = [
    'esm-artwork-template.php',
    'esm-trade-portal.php',
    'esm-template-v3.php'
];

$current = get_option('active_plugins');

foreach ($to_activate as $p) {
    if (!in_array($p, $current)) {
        $current[] = $p;
        echo "Activating: $p\n";
    } else {
        echo "Already active: $p\n";
    }
}

update_option('active_plugins', $current);
echo "\nUpdate complete. Active ESM plugins:\n";
foreach (get_option('active_plugins') as $p) {
    if (strpos($p, 'esm-') !== false) {
        echo "- $p\n";
    }
}
?>
