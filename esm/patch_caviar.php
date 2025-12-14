<?php
// patch_caviar.php
require_once($_SERVER['DOCUMENT_ROOT'] . '/wp-load.php');

$page = get_page_by_path('caviar', OBJECT, 'page');
if (!$page)
    $page = get_page_by_path('caviar-2', OBJECT, 'page');

if ($page) {
    $content = $page->post_content;

    // Broken link: .../caviar-high-res.zip
    // Correct link: .../Caviar_HighRes.zip

    // Also fix spec sheet if broken? Spec sheet link was .../downloads/caviar-spec-sheet.pdf
    // Spec Sheet V3: Caviar_Sheet.pdf ?
    // Check gen_spec_sheets output... Title: "Caviar". File: "Caviar_Sheet.pdf".
    // Link: caviar-spec-sheet.pdf (Hyphens).
    // Broken? 
    // I should check if Caviar_Sheet.pdf exists on server.
    // Assuming V3 script ran for Caviar? Yes.

    $updates = [
        'caviar-high-res.zip' => 'Caviar_HighRes.zip',
        // 'caviar-spec-sheet.pdf' => 'Caviar_Sheet.pdf' // Optional, verify first
    ];

    $newContent = $content;
    foreach ($updates as $bad => $good) {
        $newContent = str_replace($bad, $good, $newContent);
    }

    if ($newContent !== $content) {
        wp_update_post(['ID' => $page->ID, 'post_content' => $newContent]);
        echo "✅ Patched Caviar Page Link.<br>";
    } else {
        echo "⚠️ No changes needed for Caviar.<br>";
    }
} else {
    echo "❌ Caviar page not found.<br>";
}
?>