<?php
// audit_fix_v2.php
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

echo "<h1>High Res Link Audit & Fix (V2)</h1>";

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
$found_zips = 0;

while ($query->have_posts()) {
    $query->the_post();
    $id = get_the_ID();
    $title = get_the_title();
    $content = get_the_content();

    // Calculate Expected Zip
    $cleanTitle = clean_title_for_zip($title);
    $expectedZipName = $cleanTitle . '_HighRes.zip';
    $expectedZipPath = $zip_dir . $expectedZipName;

    if (file_exists($expectedZipPath)) {
        // Zip Exists -> Should have Link
        // Check if Link exists
        // Regex allows for variation in button text? Or just check filename
        if (strpos($content, $expectedZipName) !== false) {
            $stats['ok']++;
            echo "."; // Progress dot
            if ($stats['ok'] % 50 == 0)
                echo "<br>";
        } else {
            // Link Missing but Zip Exists -> FIX IT

            // Injection Logic
            $injectionPoint = false;
            if (preg_match('/<a[^>]+href="[^"]+spec_sheets[^"]+"[^>]*>.*?<\/a>/i', $content, $matches)) {
                $fullSpecLink = $matches[0];
                $injectionPoint = $fullSpecLink;
            }

            $zipUrl = "https://elliotspencermorgan.com/downloads/high_res/$expectedZipName";
            $newLinkHtml = '<br><a href="' . $zipUrl . '" class="trade-link" style="display:inline-block; margin-top:8px;">Download High Res Images</a>';

            if ($injectionPoint) {
                $newContent = str_replace($injectionPoint, $injectionPoint . $newLinkHtml, $content);
                wp_update_post(['ID' => $id, 'post_content' => $newContent]);
                echo "<br>🔧 FIXED (After Spec): $title<br>";
                $stats['fixed']++;
            } else {
                // Append to end if no spec link
                $newContent = $content . $newLinkHtml;
                wp_update_post(['ID' => $id, 'post_content' => $newContent]);
                echo "<br>🔧 FIXED (Appended): $title<br>";
                $stats['fixed']++;
            }
        }
    } else {
        // Zip Missing
        // Is it an artwork? (Has Spec Sheet link)
        if (strpos($content, 'downloads/spec_sheets/') !== false) {
            echo "<br>⚠️ MISSING ZIP: $title (Expected: $expectedZipName)<br>";
            $stats['missing_zip']++;
        } else {
            $stats['ignored']++;
        }
    }

    // Check old "HighRes.zip" links that might point to wrong file?
    // User complaint: "pieces of red has errors". We fixed that.
    // Any other generic checks?
    flush();
}

echo "<hr>";
echo "<h3>Summary</h3>";
echo "✅ OK: {$stats['ok']}<br>";
echo "🔧 Fixed: {$stats['fixed']}<br>";
echo "⚠️ Missing Zips: {$stats['missing_zip']}<br>";
echo "⚪ Ignored: {$stats['ignored']}<br>";
echo "Total Processed: " . array_sum($stats) . "<br>";
?>