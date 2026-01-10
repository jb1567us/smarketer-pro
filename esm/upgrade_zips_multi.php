<?php
// upgrade_zips_multi.php
require_once($_SERVER['DOCUMENT_ROOT'] . '/wp-load.php');
ini_set('max_execution_time', 600);
ini_set('memory_limit', '512M');

// Directory with source images
$source_dir = $_SERVER['DOCUMENT_ROOT'] . '/wp-content/uploads/2025/11/';
// Target Zip Directory
$zip_dir = $_SERVER['DOCUMENT_ROOT'] . '/downloads/high_res/';

echo "<h1>Upgrading Zips (Multi-Variant)</h1>";

// We need a list of Artworks. 
// Let's use the pages that have "HighRes.zip" links to derive the base name?
// Or better, stick to our cleaning logic.

$args = [
    'post_type' => 'page',
    'posts_per_page' => -1,
    'post_status' => 'publish'
];
$query = new WP_Query($args);

$processed = 0;

while ($query->have_posts()) {
    $query->the_post();
    $title = get_the_title();

    // Skip non-artworks if possible. Heuristic: Title must look like an artwork.
    // Or just try to find files for EVERY page title.
    if (in_array($title, ['Home', 'About', 'Contact', 'Trade', 'Cart', 'Checkout']))
        continue;

    // Clean Title -> Base Filename
    // Python Logic: re.sub(r'[^\w\s-]', '', title).strip().replace(' ', '_')
    $cleanCtx = preg_replace('/[^\w\s-]/', '', $title);
    $cleanCtx = str_replace(' ', '_', trim($cleanCtx));

    // We expect the source files to start with $cleanCtx or similar?
    // Actually, source files might be named slightly differently (e.g. "Red_PlanetPainting.jpg").
    // But we previously standardized them?
    // No, we downloaded them into `11-holdingspace-originals` as `[Title].jpg` (cleaned).
    // WAIT. If we downloaded them as `[Title].jpg`, there ARE NO variants there yet.
    // The variants exist in the ORIGINAL upload folder (`2025/11/`) where WP created them on upload.
    // BUT we don't know the original filename WP used for that upload unless we check the Media Library ID.

    // Strategy:
    // 1. Get the Page's Featured Image ID or Attached Media?
    // Most/All these pages have the image embedded in content or as Featured Image.
    // Let's try grabbing the Featured Image (Thumbnail) ID.
    $feat_id = get_post_thumbnail_id();

    if (!$feat_id) {
        // Try finding the first image in content
        $content = get_the_content();
        if (preg_match('/wp-image-(\d+)/', $content, $m)) {
            $feat_id = $m[1];
        }
    }

    if ($feat_id) {
        $meta = wp_get_attachment_metadata($feat_id);
        if ($meta && isset($meta['file'])) {
            // $meta['file'] is relative to uploads dir found in wp_upload_dir() baseurl?
            // Usually "2025/11/filename.jpg".

            $upload_dir_info = wp_upload_dir();
            $base_dir = $upload_dir_info['basedir']; // .../wp-content/uploads
            $full_path = $base_dir . '/' . $meta['file'];
            $path_info = pathinfo($full_path);
            $dir_path = $path_info['dirname'];
            $base_name = $path_info['filename']; // e.g. "Red_Planet"

            // Now Find Variants (sizes)
            // They are usually listed in $meta['sizes']
            $files_to_zip = [];

            // 1. Original
            if (file_exists($full_path))
                $files_to_zip['Original.jpg'] = $full_path;

            // 2. Sizes
            if (isset($meta['sizes'])) {
                foreach ($meta['sizes'] as $size => $data) {
                    $variant_file = $dir_path . '/' . $data['file'];
                    if (file_exists($variant_file)) {
                        $files_to_zip[$size . '.jpg'] = $variant_file;
                    }
                }
            }

            // Create Zip
            if (count($files_to_zip) > 0) {
                $zipName = $cleanCtx . '_HighRes.zip';
                $zipPath = $zip_dir . $zipName;

                $zip = new ZipArchive();
                if ($zip->open($zipPath, ZipArchive::CREATE | ZipArchive::OVERWRITE) === TRUE) {
                    foreach ($files_to_zip as $localName => $path) {
                        $zip->addFile($path, $localName);
                    }
                    $zip->close();
                    echo "📦 Zipped " . count($files_to_zip) . " files for: $title ($zipName)<br>";
                    $processed++;
                } else {
                    echo "❌ Zip Error: $title<br>";
                }
            }
        }
    } else {
        // echo "⚠️ No Image Found for: $title<br>";
    }

    if ($processed % 20 == 0)
        flush();
}

echo "Done. Processed $processed zips.";
?>