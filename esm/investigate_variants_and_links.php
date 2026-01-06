<?php
// investigate_variants_and_links.php
require_once($_SERVER['DOCUMENT_ROOT'] . '/wp-load.php');

$upload_dir = $_SERVER['DOCUMENT_ROOT'] . '/wp-content/uploads/2025/11-holdingspace-originals/';

echo "<h1>Investigation</h1>";

// 1. Check Source Files
echo "<h2>1. File Structure Check</h2>";
$patterns = ['Red_Planet*', 'Pieces_of_Red*', 'Sunset_Glacier*'];
foreach ($patterns as $p) {
    echo "<b>Pattern: $p</b><br>";
    $files = glob($upload_dir . $p);
    if ($files) {
        foreach ($files as $f) {
            echo basename($f) . " (" . filesize($f) . " bytes)<br>";
        }
    } else {
        echo "No matches found.<br>";
    }
    echo "<br>";
}

// 2. Check Double Links
echo "<h2>2. Page Content Check</h2>";
$titles = ['Pieces of Red Collage', 'Red Planet'];
foreach ($titles as $t) {
    $page = get_page_by_title($t, OBJECT, 'page');
    if (!$page) {
        // Try Slug
        $slug = sanitize_title($t); // e.g. pieces-of-red-collage or pieces_of_redcollage?
        // Known slugs: pieces_of_redcollage, red_planet
        if ($t == 'Pieces of Red Collage')
            $slug = 'pieces_of_redcollage';
        if ($t == 'Red Planet')
            $slug = 'red_planet';
        $page = get_page_by_path($slug, OBJECT, 'page');
    }

    if ($page) {
        echo "<b>Page: {$page->post_title} (ID: {$page->ID})</b><br>";
        $content = $page->post_content;
        echo "Snippet (Last 500 chars):<br>";
        echo "<textarea style='width:100%;height:100px;'>" . htmlspecialchars(substr($content, -800)) . "</textarea><br>";
    } else {
        echo "Page not found: $t<br>";
    }
}
?>