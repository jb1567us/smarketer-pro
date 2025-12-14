<?php
// Path to functions.php
$file_path = 'wp-content/themes/esm-portfolio/functions.php';

if (!file_exists($file_path)) {
    die("Error: functions.php not found at $file_path");
}

$content = file_get_contents($file_path);

// Check if already modified
if (strpos($content, 'esm_include_pages_in_tag_queries') !== false) {
    die("Success: Tag query fix is already present in functions.php.");
}

// Code to append
$code = "\n" .
    "// Fix Tag Filtering for Pages (Added by Antigravity)\n" .
    "function esm_include_pages_in_tag_queries(\$query) {\n" .
    "    // Frontend Tag Archives\n" .
    "    if ( !is_admin() && \$query->is_main_query() && \$query->is_tag() ) {\n" .
    "        \$query->set('post_type', array('post', 'page'));\n" .
    "    }\n" .
    "    // Admin Tag Filters (edit.php?tag=...)\n" .
    "    if ( is_admin() && \$query->is_main_query() && isset(\$_GET['tag']) ) {\n" .
    "        \$query->set('post_type', 'any');\n" .
    "    }\n" .
    "}\n" .
    "add_action('pre_get_posts', 'esm_include_pages_in_tag_queries');\n";

// Append
if (file_put_contents($file_path, $code, FILE_APPEND | LOCK_EX)) {
    echo "Success: Patched functions.php to include Pages in tag filters!";
} else {
    echo "Error: Failed to write to functions.php. Check permissions.";
}
?>