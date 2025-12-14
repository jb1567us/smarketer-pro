<?php
// check_anemones_content.php
require_once($_SERVER['DOCUMENT_ROOT'] . '/wp-load.php');
$p = get_post(213);
echo "<h1>Content Preview</h1>";
echo "<pre>" . htmlspecialchars(substr($p->post_content, 0, 500)) . "</pre>";
?>