<?php
// emergency_disable_all.php
// FORCE DISABLE ALL MU-PLUGINS
$dir = $_SERVER['DOCUMENT_ROOT'] . '/wp-content/mu-plugins';
echo "<h1>🛑 DISABLE ALL</h1>";

if (is_dir($dir)) {
    $files = scandir($dir);
    echo "<ul>";
    foreach ($files as $f) {
        if ($f == '.' || $f == '..')
            continue;

        $path = $dir . '/' . $f;
        if (is_file($path) && pathinfo($path, PATHINFO_EXTENSION) === 'php') {
            $new = $path . '.off';
            if (rename($path, $new)) {
                echo "<li>✅ Disabled: $f</li>";
            } else {
                echo "<li>❌ Failed: $f</li>";
            }
        }
    }
    echo "</ul>";
}

// Read log again, strictly last 10 lines
$log = $_SERVER['DOCUMENT_ROOT'] . '/error_log';
if (file_exists($log)) {
    echo "<h3>Last Errors:</h3><pre>";
    $lines = array_slice(file($log), -10);
    echo htmlspecialchars(implode("", $lines));
    echo "</pre>";
}

if (function_exists('opcache_reset'))
    opcache_reset();
echo "<a href='/fireworks/'>Check Recovery</a>";
?>