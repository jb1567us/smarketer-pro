<?php
// check_logo_html.php
$url = 'https://elliotspencermorgan.com/fireworks/';
$html = file_get_contents($url);

echo "<h1>🔍 Logo Inspector</h1>";

if ($html) {
    if (strpos($html, 'logo.png') !== false) {
        echo "✅ FOUND 'logo.png' in HTML.<br>";
        preg_match('/<figure class=".*?header-logo.*?<\/figure>/s', $html, $matches);
        if ($matches) {
            echo "HTML Snippet: <pre>" . htmlspecialchars($matches[0]) . "</pre>";
        }
    } else {
        echo "❌ MISSING 'logo.png' in HTML.<br>";
    }
} else {
    echo "Could not fetch URL.";
}
?>