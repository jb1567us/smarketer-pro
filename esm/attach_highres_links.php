<?php
// attach_highres_links.php
require_once($_SERVER['DOCUMENT_ROOT'] . '/wp-load.php');

$args = [
    'post_type' => 'page',
    'posts_per_page' => -1,
    'post_status' => 'publish',
];

$query = new WP_Query($args);
$count = 0;
$updated = 0;

echo "Scanning " . $query->found_posts . " pages...<br>";

while ($query->have_posts()) {
    $query->the_post();
    $content = get_the_content();
    $id = get_the_ID();
    $title = get_the_title();

    // Check if has spec sheet link
    // Pattern: .../downloads/spec_sheets/(Title)_Sheet.pdf
    // Note: Use simple match first
    if (strpos($content, '/downloads/spec_sheets/') !== false) {

        /*
        // Check if already has High Res link
        if (strpos($content, 'HighRes.zip') !== false) {
            // echo "Skipping $title (Already has link)<br>";
            continue;
        }
        */

        // Regex to match the link and capture title
        // <a href=".../downloads/spec_sheets/TITLE_Sheet.pdf" ...>...</a>
        // We want to insert AFTER this </a>.

        $pattern = '/(<a\s+[^>]*href="[^"]*\/downloads\/spec_sheets\/([^"]+)_Sheet\.pdf"[^>]*>.*?<\/a>)/i';

        if (preg_match($pattern, $content, $matches)) {
            $fullLink = $matches[1];
            // $specTitle = urldecode($matches[2]); 

            // USE PAGE TITLE for Zip Naming (Matches gen_zips logic)
            // Python: re.sub(r'[^\w\s-]', '', title).strip().replace(' ', '_')
            // Note: Use the WP Page Title, which should match the JSON title used for zips.

            $cleanCtx = preg_replace('/[^\w\s-]/', '', $title);
            $cleanCtx = str_replace(' ', '_', trim($cleanCtx));
            $zipFilename = $cleanCtx . '_HighRes.zip';
            $zipUrl = "https://elliotspencermorgan.com/downloads/high_res/$zipFilename";
            $newLinkHtml = '<br><a href="' . $zipUrl . '" class="trade-link" style="display:inline-block; margin-top:8px;">Download High Res Images</a>';

            $updatedContent = $content;
            $tags_changed = false;

            // 1. Check if High Res link ALREADY exists
            // Regex: <br><a href="...high_res/..." ...>...</a>
            $existingPattern = '/<br><a\s+[^>]*href="[^"]*\/downloads\/high_res\/[^"]*"[^>]*>.*?<\/a>/i';

            if (preg_match($existingPattern, $content)) {
                // Replace it with the CORRECT link (Force Fix)
                $updatedContent = preg_replace($existingPattern, $newLinkHtml, $content, 1); // Replace 1 instance
                if ($updatedContent !== $content) {
                    // echo "Fixed Link: $title -> $zipFilename<br>";
                    $tags_changed = true;
                }
            } else {
                // 2. Insert New Link after Spec Sheet regex
                $updatedContent = str_replace($fullLink, $fullLink . $newLinkHtml, $content);
                $tags_changed = true;
            }

            if ($tags_changed) {
                $my_post = [
                    'ID' => $id,
                    'post_content' => $updatedContent,
                ];
                wp_update_post($my_post);
                echo "✅ Updated/Fixed: $title -> Link: $zipFilename<br>";
                $updated++;
            }
        }
    }
}

echo "Done. Updated $updated pages.";
?>