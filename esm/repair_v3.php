<?php
// repair_v3.php
// 1. Fixes Malformed Header (CSS/Schema leaks)
// 2. Fixes Duplicate/Unstyled Buttons
// 3. Injects proper Button Styling
require_once($_SERVER['DOCUMENT_ROOT'] . '/wp-load.php');

$mode = isset($_GET['mode']) ? $_GET['mode'] : 'dry_run';

echo "<style>body{font-family:sans-serif;padding:2rem;} .added{color:green} .removed{color:red} .box{border:1px solid #eee; padding:10px; margin:10px 0;}</style>";
echo "<h1>🎨 Repair V3: Header & Buttons ($mode)</h1>";

// 1. Load Data
$json_content = file_get_contents(__DIR__ . '/artwork_data.json');
$artworks_data = json_decode($json_content, true);
$data_map = [];
foreach ($artworks_data as $item) {
    if (isset($item['title']))
        $data_map[strtolower(trim($item['title']))] = $item;
}

// 2. CSS Content
$css_block = <<<CSS
<style>
/* Font Imports */
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,600;1,400&family=Inter:wght@300;400;500;600&display=swap');
/* Container Reset */
.artwork-page-container { font-family: 'Inter', sans-serif; color: #2c3e50; max-width: 100%; margin: 0 auto; line-height: 1.6; }
/* Global Styles for Buttons */
.btn-premium { display: inline-flex; justify-content: center; align-items: center; padding: 1rem 1.5rem; border-radius: 4px; text-decoration: none; font-weight: 500; transition: all 0.3s ease; text-transform: uppercase; letter-spacing: 0.5px; font-size: 0.9rem; cursor: pointer; }
.btn-trade { background-color: transparent; color: #1a1a1a !important; border: 1px solid #1a1a1a; }
.btn-trade:hover { background-color: #f8f9fa; color: #000 !important; }
/* Specs Box */
.designer-specs-premium { border: 1px solid #e0e0e0; padding: 2rem; border-radius: 8px; background: #fff; position: relative; overflow: hidden; margin-top: 40px; max-width: 800px; margin-left: auto; margin-right: auto; }
.designer-specs-premium::before { content: "TRADE ONLY"; position: absolute; top: 1rem; right: 1rem; font-size: 0.6rem; font-weight: 700; border: 1px solid #1a1a1a; padding: 0.25rem 0.5rem; border-radius: 2px; }
.specs-title { font-family: 'Playfair Display', serif; font-size: 1.5rem; margin-bottom: 1.5rem; margin-top: 0; }
.specs-list { list-style: none; padding: 0; margin: 0; }
.specs-list li { padding: 0.75rem 0; border-bottom: 1px solid #f0f0f0; display: flex; align-items: center; }
.check-icon { color: #27ae60; margin-right: 0.75rem; }
</style>
CSS;

$pages = get_posts(['post_type' => 'page', 'posts_per_page' => -1, 'post_status' => 'publish']);

foreach ($pages as $page) {
    if (in_array($page->post_title, ['Home', 'Portfolio', 'Contact', 'About', 'Portal', 'Checkout', 'Cart', 'Shop']))
        continue;

    echo "<div class='box'><strong>{$page->post_title}</strong><br>";
    $content = $page->post_content;
    $orig_len = strlen($content);
    $clean_title = strtolower(trim($page->post_title));
    $data = isset($data_map[$clean_title]) ? $data_map[$clean_title] : null;

    // --- STEP 1: AGGRESSIVE CLEANUP ---

    // Remove Raw CSS / Malformed Header
    // Strategy: Remove everything from start (or Font Imports) up to the first <div> or <header> or <h1>
    // We want to preserve the content but kill the bad style block.
    // Match: /* Font Imports */ ... (anything) ... up to <div or <h1
    if (strpos($content, '/* Font Imports */') !== false) {
        $content = preg_replace('/(?:\/\* Font Imports \*\/|<style>).*?(?=<div|<h1|<header)/s', '', $content, 1);
        // Also remove any stray specific leak strings like "TRADE ONLY" if they survived
        $content = str_replace('.designer-specs-premium::before { content: "TRADE ONLY";', '', $content);
    }
    // Remove any Malformed Schema that leaked text
    $content = preg_replace('/\{ "@context": "https:\/\/schema\.org".*?\}\s*/s', '', $content); // Basic removal, we will regen

    // Remove Old Buttons and Spec Boxes
    $content = preg_replace('/<div class=[\'"]specs-box[\'"].*?<\/div>/s', '', $content); // Remove previous injected box
    $content = preg_replace('/<div class=[\'"]designer-specs-premium[\'"].*?<\/div>/s', '', $content); // Remove even older one
    $content = preg_replace('/<a[^>]*>.*?High Res.*?<\/a>/is', '', $content);
    $content = preg_replace('/<a[^>]*>.*?Spec Sheet.*?<\/a>/is', '', $content);
    $content = preg_replace('/<br>\s*<br>/', '', $content); // Cleanup double breaks

    if (strlen($content) != $orig_len)
        echo "<span class='removed'>Cleaned Header/Buttons. </span>";

    // --- STEP 2: PREPARE NEW CONTENT ---

    // A. Schema
    $image_url = $data['image_url'] ?? '';
    // Escape for JSON
    $schema = [
        "@context" => "https://schema.org",
        "@type" => "VisualArtwork",
        "name" => $page->post_title,
        "artist" => ["@type" => "Person", "name" => "Elliot Spencer Morgan"],
        "image" => $image_url,
        "offers" => ["@type" => "Offer", "price" => $data['price'] ?? "950", "priceCurrency" => "USD", "availability" => "https://schema.org/InStock"]
    ];
    $schema_html = '<script type="application/ld+json">' . json_encode($schema, JSON_UNESCAPED_SLASHES) . '</script>';

    // B. Specs Box (With Button Styling)
    $installation = $data['readyToHang'] ?? "Wired & Ready to Hang";
    $framing = $data['frame'] ?? "Unframed";

    // Files
    $slug = sanitize_title($page->post_title);
    $title_c = trim($page->post_title);
    $spec_file = find_file($_SERVER['DOCUMENT_ROOT'] . '/downloads/spec_sheets/', [$title_c . '_spec.pdf', $slug . '_spec.pdf', $title_c . '.pdf']);
    $zip_file = find_file($_SERVER['DOCUMENT_ROOT'] . '/downloads/high_res/', [$title_c . '_HighRes.zip', $slug . '_HighRes.zip', $title_c . '.zip']);

    $buttons_html = "";
    if ($spec_file) {
        $url = 'https://elliotspencermorgan.com/downloads/spec_sheets/' . $spec_file;
        $buttons_html .= '<a href="' . $url . '" class="btn-premium btn-trade" style="margin-right:15px;">Download Spec Sheet</a>';
    }
    if ($zip_file) {
        $url = 'https://elliotspencermorgan.com/downloads/high_res/' . $zip_file;
        $buttons_html .= '<a href="' . $url . '" class="btn-premium btn-trade">Download High Res Images</a>';
    }

    $specs_html = <<<HTML
<div class="designer-specs-premium">
    <h3 class="specs-title">Designer Specifications</h3>
    <ul class="specs-list">
       <li><span class="check-icon">✓</span> <strong>Installation:</strong> $installation</li>
       <li><span class="check-icon">✓</span> <strong>Framing:</strong> $framing</li>
       <li><span class="check-icon">✓</span> <strong>Weight:</strong> 5 lbs (Lightweight)</li>
       <li><span class="check-icon">✓</span> <strong>Lead Time:</strong> Ships in 5-7 Days</li>
    </ul>
    <div style="margin-top: 2rem; display:flex; flex-wrap:wrap; gap:10px;">
       $buttons_html
    </div>
</div>
HTML;

    // --- STEP 3: ASSEMBLE ---
    // Ensure we have a container open 
    // If we stripped the start, we might need to add it back.
    // Assuming mostly standard layout: Styles -> Schema -> Container -> Content -> Specs -> End Container

    // If content doesn't start with container class, wrap it? 
    // Ideally we just Prepend Styles+Schema and Append Specs.
    $new_content = $css_block . "\n" . $schema_html . "\n" . $content . "\n" . $specs_html;

    if ($mode === 'inject') {
        wp_update_post(['ID' => $page->ID, 'post_content' => $new_content]);
        echo "<span class='added'> <strong>[INJECTED]</strong></span>";
    } else {
        echo "<span class='added'> [Ready to Inject]</span>";
    }
    echo "</div>";
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
    echo "<a href='?mode=inject' style='font-size:20px;display:block;margin-top:20px;'>🚀 RUN INJECTION V3</a>";
?>