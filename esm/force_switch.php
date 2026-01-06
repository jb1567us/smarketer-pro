<?php
// force_switch.php
require_once($_SERVER['DOCUMENT_ROOT'] . '/wp-load.php');
if (!is_dir(WP_CONTENT_DIR . '/themes/esm-portfolio'))
    die("Theme not found");
update_option('template', 'esm-portfolio');
update_option('stylesheet', 'esm-portfolio');
echo "Active: " . get_option('stylesheet');
?>