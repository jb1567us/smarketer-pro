<?php
// list_theme_files.php
$root = $_SERVER['DOCUMENT_ROOT'] . '/wp-content/themes/twentytwentyfour';

function listFolderFiles($dir)
{
    $ffs = scandir($dir);
    echo '<ul style="list-style:none;">';
    foreach ($ffs as $ff) {
        if ($ff != '.' && $ff != '..') {
            $path = $dir . '/' . $ff;
            echo '<li>' . $ff;
            if (is_dir($path)) {
                listFolderFiles($path);
            }
            echo '</li>';
        }
    }
    echo '</ul>';
}

echo "<h1>📂 Theme Structure: $root</h1>";
if (is_dir($root)) {
    listFolderFiles($root);
} else {
    echo "❌ Theme directory mismatch.";
}
?>