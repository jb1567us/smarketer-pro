<?php
// inspect_blank_page.php
require_once($_SERVER['DOCUMENT_ROOT'] . '/wp-load.php');

$id = 2240; // Floating 6 - Rabbit Sculpture
$page = get_post($id);

echo "<h1>Inspecting ID $id: {$page->post_title}</h1>";
echo "Slug: " . $page->post_name . "<br>";
echo "Link: <a href='/" . $page->post_name . "/'>Visit Page</a><br>";

$content = $page->post_content;
echo "<h3>Raw Content Length: " . strlen($content) . "</h3>";

echo "<h3>Escaped Content:</h3>";
echo "<textarea style='width:100%;height:300px;'>" . htmlspecialchars($content) . "</textarea>";

echo "<h3>Preview (Rendered):</h3>";
echo "<div style='border:1px solid #ccc; padding:10px; margin:10px;'>";
echo $content;
echo "</div>";
?>