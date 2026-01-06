<?php
// inspect_blank_page_v2.php
require_once($_SERVER['DOCUMENT_ROOT'] . '/wp-load.php');

$id = 2240; // Floating 6 - Rabbit Sculpture
$page = get_post($id);

echo "<h1>Inspecting ID $id (V2)</h1>";
$content = $page->post_content;

echo "<h3>Start of Content (Escaped):</h3>";
echo "<pre style='background:#f0f0f0; padding:10px; white-space:pre-wrap;'>" . htmlspecialchars(substr($content, 0, 2000)) . "</pre>";

echo "<h3>End of Content (Escaped):</h3>";
echo "<pre style='background:#f0f0f0; padding:10px; white-space:pre-wrap;'>" . htmlspecialchars(substr($content, -1000)) . "</pre>";

// Specific Checks
echo "<h3>Diagnostic Checks:</h3>";
if (strpos($content, 'display: none') !== false)
    echo "⚠️ Found 'display: none'<br>";
if (strpos($content, 'opacity: 0') !== false)
    echo "⚠️ Found 'opacity: 0'<br>";
if (strpos($content, '</style>') === false && strpos($content, '<style>') !== false)
    echo "⚠️ Found unclosed style tag!<br>";

// Check if content starts with CSS
if (trim(substr($content, 0, 2)) === '/*')
    echo "⚠️ Content starts with comment (Raw CSS?)<br>";
?>