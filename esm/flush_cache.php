<?php
// flush_cache.php
require_once($_SERVER['DOCUMENT_ROOT'] . '/wp-load.php');

if (function_exists('w3tc_flush_all')) {
    w3tc_flush_all();
    echo "✅ W3TC Cache Flushed.<br>";
}

if (function_exists('wp_cache_flush')) {
    wp_cache_flush();
    echo "✅ WP Object Cache Flushed.<br>";
}

// Clear any other known caches
if (class_exists('AutoptimizeCache')) {
    AutoptimizeCache::clearall();
    echo "✅ Autoptimize Cache Flushed.<br>";
}

echo "Done.";
?>