<?php
// debug_pieces_red.php
require_once($_SERVER['DOCUMENT_ROOT'] . '/wp-load.php');

$id = 2410;
$p = get_post($id);

if ($p) {
    echo "<h1>Debugging ID $id ({$p->post_title})</h1>";
    echo "Slug: " . $p->post_name . "<br>";

    $content = $p->post_content;

    // Find the Zip Link to locate the area
    $zipPos = strpos($content, 'HighRes.zip');
    if ($zipPos !== false) {
        $context = substr($content, $zipPos - 100, 400); // 100 before, 300 after
        echo "<h3>Context Area (HTMLSpecialChars):</h3>";
        echo "<textarea style='width:100%;height:150px;'>" . htmlspecialchars($context) . "</textarea><br>";

        // Attempt Fix
        // We look for: <a href="...pieces_of_redcollage/">High-Res         Images</a>
        // It likely follows the zip link.

        // Regex that covers the link matching THIS page slug?
        // Or just the text "High-Res         Images"

        $newContent = preg_replace('/<a\s+[^>]*>[\s\n]*High-Res\s+Images[\s\n]*<\/a>/i', '', $content);

        if ($newContent !== $content) {
            echo "<h2>✅ Fix Applied (Regex Match).</h2>";
            wp_update_post(['ID' => $id, 'post_content' => $newContent]);
        } else {
            echo "<h2>⚠️ Fix Failed (Regex did not match). Reference the textarea above.</h2>";
        }
    } else {
        echo "Zip link not found in content??<br>";
    }
} else {
    echo "Post 2410 not found.";
}
?>