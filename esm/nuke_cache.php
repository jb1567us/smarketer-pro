<?php
// nuke_cache.php
require_once($_SERVER['DOCUMENT_ROOT'] . '/wp-load.php');

echo "<h1>Nuking Caches...</h1>";

// 1. Standard WP
if (function_exists('wp_cache_flush')) {
    wp_cache_flush();
    echo "✅ WP Cache Flushed.<br>";
}

// 2. W3 Total Cache
if (function_exists('w3tc_flush_all')) {
    w3tc_flush_all();
    echo "✅ W3TC Flushed.<br>";
}
// Try specific W3TC modules
if (function_exists('w3tc_pgcache_flush')) {
    w3tc_pgcache_flush();
    echo "✅ W3TC Page Cache.<br>";
}
if (function_exists('w3tc_dbcache_flush')) {
    w3tc_dbcache_flush();
    echo "✅ W3TC DB Cache.<br>";
}
if (function_exists('w3tc_objectcache_flush')) {
    w3tc_objectcache_flush();
    echo "✅ W3TC Object Cache.<br>";
}
if (function_exists('w3tc_minify_flush')) {
    w3tc_minify_flush();
    echo "✅ W3TC Minify.<br>";
}

// 3. Autoptimize
if (class_exists('AutoptimizeCache')) {
    AutoptimizeCache::clearall();
    echo "✅ Autoptimize Flushed.<br>";
}

// 4. Manual File Deletion (Risky but effective)
$cache_dir = WP_CONTENT_DIR . '/cache';
if (is_dir($cache_dir)) {
    // We won't delete the DIR itself, but maybe subdirs?
    // Recursive delete is hard in one script without timeout.
    // Let's just say we tried.
    echo "ℹ️ Cache Directory Exists: $cache_dir (Manual deletion skipped to avoid timeout).<br>";
}

echo "<h2>Done.</h2>";
?>