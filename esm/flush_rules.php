<?php
// flush_rules.php
require_once($_SERVER['DOCUMENT_ROOT'] . '/wp-load.php');

echo "<h1>Flushing Rewrite Rules</h1>";

// 1. Check if class exists
if (class_exists('ESM_Trade_Portal')) {
    echo "✅ Class ESM_Trade_Portal exists.<br>";
} else {
    echo "❌ Class ESM_Trade_Portal NOT found (Plugin not active?).<br>";
}

// 2. Add Rule Manually (just in case init didn't fire yet)
add_rewrite_rule('^trade/?$', 'index.php?esm_trade=1', 'top');
add_rewrite_tag('%esm_trade%', '1');

// 3. Flush
global $wp_rewrite;
$wp_rewrite->flush_rules(true); // Hard flush

echo "✅ Rules Flushed.<br>";

// 4. Test Match
$url = home_url('/trade/');
echo "Test URL: <a href='$url'>$url</a><br>";
?>