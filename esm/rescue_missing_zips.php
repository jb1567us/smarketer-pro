<?php
// rescue_missing_zips.php
require_once($_SERVER['DOCUMENT_ROOT'] . '/wp-load.php');
ini_set('memory_limit', '512M');

$targets = [
    [
        'title' => 'Red Planet',
        'url' => 'https://elliotspencermorgan.com/wp-content/uploads/2025/11/Red_PlanetPainting.jpg'
    ],
    [
        'title' => 'Sunset Glacier Painting',
        'url' => 'https://elliotspencermorgan.com/wp-content/uploads/2025/11/Sunset_GlacierPainting.jpg'
    ],
    [
        'title' => 'Warm Glacier Painting',
        'url' => 'https://elliotspencermorgan.com/wp-content/uploads/2025/11/Warm_GlacierPainting.jpg'
    ]
];

$zip_dir = $_SERVER['DOCUMENT_ROOT'] . '/downloads/high_res/';
if (!is_dir($zip_dir))
    mkdir($zip_dir, 0755, true);

foreach ($targets as $t) {
    $title = $t['title'];
    $url = $t['url'];

    echo "<h3>Processing: $title</h3>";

    // Clean Title for Zip Matches Python
    $cleanTitle = preg_replace('/[^\w\s-]/', '', $title);
    $cleanTitle = str_replace(' ', '_', trim($cleanTitle));
    $zipName = $cleanTitle . '_HighRes.zip';
    $zipPath = $zip_dir . $zipName;

    // 1. Get Image Content
    $imgContent = false;

    // Try Local Path first (faster, reliable)
    // URL: .../wp-content/uploads/2025/11/File.jpg
    $relPath = str_replace('https://elliotspencermorgan.com/', '', $url);
    $localPath = $_SERVER['DOCUMENT_ROOT'] . '/' . $relPath;

    if (file_exists($localPath)) {
        echo "Found local file: $localPath<br>";
        $imgContent = file_get_contents($localPath);
    } else {
        echo "Local file missing ($relPath). Trying URL download...<br>";
        $imgContent = @file_get_contents($url);
    }

    if ($imgContent) {
        $cleanImgName = $cleanTitle . '.jpg';

        $zip = new ZipArchive();
        if ($zip->open($zipPath, ZipArchive::CREATE | ZipArchive::OVERWRITE) === TRUE) {
            $zip->addFromString($cleanImgName, $imgContent);
            $zip->close();
            echo "✅ Created Zip: $zipName<br>";

            // 2. Inject Link
            $page = get_page_by_title($title, OBJECT, 'page');
            if (!$page) {
                // Try slug?
                $slug = sanitize_title($title);
                $page = get_page_by_path($slug, OBJECT, 'page');
            }

            if ($page) {
                $content = $page->post_content;
                // Check if link exists
                if (strpos($content, 'HighRes.zip') === false) {
                    $zipUrl = "https://elliotspencermorgan.com/downloads/high_res/$zipName";
                    $linkHtml = '<br><a href="' . $zipUrl . '" class="trade-link" style="display:inline-block; margin-top:8px;">Download High Res Images</a>';

                    // Inject after spec link if possible
                    if (preg_match('/<a[^>]+spec_sheet[^>]+>.*?<\/a>/i', $content, $m)) {
                        $newContent = str_replace($m[0], $m[0] . $linkHtml, $content);
                    } else {
                        // Or just formatting
                        $newContent = $content . $linkHtml;
                    }
                    wp_update_post(['ID' => $page->ID, 'post_content' => $newContent]);
                    echo "✅ Injected Link into Page.<br>";
                } else {
                    echo "ℹ️ Page already has link.<br>";
                }
            } else {
                echo "⚠️ Page not found for $title.<br>";
            }

        } else {
            echo "❌ Failed to create Zip.<br>";
        }
    } else {
        echo "❌ Image not found (Local or Remote).<br>";
    }
    echo "<hr>";
}
echo "Done.";
?>