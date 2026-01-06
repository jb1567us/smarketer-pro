<?php
// fix_css_display.php
require_once($_SERVER['DOCUMENT_ROOT'] . '/wp-load.php');

$target_pages = [
    'Pieces of Red Collage',
    'Pieces of Red' // Just in case
];

foreach ($target_pages as $title) {
    $page = get_page_by_title($title, OBJECT, 'page');
    if (!$page) {
        $slug = sanitize_title($title);
        $page = get_page_by_path($slug, OBJECT, 'page');
    }

    if ($page) {
        $content = $page->post_content;

        // Improved CSS Wrapping Logic
        // Find "/* Font Imports */"
        $cssStart = strpos($content, '/* Font Imports */');

        if ($cssStart !== false && strpos($content, '<style>') === false) {

            // Find where CSS likely ends. 
            // My template has CSS followed by <div class="artwork-page">
            $htmlStart = strpos($content, '<div class="artwork-page">');

            if ($htmlStart !== false && $htmlStart > $cssStart) {
                $cssBlock = substr($content, $cssStart, $htmlStart - $cssStart);
                $htmlBlock = substr($content, $htmlStart);

                // Clean up CSS Block (remove p tags if WP added them)
                $cleanCss = strip_tags($cssBlock); // Removes <p>, <br> etc from CSS

                $newContent = "<style>\n" . $cleanCss . "\n</style>\n" . $htmlBlock;

                // Preserve anything BEFORE the CSS (unlikely, but maybe title?)
                if ($cssStart > 0) {
                    $preamble = substr($content, 0, $cssStart);
                    // If preamble is just empty p tags, ignore?
                    $newContent = $preamble . $newContent;
                }

                wp_update_post(['ID' => $page->ID, 'post_content' => $newContent]);
                echo "✅ Wrapped CSS (Aggressive) for: $title<br>";
            } else {
                echo "⚠️ Found CSS start but couldn't find '<div class=\"artwork-page\">' to split on.<br>";
            }
        } elseif (strpos($content, '<style>') !== false) {
            echo "ℹ️ Page already has style tags: $title<br>";
        } else {
            echo "ℹ️ CSS signature not found: $title<br>";
        }
    } else {
        echo "❌ Page not found: $title<br>";
    }
}
?>