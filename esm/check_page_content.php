<?php
require_once($_SERVER['DOCUMENT_ROOT'] . '/wp-load.php');
$page = get_page_by_path('animal-kingdom');
if ($page) {
    echo "<h1>DB Content for: " . $page->post_title . " (ID: " . $page->ID . ")</h1>";
    echo "<hr><pre>";
    // Use htmlspecialchars to see tags/shortcodes exactly as stored
    echo htmlspecialchars($page->post_content);
    echo "</pre><hr>";
} else {
    echo "Page not found.";
}
?>