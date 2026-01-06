<?php
require_once('wp-load.php');
$id = 1927; // Portal
$page = get_post($id);
echo "<h1>DB Content for Portal ($id)</h1>";
echo "<pre>" . htmlspecialchars($page->post_content) . "</pre>";
?>