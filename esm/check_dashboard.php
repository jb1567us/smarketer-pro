<?php
require_once('wp-load.php');
$page = get_page_by_path('project-status');
if ($page) {
    echo "Page Found: " . $page->post_title . " (ID: " . $page->ID . ")<br>";
    echo "Status: " . $page->post_status . "<br>";
    echo "Author: " . $page->post_author . "<br>";
    echo "Link: " . get_permalink($page->ID);
} else {
    echo "Page 'project-status' NOT FOUND.";
    // Try by ID 2877 just in case
    $p2 = get_post(2877);
    if ($p2) {
       echo "<br>Found post 2877 though: " . $p2->post_title . " (" . $p2->post_name . ")";
    }
}
?>
