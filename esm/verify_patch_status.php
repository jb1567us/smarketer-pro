<?php
// verify_patch_status.php
$root = $_SERVER['DOCUMENT_ROOT'] . '/wp-content/themes/twentytwentyfour';
$page_file = $root . '/templates/page.html';

echo "<h1>🔍 Patch Verifier</h1>";

// 1. Check Disk Content
if (file_exists($page_file)) {
    $c = file_get_contents($page_file);
    if (strpos($c, 'wp:post-title') === false) {
        echo "✅ Disk: page.html has NO Title Block.<br>";
    } else {
        echo "❌ Disk: page.html STILL HAS Title Block.<br>";
        echo "<pre>" . htmlspecialchars(substr($c, 0, 800)) . "</pre>";
    }
} else {
    echo "❌ page.html not found.<br>";
}

// 2. Check Live HTML (Self-Request)
$url = 'https://elliotspencermorgan.com/fireworks/';
$live = file_get_contents($url); // Simple fetch

if ($live) {
    if (strpos($live, 'wp-block-post-title') === false) {
        echo "✅ Live: HTML has NO Title Class.<br>";
    } else {
        echo "❌ Live: HTML STILL HAS Title Class.<br>";
        // Show context
        preg_match('/<h1.*?wp-block-post-title.*?<\/h1>/s', $live, $matches);
        if ($matches) {
            echo "Found: " . htmlspecialchars($matches[0]) . "<br>";
        }
    }
} else {
    echo "⚠️ Could not fetch live URL.<br>";
}
?>