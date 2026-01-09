<?php
// check_source_debug.php
$url = 'https://elliotspencermorgan.com/fireworks/';
$html = file_get_contents($url);

echo "<h1>🔍 Source Inspector</h1>";

if ($html) {
    // 1. Check for MU-Plugin CSS
    if (strpos($html, '.wp-block-post-title { display: none !important; }') !== false) {
        echo "✅ FOUND CSS Injection (MU-Plugin is loading).<br>";
    } else {
        echo "❌ MISSING CSS Injection (MU-Plugin NOT loading).<br>";
    }

    // 2. Check for Navigation Hamburger
    // The rendered HTML for a hamburger usually involves a button with class 'wp-block-navigation__responsive-container-open'
    if (strpos($html, 'wp-block-navigation__responsive-container-open') !== false) {
        echo "✅ FOUND Hamburger Button HTML.<br>";
    } else {
        echo "❌ MISSING Hamburger Button HTML.<br>";
    }

    // 3. Check for Page List (Failure state)
    if (strpos($html, 'wp-block-page-list') !== false) {
        echo "❌ FOUND Page List Block (Default Fallback Active).<br>";
    } else {
        echo "✅ NO Page List Block.<br>";
    }

    // 4. Check for Double Title
    // We look for wp-block-post-title class elements
    $count = substr_count($html, 'wp-block-post-title');
    echo "Found $count instances of 'wp-block-post-title'.<br>";

} else {
    echo "Could not fetch URL.";
}
?>