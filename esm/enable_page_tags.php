<?php
// Path to functions.php
// We are in public_html, so path is:
$file_path = 'wp-content/themes/esm-portfolio/functions.php';

if (!file_exists($file_path)) {
    die("Error: functions.php not found at $file_path");
}

$content = file_get_contents($file_path);

// Check if already modified
if (strpos($content, 'register_taxonomy_for_object_type(\'post_tag\', \'page\')') !== false) {
    die("Success: Tags for pages are already enabled in functions.php.");
}

// Code to append
$code = "\n" .
    "// Enable Tags for Pages (Added by Antigravity)\n" .
    "function add_tags_to_pages_custom() {\n" .
    "    register_taxonomy_for_object_type('post_tag', 'page');\n" .
    "}\n" .
    "add_action('init', 'add_tags_to_pages_custom');\n";

// Append
if (file_put_contents($file_path, $code, FILE_APPEND | LOCK_EX)) {
    echo "Success: Enabled tags for pages in functions.php!";
} else {
    echo "Error: Failed to write to functions.php. Check permissions.";
}
?>