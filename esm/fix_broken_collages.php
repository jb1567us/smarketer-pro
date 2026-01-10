<?php
// fix_broken_collages.php
require_once($_SERVER['DOCUMENT_ROOT'] . '/wp-load.php');

$fixes = [
    // Page Title => [Old Base, New Base]
    'Pieces of Red Collage' => [
        'old' => 'Pieces-of-Red',
        'new' => 'Pieces_of_Red_Collage'
    ],
    'Red and Black - Mulch Series Collage' => [
        'old' => 'Red-and-Black-Mulch-Series', // Or whatever strict match
        'new' => 'Red_and_Black_-_Mulch_Series_Collage' // Check actual filename
    ],
    // Actually, checking "Red and Black Mulch Series" (JSON Title) -> Filename "Red_and_Black_Mulch_Series_Sheet.pdf"
    // Wait, JSON title is "Red and Black Mulch Series"? No, user said "Red and Black – Mulch Series Collage is a duplicate".
    // I kept ID 1865 "Red and Black Mulch Series"? 
    // Let's verify what I kept in JSON.
];

// Re-verify exact filenames before assuming.
// I will just perform a targeted fix for "Pieces of Red Collage" first as requested.
// And search for the others.

$target_pages = [
    'Pieces of Red Collage',
    'City at Night Mulch Series', // Check if this is the surviving title
    'Close up Mulch Series',
    'Red and Black Mulch Series'
];

foreach ($target_pages as $title) {
    $page = get_page_by_title($title, OBJECT, 'page');
    if (!$page) {
        $slug = sanitize_title($title);
        $page = get_page_by_path($slug, OBJECT, 'page');
    }

    if ($page) {
        $content = $page->post_content;
        // $updatedContent = $content;

        // Fix Spec Sheet Link
        // Current: .../spec_sheets/[Something]_Sheet.pdf
        // Correct: .../spec_sheets/[CleanTitle]_Sheet.pdf

        // Simple String Replace Strategy

        // 1. Pieces of Red
        $content = str_replace(
            '/downloads/spec_sheets/Pieces-of-Red_Sheet.pdf',
            '/downloads/spec_sheets/Pieces_of_Red_Collage_Sheet.pdf',
            $content
        );
        $content = str_replace(
            '/downloads/high_res/Pieces-of-Red_HighRes.zip',
            '/downloads/high_res/Pieces_of_Red_Collage_HighRes.zip',
            $content
        );

        // 2. City at Night Mulch Series
        $content = str_replace(
            '/downloads/spec_sheets/City-at-Night-Mulch-Series_Sheet.pdf',
            '/downloads/spec_sheets/City_at_Night_Mulch_Series_Sheet.pdf',
            $content
        );
        $content = str_replace(
            '/downloads/high_res/City-at-Night-Mulch-Series_HighRes.zip',
            '/downloads/high_res/City_at_Night_Mulch_Series_HighRes.zip',
            $content
        );

        // 3. Close up Mulch Series
        $content = str_replace(
            '/downloads/spec_sheets/Close-up-Mulch-Series_Sheet.pdf',
            '/downloads/spec_sheets/Close_up_Mulch_Series_Sheet.pdf',
            $content
        );
        $content = str_replace(
            '/downloads/high_res/Close-up-Mulch-Series_HighRes.zip',
            '/downloads/high_res/Close_up_Mulch_Series_HighRes.zip',
            $content
        );

        // 4. Red and Black Mulch Series
        $content = str_replace(
            '/downloads/spec_sheets/Red-and-Black-Mulch-Series_Sheet.pdf',
            '/downloads/spec_sheets/Red_and_Black_Mulch_Series_Sheet.pdf',
            $content
        );
        $content = str_replace(
            '/downloads/high_res/Red-and-Black-Mulch-Series_HighRes.zip',
            '/downloads/high_res/Red_and_Black_Mulch_Series_HighRes.zip',
            $content
        );

        if ($content !== $page->post_content) {
            wp_update_post(['ID' => $page->ID, 'post_content' => $content]);
            echo "✅ Fixed Links for: $title<br>";
        } else {
            // echo "⚠️ No changes for: $title<br>";
        }
    } else {
        echo "❌ Page not found: $title<br>";
    }
}
?>