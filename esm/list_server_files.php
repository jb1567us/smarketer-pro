<?php
$dir = __DIR__ . '/wp-content/themes/';
if (is_dir($dir)) {
    $themes = scandir($dir);
    echo "<h1>Themes in $dir</h1><ul>";
    foreach ($themes as $theme) {
        if ($theme == '.' || $theme == '..')
            continue;
        echo "<li>$theme</li>";
        if (is_dir($dir . $theme)) {
            echo "<ul>";
            $files = scandir($dir . $theme);
            foreach ($files as $file) {
                if ($file == '.' || $file == '..')
                    continue;
                echo "<li>$file</li>";
            }
            echo "</ul>";
        }
    }
    echo "</ul>";
} else {
    echo "Themes dir not found";
}
?>