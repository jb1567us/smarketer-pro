
<?php
// flush_cache.php
echo "<pre>Starting Cache Flush...\n";

// 1. Load WordPress environment
if (file_exists('wp-load.php')) {
    require_once('wp-load.php');
    echo "WordPress loaded.\n";
    
    // 2. Try Plugin Specific Flushes
    if (function_exists('w3tc_flush_all')) {
        w3tc_flush_all();
        echo "W3 Total Cache flushed.\n";
    }
    if (function_exists('wp_cache_clear_cache')) {
        wp_cache_clear_cache();
        echo "WP Super Cache flushed.\n";
    }
    if (class_exists('autoptimizeCache')) {
        autoptimizeCache::clearall();
        echo "Autoptimize flushed.\n";
    }
    
    // WP-Optimize / WPO Cache
    // Often stores cache in wp-content/cache/wpo-cache
    
    // SpeedyCache
    global $speedycache;
    if (isset($speedycache) && method_exists($speedycache, 'purge_all')) {
        $speedycache->purge_all();
        echo "SpeedyCache flushed.\n";
    }

} else {
    echo "wp-load.php not found. Proceeding with manual file deletion.\n";
}

// 3. Manual Deletion of Cache Directory
$cache_dir = 'wp-content/cache';
if (is_dir($cache_dir)) {
    echo "Deleting contents of $cache_dir...\n";
    
    $di = new RecursiveDirectoryIterator($cache_dir, FilesystemIterator::SKIP_DOTS);
    $ri = new RecursiveIteratorIterator($di, RecursiveIteratorIterator::CHILD_FIRST);
    
    foreach ($ri as $file) {
        if ($file->getFilename() === '.htaccess' || $file->getFilename() === 'index.php') continue; // Preserve basics if needed, but usually safe to nuke
        
        // Actually, let's just nuke everything except maybe the folder itself
        try {
            if ($file->isDir()) {
                rmdir($file->getRealPath());
            } else {
                unlink($file->getRealPath());
            }
        } catch (Exception $e) {
            echo "Failed to delete " . $file->getRealPath() . ": " . $e->getMessage() . "\n";
        }
    }
    echo "Manual cache clean completed.\n";
} else {
    echo "No cache directory found at $cache_dir\n";
}

// 4. Reset Opcache
if (function_exists('opcache_reset')) {
    opcache_reset();
    echo "Opcache reset.\n";
}

echo "Done.\n</pre>";
?>