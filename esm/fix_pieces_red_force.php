<?php
// fix_pieces_red_force.php
require_once($_SERVER['DOCUMENT_ROOT'] . '/wp-load.php');

$id = 2410;
$p = get_post($id);

if ($p) {
    echo "<h1>Fixing ID $id</h1>";
    $content = $p->post_content;

    // Find Zip Link
    // "downloads/high_res/Pieces_of_Red_Collage_HighRes.zip"
    $zipSig = 'Pieces_of_Red_Collage_HighRes.zip';
    $pos = strpos($content, $zipSig);

    if ($pos !== false) {
        // Find the END of the Zip Link tag
        $endZipLink = strpos($content, '</a>', $pos);
        if ($endZipLink !== false) {
            $endZipLink += 4; // Include </a>

            // Look ahead ~200 chars for the BAD link
            // Bad link contains "High-Res" and "pieces_of_redcollage"
            $searchArea = substr($content, $endZipLink, 500);

            // Regex to match <a href="...pieces_of_redcollage...">...High-Res...</a>
            // We'll just be aggressive: remove the first <a ...>High-Res...</a> we find in this area.

            if (preg_match('/(<br\s*\/?>\s*)*<a\s+[^>]*href=[^>]*pieces_of_redcollage[^>]*>.*?High-Res.*?<\/a>/is', $searchArea, $m)) {
                $badString = $m[0];
                echo "Found bad string: " . htmlspecialchars($badString) . "<br>";

                // Remove it from content
                // Use str_replace on the WHOLE content to be safe (if unique enough)
                // Or splice it.
                $newContent = str_replace($badString, '', $content);

                // Also clean up double breaks?

                if (strlen($newContent) < strlen($content)) {
                    wp_update_post(['ID' => $id, 'post_content' => $newContent]);
                    echo "✅ Fixed!<br>";
                }
            } else {
                echo "⚠️ Bad link pattern not found in search area.<br>";
                echo "Area dump: " . htmlspecialchars($searchArea);
            }
        }
    } else {
        echo "Zip link not found.";
    }
}
?>