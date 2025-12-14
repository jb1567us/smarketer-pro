<?php
// fix_all_final.php
require_once($_SERVER['DOCUMENT_ROOT'] . '/wp-load.php');

// Prioritize SLUG to match URL
$target_slug = 'pieces_of_redcollage';
$page = get_page_by_path($target_slug, OBJECT, 'page');

if (!$page) {
    echo "⚠️ Slug lookup failed, trying title...<br>";
    $page = get_page_by_title('Pieces of Red Collage', OBJECT, 'page');
}

if ($page) {
    echo "<h1>Debugging: {$page->post_title} (ID: {$page->ID})</h1>";
    $content = $page->post_content;

    // 1. CSS FIX
    $cssFix = false;
    $cssStart = strpos($content, '/* Font Imports */');
    if ($cssStart !== false && strpos($content, '<style>') === false) {

        // Robust Split Logic
        $htmlStart = strpos($content, '<div class="artwork-page">');

        // Fallback: ANY div
        if ($htmlStart === false) {
            $htmlStart = strpos($content, '<div');
        }

        // Fallback: First <p> tag?
        if ($htmlStart === false) {
            $htmlStart = strpos($content, '<p');
        }

        if ($htmlStart !== false && $htmlStart > $cssStart) {
            $cssBlock = substr($content, $cssStart, $htmlStart - $cssStart);
            $htmlBlock = substr($content, $htmlStart);
            $cleanCss = strip_tags($cssBlock);
            $newContent = "<style>\n" . $cleanCss . "\n</style>\n" . $htmlBlock;
            if ($cssStart > 0)
                $newContent = substr($content, 0, $cssStart) . $newContent;

            $content = $newContent;
            $cssFix = true;
            echo "✅ CSS Wrapped.<br>";
        } else {
            echo "⚠️ Found CSS but no split point.<br>";
        }
    } else {
        echo "ℹ️ CSS seems OK or missing.<br>";
    }

    // 2. LINK FIX
    $linkFix = false;
    $badSpec = '/downloads/spec_sheets/Pieces-of-Red_Sheet.pdf';
    $goodSpec = '/downloads/spec_sheets/Pieces_of_Red_Collage_Sheet.pdf';

    $badZip = '/downloads/high_res/Pieces-of-Red_HighRes.zip';
    $goodZip = '/downloads/high_res/Pieces_of_Red_Collage_HighRes.zip';

    if (strpos($content, $badSpec) !== false) {
        $content = str_replace($badSpec, $goodSpec, $content);
        $linkFix = true;
        echo "✅ Spec Link Fixed.<br>";
    } else {
        echo "ℹ️ Bad Spec Link not found (Already fixed?). <br>";
    }

    if (strpos($content, $badZip) !== false) {
        $content = str_replace($badZip, $goodZip, $content);
        $linkFix = true;
        echo "✅ Zip Link Fixed.<br>";
    } else {
        echo "ℹ️ Bad Zip Link not found (Already fixed?). <br>";
    }

    // 3. SAVE
    if ($cssFix || $linkFix) {
        wp_update_post(['ID' => $page->ID, 'post_content' => $content]);
        echo "💾 Saved Changes.<br>";

        // 4. FLUSH
        if (function_exists('w3tc_flush_all'))
            w3tc_flush_all();
        if (function_exists('wp_cache_flush'))
            wp_cache_flush();
        echo "🧹 Cache Flushed.<br>";

    } else {
        echo "🤷 No changes made.<br>";
    }

    // Dump Start of content for verification
    echo "<hr>Preview Start:<br>" . htmlspecialchars(substr($content, 0, 500));
} else {
    echo "❌ Page not found.";
}
?>