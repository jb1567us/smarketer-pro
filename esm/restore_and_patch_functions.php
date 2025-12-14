<?php
$file = 'wp-content/themes/esm-portfolio/functions.php';
$content = file_get_contents($file);

// 1. Identify where we started adding code
$marker1 = "// Enable Tags for Pages (Added by Antigravity)";

$pos = strpos($content, $marker1);

if ($pos !== false) {
    // Found the mess. Truncate it.
    echo "Found marker at position $pos. Truncating file...\n";
    $clean_content = substr($content, 0, $pos);
    
    // 2. Remove trailing closing tag ?> from the cleaned content
    // We check the last few chars.
    $clean_content = trim($clean_content);
    if (substr($clean_content, -2) === '?>') {
        echo "Found closing PHP tag '?>'. Removing it...\n";
        $clean_content = substr($clean_content, 0, -2);
    }
    
    // 3. Re-append the code properly
    $new_code = "\n\n" .
        "// Enable Tags for Pages (Added by Antigravity)\n" .
        "function add_tags_to_pages_custom() {\n" .
        "    register_taxonomy_for_object_type('post_tag', 'page');\n" .
        "}\n" .
        "add_action('init', 'add_tags_to_pages_custom');\n" .
        "\n" .
        "// Fix Tag Filtering for Pages (Added by Antigravity)\n" .
        "function esm_include_pages_in_tag_queries(\$query) {\n" .
        "    if ( !is_admin() && \$query->is_main_query() && \$query->is_tag() ) {\n" .
        "        \$query->set('post_type', array('post', 'page'));\n" .
        "    }\n" .
        "    if ( is_admin() && \$query->is_main_query() && isset(\$_GET['tag']) ) {\n" .
        "        \$query->set('post_type', 'any');\n" .
        "    }\n" .
        "}\n" .
        "add_action('pre_get_posts', 'esm_include_pages_in_tag_queries');\n";
        
    $final_content = $clean_content . $new_code;
    
    if (file_put_contents($file, $final_content)) {
        echo "SUCCESS: functions.php has been repaired.";
    } else {
        echo "ERROR: Could not write to file.";
    }
    
} else {
    echo "Marker not found. Dumping last 100 chars for diagnostics:\n";
    echo htmlspecialchars(substr($content, -100));
}
?>
