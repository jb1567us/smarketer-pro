<?php
// diagnose_theme_structure.php
require_once($_SERVER['DOCUMENT_ROOT'] . '/wp-load.php');

$child = get_stylesheet_directory();
$parent = get_template_directory();

echo "<h1>Theme Structure</h1>";
echo "Active (Child): $child<br>";
echo "Parent: $parent<br>";

if ($child !== $parent) {
    echo "<h3>Child Theme Detected!</h3>";
} else {
    echo "<h3>Single Theme Mode</h3>";
}

function list_dir_sizes($dir)
{
    echo "<h4>Listing $dir</h4><ul>";
    $scan = scandir($dir);
    foreach ($scan as $f) {
        if ($f == '.' || $f == '..')
            continue;
        if (substr($f, -4) !== '.php')
            continue;

        $path = $dir . '/' . $f;
        $size = filesize($path);
        echo "<li>$f: $size bytes</li>";
    }
    echo "</ul>";
}

list_dir_sizes($child);
if ($child !== $parent) {
    list_dir_sizes($parent);
}
?>