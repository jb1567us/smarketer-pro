<?php
// fix_double_links_dom.php
require_once($_SERVER['DOCUMENT_ROOT'] . '/wp-load.php');
ini_set('max_execution_time', 300);

echo "<h1>Fixing Double Links (DOM)</h1>";

$pages = get_posts([
    'post_type' => 'page',
    'numberposts' => -1,
    'post_status' => 'publish'
]);

$fixed = 0;

foreach ($pages as $p) {
    if (in_array($p->post_title, ['Home', 'About', 'Contact', 'Trade']))
        continue;

    $content = $p->post_content;

    // Safety: Only process if we have a valid zip link
    if (strpos($content, 'HighRes.zip') === false)
        continue;

    // Using DOMDocument to be precise
    // Note: detailed HTML parsing can be messy if partial valid HTML
    // We will target the string block more intelligently if DOM fails?
    // Let's try str_replace approach using the EXACT string found in the artifact.
    // "[High-Res Images](...)" is Markdown representation.
    // The HTML is <a href="...">High-Res Images</a>
    // The issue is whitespace.

    // Strategy: Split by "HighRes.zip" link. Look at what follows.
    // If what follows contains "High-Res Images", strip it.

    // Find Position of Zip Link
    $pos = strpos($content, 'HighRes.zip');
    if ($pos !== false) {
        // Look ahead 200 chars
        $start = strrpos(substr($content, 0, $pos), '<a'); // Start of Zip Link
        $end_of_zip_link = strpos($content, '</a>', $pos);

        if ($end_of_zip_link !== false) {
            $end_of_zip_link += 4; // include </a>

            $suffix = substr($content, $end_of_zip_link);

            // Look for the "bad" link in the immediate suffix
            // <br><a href="https://elliotspencermorgan.com/pieces_of_redcollage/">High-Res         Images</a>

            // Regex match ANY link with text "High-Res Images"
            if (preg_match('/(<br\s*\/?>\s*)*<a\s+[^>]+>[\s\n]*High-Res[\s\n]+Images[\s\n]*<\/a>/i', $suffix, $matches)) {
                $bad_string = $matches[0];
                $new_suffix = str_replace($bad_string, '', $suffix);
                $newContent = substr($content, 0, $end_of_zip_link) . $new_suffix;

                wp_update_post(['ID' => $p->ID, 'post_content' => $newContent]);
                echo "✅ Fixed DOM/Regex: {$p->post_title}<br>";
                $fixed++;
            }
        }
    }
}

echo "Done. Fixed $fixed pages.";
?>