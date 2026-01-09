<?php
// fix_double_links_sql.php
require_once($_SERVER['DOCUMENT_ROOT'] . '/wp-load.php');
global $wpdb;

echo "<h1>SQL Double Link Fix</h1>";

// 1. Inspect "Pieces of Red" (ID 2410 or slug pieces_of_redcollage)
$slug = 'pieces_of_redcollage';
$rows = $wpdb->get_results("SELECT ID, post_content FROM {$wpdb->posts} WHERE post_name = '$slug'");

if ($rows) {
    echo "Found Pieces of Red (ID {$rows[0]->ID})<br>";
    $content = $rows[0]->post_content;

    // Show us the end of content
    echo "<textarea style='width:100%;height:150px;'>" . htmlspecialchars(substr($content, -800)) . "</textarea><br>";

    // We want to delete: <a href="...pieces_of_redcollage/">High-Res         Images</a>
    // Note: The spaces. Regex in SQL is hard. LIKE is better.

    // Pattern to look for: Link with text 'High-Res' that points to ITSELF?
    // Or just any link with text 'High-Res         Images' (looks like 9 spaces?)

    // Let's try to identify the unique string signature of the bad link.
    // IT IS: ">High-Res         Images</a>"
    // Does the good link have that?
    // Good link: [Download High Res Images](...) -> <a ...>Download High Res Images</a>
    // So the text "High-Res         Images" (with extra spaces) seems likely unique to the BAD link.

    // Let's try to remove any <a> tag containing "High-Res         Images" (with spaces).
    // Or just 'High-Res % Images' in SQL LIKE.

    // Test Select
    $bad_marker = '%High-Res%Images</a>%';
    $count = $wpdb->get_var("SELECT COUNT(*) FROM {$wpdb->posts} WHERE post_content LIKE '$bad_marker'");
    echo "Found $count pages with suspicious 'High-Res...Images' link.<br>";

    if ($count > 0) {
        // We can't use REPLACE with wildcards easily in MySQL.
        // We might need to use PHP to fetch, clean, update.
        // BUT we are in a script. We can loop and update safely.

        $candidates = $wpdb->get_results("SELECT ID, post_content, post_title FROM {$wpdb->posts} WHERE post_content LIKE '$bad_marker'");
        foreach ($candidates as $post) {
            $raw = $post->post_content;

            // Regex to remove the bad link
            // <a ...>High-Res\s+Images</a>
            // Be careful not to remove the GOOD link "Download High Res Images"

            $clean = preg_replace('/<a\s+[^>]*>[^<]*High-Res\s+Images\s*<\/a>/i', '', $raw);

            if (strlen($clean) != strlen($raw)) {
                $wpdb->update($wpdb->posts, ['post_content' => $clean], ['ID' => $post->ID]);
                echo "✅ Cleaned: {$post->post_title}<br>";
            } else {
                echo "⚠️ Regex mis-match for: {$post->post_title}<br>";
            }
        }
    }
} else {
    echo "Pieces of Red not found by slug.";
}
?>