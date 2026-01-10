<?php
echo "PHP is working. Server Software: " . $_SERVER['SERVER_SOFTWARE'];
// Try to load WP minimal
define('WP_USE_THEMES', false);
require('./wp-blog-header.php');
echo "WP Loaded successfully";
?>
