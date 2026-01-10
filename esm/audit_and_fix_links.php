<?php
// audit_and_fix_links.php
require_once($_SERVER['DOCUMENT_ROOT'] . '/wp-load.php');
ini_set('max_execution_time', 300); // 5 minutes

// Helper to clean title matches Python/Previous Logic
function clean_title_for_zip($title)
{
    // Standardize: Remove special chars, spaces to underscores
    $clean = preg_replace('/[^\w\s-]/', '', $title);
    $clean = str_replace(' ', '_', trim($clean));
    return $clean;
}

echo "<h1>High Res Link Audit & Fix (Verbose)</h1>";

$args = [
    'post_type' => 'page',
    'posts_per_page' => -1, // All pages
    'post_status' => 'publish',
];

$query = new WP_Query($args);
echo "Found " . $query->found_posts . " pages.<br><hr>";
flush();

$stats = [
    'ok' => 0,
    'fixed' => 0,
    'missing_zip' => 0,
    'ignored' => 0 // Pages that aren't artworks (e.g. Home, Contact)
];

$zip_dir = $_SERVER['DOCUMENT_ROOT'] . '/downloads/high_res/';

while ($query->have_posts()) {
    $query->the_post();
    $id = get_the_ID();
    $title = get_the_title();
    $content = get_the_content();

    // Filter: Only check pages that look like artworks?
    // Heuristic: Has "Designer Specifications" or "Spec Sheet" link?
    // Or just try to match a Zip for EVERY page?
    // Better heuristic: match Title against Zip list?

    // Strategy: Calculate Expected Zip. If it exists, Page SHOULD have link.

    $cleanTitle = clean_title_for_zip($title);
    $expectedZipName = $cleanTitle . '_HighRes.zip';
    $expectedZipPath = $zip_dir . $expectedZipName;

    if (file_exists($expectedZipPath)) {
        // This IS an artwork page because we have a zip for it.

        // Check if Link exists in content
        if (strpos($content, $expectedZipName) !== false) {
            $stats['ok']++;
            // echo "✅ OK: $title<br>";
        } else {
            // Link Missing but Zip Exists -> FIX IT

            // Where to inject?
            // 1. After Spec Sheet Link?
            // 2. End of "Designer Specifications"?
            // 3. End of content?

            $injectionPoint = false;

            // Try searching for Spec Sheet pattern
            if (preg_match('/<a[^>]+href="[^"]+spec_sheets[^"]+"[^>]*>.*?<\/a>/i', $content, $matches)) {
                $fullSpecLink = $matches[0];
                $injectionPoint = $fullSpecLink;
            }

            // Construct Link
            $zipUrl = "https://elliotspencermorgan.com/downloads/high_res/$expectedZipName";
            $newLinkHtml = '<br><a href="' . $zipUrl . '" class="trade-link" style="display:inline-block; margin-top:8px;">Download High Res Images</a>';

            if ($injectionPoint) {
                // Append after Spec Link
                $newContent = str_replace($injectionPoint, $injectionPoint . $newLinkHtml, $content);
                wp_update_post(['ID' => $id, 'post_content' => $newContent]);
                echo "🔧 FIXED (Appended to Spec Link): $title<br>";
                $stats['fixed']++;
            } else {
                // Fallback: Append to content (maybe "Tags" section?)
                // Or just append to end
                $newContent = $content . $newLinkHtml;
                wp_update_post(['ID' => $id, 'post_content' => $newContent]);
                echo "🔧 FIXED (Appended to Content): $title<br>";
                $stats['fixed']++;
            }
        }
    } else {
        // Zip does not exist.
        // Is it an artwork?
        // Check if it has a Spec Sheet link?
        if (strpos($content, 'downloads/spec_sheets/') !== false) {
            echo "⚠️ MISSING ZIP for Artwork: $title (Expected: $expectedZipName)<br>";
            $stats['missing_zip']++;
        } else {
            // Probably not an artwork (Home, About, etc)
            $stats['ignored']++;
        }
    }
}

echo "<hr>";
echo "<h3>Summary</h3>";
echo "✅ Valid Links: {$stats['ok']}<br>";
echo "🔧 Fixed Now: {$stats['fixed']}<br>";
echo "⚠️ Missing Zips: {$stats['missing_zip']}<br>";
echo "⚪ Ignored (Non-Art): {$stats['ignored']}<br>";
?>