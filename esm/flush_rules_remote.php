<?php
require_once('wp-load.php');
flush_rewrite_rules();
echo "Rewrite rules flushed successfully.";
unlink(__FILE__);
