import json
import os

# 1. Load Data
with open(r'C:\sandbox\esm\artwork_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

items = []
for item in data:
    if not item.get('wordpress_id'): continue
    
    # Reconstruct filename logic from rename_specs.py
    # "Title of Work" -> "Title-of-Work_Sheet.pdf"
    raw_name = item['title'].replace('/', '-').replace('\\', '-') + "_Sheet.pdf"
    clean_name = raw_name.replace(" ", "-").replace("'", "").replace("&", "and")
    # Ensure URL safe? Actually I already renamed them on disk.
    
    # Use Slug for mapping
    slug = item.get('slug')
    if not slug:
         # Fallback to sanitizing title if slug missing (shouldn't be)
         slug = item['title'].lower().replace(' ', '-').replace("'", "")
    
    items.append({
        'slug': slug,
        'title': item['title'],
        'pdf': clean_name
    })

# 2. Generate PHP
php_data = "[\n"
for i in items:
    php_data += f"    '{i['slug']}' => '{i['pdf']}',\n"
php_data += "];"

php_script = f"""<?php
require_once('wp-load.php');

// 2. UPDATE LINKS
// Use sheets.zip
ini_set('display_errors', 1);
ini_set('display_startup_errors', 1);
error_reporting(E_ALL);

$zipFile = __DIR__ . '/sheets.zip';
$extractPath = __DIR__ . '/downloads/spec_sheets/';

if (!file_exists($extractPath)) mkdir($extractPath, 0755, true);

if (file_exists($zipFile)) {{
    echo "Found sheets.zip (" . filesize($zipFile) . " bytes).\\n";
    $zip = new ZipArchive;
    if ($zip->open($zipFile) === TRUE) {{
        $zip->extractTo($extractPath);
        $zip->close();
        echo "✅ Extracted ZIP (sheets.zip) to $extractPath\\n";
    }} else {{
        echo "❌ Failed to open ZIP (sheets.zip). Code: " . $zip->getStatusString() . "\\n";
    }}
}} else {{
    echo "❌ sheets.zip NOT FOUND in " . __DIR__ . "\\n";
}}

// Verify Extraction
$filesCount = count(glob($extractPath . "*.pdf"));
echo "📂 PDF Files in $extractPath: $filesCount\\n";

$map = {php_data}

echo "<pre>Updating Content Links (Debug V3)...\\n";

$count = 0;
foreach ($map as $slug => $filename) {{
    // echo "Checking slug: '$slug'... ";
    
    // Lookup by Slug
    $post = get_page_by_path($slug, OBJECT, 'page');
    
    if (!$post) {{ 
        // Force check 'portal-2' specifically to debug my data
        if ($slug == 'portal-2' || $slug == 'portal') {{
            echo "DEBUG: Slug '$slug' not found via get_page_by_path. Trying Query...\\n";
            $q = new WP_Query(['name' => $slug, 'post_type' => 'page']);
            if ($q->have_posts()) echo "  FOUND via WP_Query! ID: " . $q->posts[0]->ID . "\\n";
            else echo "  NOT FOUND via WP_Query either.\\n";
        }}
        continue; 
    }}
    
    $page_id = $post->ID;
    $content = $post->post_content;
    
    // Check if Caviar link exists
    if (strpos($content, 'caviar-spec-sheet.pdf') === false) {{
        // echo "Page $slug ($page_id): No caviar link found.\\n";
        continue;
    }}
    
    $new_link = "https://elliotspencermorgan.com/downloads/spec_sheets/" . $filename;
    
    $pattern_spec = '/href="[^"]*caviar-spec-sheet\.pdf"/i';
    $replacement_spec = 'href="' . $new_link . '"';
    
    $pattern_hr = '/href="[^"]*caviar-high-res\.zip"/i';
    $replacement_hr = 'href="#" onclick="return false;" style="opacity:0.5; cursor:not-allowed;" title="High Res Coming Soon"';
    
    $new_content = preg_replace($pattern_spec, $replacement_spec, $content);
    $new_content = preg_replace($pattern_hr, $replacement_hr, $new_content);
    
    if ($new_content !== $content) {{
        $res = wp_update_post([
            'ID' => $page_id,
            'post_content' => $new_content
        ]);
        if ($res) echo "✅ Updated Page $slug ($page_id) -> $filename\\n";
        else echo "❌ Failed Update Page $slug ($page_id)\\n";
        $count++;
    }} else {{
         echo "⚠️ Page $slug: Match failed despite strpos success.\\n";
         // Fallback simple replace
         $simple = str_replace('caviar-spec-sheet.pdf', 'spec_sheets/' . $filename, $content);
         if ($simple !== $content) {{
             wp_update_post(['ID' => $page_id, 'post_content' => $simple]);
             echo "✅ Simple Replace Page $slug\\n";
             $count++;
         }}
    }}
}}
echo "Done. Updated $count pages.</pre>";
?>
"""

with open(r'C:\sandbox\esm\update_links.php', 'w', encoding='utf-8') as f:
    f.write(php_script)
print("Generated C:\\sandbox\\esm\\update_links.php")
