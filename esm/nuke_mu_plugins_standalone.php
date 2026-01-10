<?php
// nuke_mu_plugins_standalone.php
// ABSOLUTELY NO WORDPRESS LOAD
// Direct file manipulation only

echo "<h1>☢️ STANDALONE NUKE (No WP Load)</h1>";

$doc_root = $_SERVER['DOCUMENT_ROOT'];
$mu_dir = $doc_root . '/wp-content/mu-plugins';

echo "Targeting: $mu_dir <br>";

if (!is_dir($mu_dir)) {
    die("❌ Error: MU-Plugins dir not found.");
}

$files = scandir($mu_dir);
foreach ($files as $file) {
    if ($file === '.' || $file === '..')
        continue;

    // Only target PHP files
    if (pathinfo($file, PATHINFO_EXTENSION) === 'php') {
        $old_path = $mu_dir . '/' . $file;
        $new_path = $mu_dir . '/' . $file . '.off';

        if (rename($old_path, $new_path)) {
            echo "✅ DISABLED: $file <br>";
        } else {
            echo "❌ FAILED to disable: $file <br>";
        }
    }
}

echo "<hr>Done. <a href='/'>Check Site</a>";
?>