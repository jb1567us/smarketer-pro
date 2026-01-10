<?php
// analyze_artwork_links.php
// Analyze all artwork pages for Spec Sheet and Zip links
// And verify if the physical files exist on the server

require_once($_SERVER['DOCUMENT_ROOT'] . '/wp-load.php');

echo '<style>
    body { font-family: sans-serif; padding: 20px; }
    table { border-collapse: collapse; width: 100%; font-size: 14px; }
    th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
    th { background-color: #f2f2f2; }
    .missing { color: red; font-weight: bold; }
    .found { color: green; }
    .partial { color: orange; }
    small { display: block; margin-top: 4px; font-family: monospace; }
</style>';

echo "<h1>🔍 Artwork Page & Asset Analysis (Re-run)</h1>";

// 1. Get all artwork PAGES
$args = [
    'post_type' => ['page'], // Focus on pages per user instruction
    'post_status' => 'publish',
    'posts_per_page' => -1,
    'orderby' => 'title',
    'order' => 'ASC',
];

$posts = get_posts($args);
echo "<p>Scanning " . count($posts) . " published pages...</p>";

echo '<table>
    <thead>
        <tr>
            <th>Artwork Page</th>
            <th>Spec Sheet Link</th>
            <th>High Res Link</th>
            <th>Status</th>
        </tr>
    </thead>
    <tbody>';

$issues_count = 0;

// Correct Server Paths
$doc_root = $_SERVER['DOCUMENT_ROOT'];
$paths = [
    'spec' => $doc_root . '/downloads/spec_sheets/',
    'zip' => $doc_root . '/downloads/high_res/'
];

foreach ($posts as $post) {
    // Basic filter: Skip obvious non-artwork pages
    if (in_array($post->post_title, ['Home', 'Portfolio', 'Contact', 'About', 'Portal', 'Cart', 'Checkout', 'My account', 'Shop']))
        continue;

    $content = $post->post_content;

    // Check for Injected Links
    $has_spec_link = (strpos($content, 'downloads/spec_sheets') !== false);
    $has_zip_link = (strpos($content, 'downloads/high_res') !== false);

    // Check for actual files on server
    $title_clean = trim($post->post_title);
    $slug = sanitize_title($title_clean);

    // Spec Search
    $spec_found = false;
    $spec_candidates = [$title_clean . '_spec.pdf', $slug . '_spec.pdf', $title_clean . '.pdf', $slug . '.pdf', str_replace(' ', '_', $title_clean) . '_spec.pdf'];
    foreach ($spec_candidates as $f) {
        if (file_exists($paths['spec'] . $f)) {
            $spec_found = $f;
            break;
        }
    }

    // Zip Search
    $zip_found = false;
    $zip_candidates = [$title_clean . '_HighRes.zip', $slug . '_HighRes.zip', $title_clean . '.zip', str_replace(' ', '_', $title_clean) . '_HighRes.zip'];
    foreach ($zip_candidates as $f) {
        if (file_exists($paths['zip'] . $f)) {
            $zip_found = $f;
            break;
        }
    }

    $row_class = '';

    // Logic: If file exists, link MUST exist.
    $missing_spec_link = ($spec_found && !$has_spec_link);
    $missing_zip_link = ($zip_found && !$has_zip_link);
    $broken_spec_link = ($has_spec_link && !$spec_found); // Link exists but file doesn't?

    if ($missing_spec_link || $missing_zip_link) {
        $row_class = 'style="background-color: #fff0f0"';
        $issues_count++;
    } elseif ($has_spec_link || $has_zip_link) {
        $row_class = 'style="background-color: #f0fff0"';
    }

    echo "<tr $row_class>";
    echo "<td><a href='" . get_permalink($post->ID) . "' target='_blank'><strong>" . esc_html($post->post_title) . "</strong></a></td>";

    // Spec Column
    echo "<td>";
    if ($has_spec_link)
        echo "🔗 Linked<br>";
    if ($spec_found)
        echo "<small style='color:green'>Found: $spec_found</small>";
    else
        echo "<small style='color:ccc'>-</small>";
    if ($missing_spec_link)
        echo "<br><span class='missing'>⚠️ MISSING LINK</span>";
    echo "</td>";

    // Zip Column
    echo "<td>";
    if ($has_zip_link)
        echo "🔗 Linked<br>";
    if ($zip_found)
        echo "<small style='color:green'>Found: $zip_found</small>";
    else
        echo "<small style='color:ccc'>-</small>";
    if ($missing_zip_link)
        echo "<br><span class='missing'>⚠️ MISSING LINK</span>";
    echo "</td>";

    echo "<td>";
    if ($missing_spec_link || $missing_zip_link)
        echo "⚠️ Fix Needed";
    elseif ($has_spec_link || $has_zip_link)
        echo "✅ OK";
    else
        echo "<span style='color:#999'>No Assets</span>";
    echo "</td>";

    echo "</tr>";
}

echo '</tbody></table>';

echo "<h2>Analysis Summary</h2>";
echo "<p>$issues_count Items found needing repair.</p>";
?>