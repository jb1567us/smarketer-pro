<?php
// flush_opcache.php
if (function_exists('opcache_reset')) {
    if (opcache_reset()) {
        echo "✅ Opcache Reset Successfully.<br>";
    } else {
        echo "⚠️ Opcache Reset Returned False.<br>";
    }
} else {
    echo "⚠️ Opcache Not Detected.<br>";
}

// Also try apc_clear_cache if present
if (function_exists('apc_clear_cache')) {
    apc_clear_cache();
    echo "✅ APC Cache Cleared.<br>";
}

require_once 'rebuild_theme_stack.php';
?>