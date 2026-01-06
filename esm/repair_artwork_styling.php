<?php
// repair_artwork_styling.php
// 1. Cleans up ugly/duplicate buttons
// 2. Injects the standardized "Designer Specifications" content box (Anemones Style)
// 3. Uses artwork_data.json for metadata

require_once($_SERVER['DOCUMENT_ROOT'] . '/wp-load.php');

$mode = isset($_GET['mode']) ? $_GET['mode'] : 'dry_run'; // 'clean', 'inject', 'dry_run'

echo "<style>body{font-family:sans-serif;padding:2rem;} .added{color:green} .removed{color:red} .skip{color:#999} .box{border:1px solid #eee; padding:10px; margin:10px 0;}</style>";
echo "<h1>🎨 Artwork Styling Repair ($mode)</h1>";

// 1. Load Data
$json_content = file_get_contents(__DIR__ . '/artwork_data.json');
$artworks_data = json_decode($json_content, true);
$data_map = [];
foreach ($artworks_data as $item) {
    if (isset($item['title'])) {
        $data_map[clean_match_title($item['title'])] = $item;
    }
}

// 2. Paths
$paths = [
    'spec' => $_SERVER['DOCUMENT_ROOT'] . '/downloads/spec_sheets/',
    'zip' => $_SERVER['DOCUMENT_ROOT'] . '/downloads/high_res/',
    'spec_url' => 'https://elliotspencermorgan.com/downloads/spec_sheets/',
    'zip_url' => 'https://elliotspencermorgan.com/downloads/high_res/'
];

// 3. Process Pages
$pages = get_posts(['post_type' => 'page', 'posts_per_page' => -1, 'post_status' => 'publish']);
$count = 0;

foreach ($pages as $page) {
    if (in_array($page->post_title, ['Home', 'Portfolio', 'Contact', 'About', 'Portal', 'Checkout', 'Cart', 'Shop']))
        continue;

    $content = $page->post_content;
    $orig_len = strlen($content);
    $clean_match_title = clean_match_title($page->post_title);

    echo "<div class='box'><strong>{$page->post_title}</strong><br>";

    // --- STEP 1: CLEANUP ---
    // Remove old "artwork-downloads" div
    $content = preg_replace('/<div class=[\'"]artwork-downloads[\'"].*?<\/div>/s', '', $content);
    // Remove loose ugly buttons (broad match for likely button HTML)
    $content = preg_replace('/<a [^>]*class=[\'"]btn btn-(spec|zip)[\'"][^>]*>.*?<\/a>/s', '', $content);
    $content = preg_replace('/<br>\s*<a [^>]*>.*?Download Spec Sheet.*?<\/a>/is', '', $content);
    // Remove "DOWNLOAD HIGH RES IMAGES" block if present (user screenshots)
    $content = preg_replace('/<a[^>]*style=[^>]*background[^>]*>.*?DOWNLOAD HIGH RES.*?<\/a>/is', '', $content);

    // Remove UNSTYLED "Designer Specifications" block (Header + List)
    // We only do this if we don't see the "specs-box" class wrapper around it
    // Use strpos check first to avoid expensive regex if not needed
    if (strpos($content, 'class="specs-box"') === false && stripos($content, 'Designer Specifications') !== false) {
        // Regex targets: Header (h2/3/4) ... List (ul) ... optionally Tags (p/div)
        // This is aggressive but necessary to clear the bad formatting
        $content = preg_replace('/<h[234][^>]*>\s*Designer Specifications\s*<\/h[234]>.*?<\/ul>/is', '', $content);
        echo "<span class='removed'>Removed unstyled specs. </span>";
    }

    if (strlen($content) != $orig_len) {
        echo "<span class='removed'>Cleaned content. </span>";
    }

    // --- STEP 2: CHECK EXISTING ---
    // Only skip if the PROPER specs-box is present
    if (strpos($content, 'class="specs-box"') !== false) {
        echo "<span class='skip'>Has Specs Box. Skipping injection.</span>";
        // Ensure changes (cleanup) are saved even if we don't inject new box
        if ($mode === 'inject' && strlen($content) != $orig_len) {
            wp_update_post(['ID' => $page->ID, 'post_content' => $content]);
            echo " [Saved Cleanup]";
        }
        echo "</div>";
        continue;
    }

    // --- STEP 3: PREPARE DATA ---
    $data = isset($data_map[$clean_match_title]) ? $data_map[$clean_match_title] : null;

    // Defaults
    $installation = "Wired & Ready to Hang";
    $weight = "5 lbs (Lightweight)";
    $framing = "Unframed";
    $lead_time = "Ships in 5-7 Days";
    $tags_html = "";

    if ($data) {
        if (!empty($data['readyToHang']))
            $installation = $data['readyToHang'];
        if (!empty($data['frame']))
            $framing = $data['frame'];
        // Tags
        if (!empty($data['styles'])) {
            $tags = is_array($data['styles']) ? $data['styles'] : explode(',', $data['styles']);
            $t_html = [];
            foreach ($tags as $t)
                $t_html[] = '<span class="tag-pill" style="display:inline-block; padding:2px 8px; border:1px solid #eee; border-radius:10px; font-size:12px; margin:2px;">' . trim($t) . '</span>';
            $tags_html = implode(' ', $t_html);
        }
    }

    // --- STEP 4: FIND ASSETS ---
    $slug = sanitize_title($page->post_title);
    $title_clean_ws = trim($page->post_title);

    $spec_file = find_file($paths['spec'], [$title_clean_ws . '_spec.pdf', $slug . '_spec.pdf', $title_clean_ws . '.pdf']);
    $zip_file = find_file($paths['zip'], [$title_clean_ws . '_HighRes.zip', $slug . '_HighRes.zip', $title_clean_ws . '.zip']);

    // --- STEP 5: BUILD HTML ---
    // Only build if we have assets OR data (but mainly we want the box for styling)

    $links_html = "";
    if ($spec_file) {
        $url = $paths['spec_url'] . $spec_file;
        $links_html .= '<a href="' . $url . '" class="download-link" style="color:#333; text-decoration:none; border-bottom:1px dotted #333; margin-right:15px; font-family:\'Inter\',sans-serif; font-size:14px;">Download Spec Sheet</a>';
    }
    if ($zip_file) {
        $url = $paths['zip_url'] . $zip_file;
        $links_html .= '<a href="' . $url . '" class="download-link" style="color:#333; text-decoration:none; border-bottom:1px dotted #333; font-family:\'Inter\',sans-serif; font-size:14px;">High-Res Images</a>';
    }

    // Template
    $specs_html = <<<HTML
<div class="specs-box" style="margin-top:40px; border:1px solid #eee; padding:30px; border-radius:4px; max-width:800px; margin-left:auto; margin-right:auto;">
    <h3 style="font-family: 'Playfair Display', serif; font-size: 1.5rem; margin-top:0; margin-bottom:20px;">Designer Specifications</h3>
    <ul style="list-style: none; padding: 0; margin:0;">
       <li style="padding: 0.5rem 0; border-bottom: 1px solid #f0f0f0;"><span style="color:green; margin-right:10px;">✓</span> <strong>Installation:</strong> $installation</li>
       <li style="padding: 0.5rem 0; border-bottom: 1px solid #f0f0f0;"><span style="color:green; margin-right:10px;">✓</span> <strong>Weight:</strong> $weight</li>
       <li style="padding: 0.5rem 0; border-bottom: 1px solid #f0f0f0;"><span style="color:green; margin-right:10px;">✓</span> <strong>Framing:</strong> $framing</li>
       <li style="padding: 0.5rem 0; border-bottom: 1px solid #f0f0f0;"><span style="color:green; margin-right:10px;">✓</span> <strong>Lead Time:</strong> $lead_time</li>
       <li style="padding: 0.5rem 0; border-bottom: 1px solid #f0f0f0;">
            <span style="font-size: 0.75rem; color: #999; text-transform: uppercase; letter-spacing: 1px; margin-right: 0.5rem;">Tags:</span>
            $tags_html
       </li>
    </ul>
    <div style="margin-top: 2rem;">
       $links_html
    </div>
</div>
HTML;

    $content .= $specs_html;
    echo "<span class='added'>PreparedSpecs Box.</span>";

    if ($mode === 'inject') {
        wp_update_post(['ID' => $page->ID, 'post_content' => $content]);
        echo " <strong>[INJECTED]</strong>";
    }

    echo "</div>";
    $count++;
}

// Helpers
function clean_match_title($t)
{
    return strtolower(trim($t));
}
function find_file($dir, $candidates)
{
    foreach ($candidates as $c) {
        if (file_exists($dir . $c))
            return $c;
        if (file_exists($dir . str_replace(' ', '_', $c)))
            return str_replace(' ', '_', $c);
    }
    return false;
}

if ($mode !== 'inject')
    echo "<a href='?mode=inject' style='font-size:20px;display:block;margin-top:20px;'>🚀 RUN INJECTION MODE</a>";
?>