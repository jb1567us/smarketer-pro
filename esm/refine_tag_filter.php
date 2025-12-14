<?php
// Path to functions.php
$file = 'wp-content/themes/esm-portfolio/functions.php';
$content = file_get_contents($file);

// We want to change the 'any' or 'array(post, page)' to just 'page' checks.
// But simpler: let's just REPLACE the function we added with the stricter version.
// The function name is: esm_include_pages_in_tag_queries

// Regex to match the whole function provided previously
// We look for "function esm_include_pages_in_tag_queries($query) {" ... up to ... "}"
// But regex multiline on code is tricky.

// Safer: Just APPEND the OVERRIDE or updated version? PHP doesn't allow re-declaring functions.
// We must replace it.

// Construct the OLD function signature to find.
$old_code_start = "function esm_include_pages_in_tag_queries(\$query) {";

// Construct the NEW code (Strict Page Only)
// We change: $query->set('post_type', 'any');  ---> $query->set('post_type', 'page');
// We change: $query->set('post_type', array('post', 'page')); ---> $query->set('post_type', 'page');

// Let's read the file line by line or string replace.
// The file content likely has:
// if ( !is_admin() ... $query->set('post_type', array('post', 'page'));
// if ( is_admin() ... $query->set('post_type', 'any');

$new_content = $content;

// 1. Update Frontend logic
$new_content = str_replace(
    "\$query->set('post_type', array('post', 'page'));",
    "\$query->set('post_type', 'page'); // Modified to exclude Posts",
    $new_content
);

// 2. Update Admin logic (or keep it 'any' for admin? User said "search up... pull up pages")
// If the User is searching in Admin, they might want to see ONLY pages too if they hate the posts.
// Let's make it ALL pages for safety.
$new_content = str_replace(
    "\$query->set('post_type', 'any');",
    "\$query->set('post_type', 'page'); // Modified to exclude Posts",
    $new_content
);

// Also handle the 'post' string variant if I wrote it differently
$new_content = str_replace(
    "\$query->set('post_type', 'post');",
    "\$query->set('post_type', 'page');",
    $new_content
);


if ($content !== $new_content) {
    if (file_put_contents($file, $new_content)) {
        echo "SUCCESS: Updated tag filter to STRICTLY show Pages only.";
    } else {
        echo "ERROR: Write failed.";
    }
} else {
    echo "WARNING: No changes made. Code matching failed. Dumping file tail...\n";
    echo htmlspecialchars(substr($content, -500));
}
?>