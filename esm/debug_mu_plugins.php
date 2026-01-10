<?php
// debug_mu_plugins.php
$dir = $_SERVER['DOCUMENT_ROOT'] . '/wp-content/mu-plugins';
echo "<h1>🛠️ Debugging MU Plugins</h1>";

if (is_dir($dir)) {
    echo "Directory exists: $dir<br>";
    $files = scandir($dir);
    echo "<ul>";
    foreach ($files as $f) {
        if ($f == '.' || $f == '..')
            continue;
        echo "<li>$f";

        if (strpos($f, '.php') !== false) {
            $full_path = $dir . '/' . $f;
            $new_name = $full_path . '.off';
            if (rename($full_path, $new_name)) {
                echo " ➡️ <strong>DISABLED (.off)</strong>";
            } else {
                echo " ❌ <strong>RENAME FAILED</strong>";
            }
        }
        echo "</li>";
    }
    echo "</ul>";
} else {
    echo "❌ Directory '$dir' NOT FOUND.<br>";
}

if (function_exists('opcache_reset')) {
    opcache_reset();
    echo "Cache flushed.<br>";
}
echo "<a href='/fireworks/'>Check Site</a>";
?>