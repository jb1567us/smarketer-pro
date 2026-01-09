<?php
// fix_work_party_formatted_sql.php
require_once($_SERVER['DOCUMENT_ROOT'] . '/wp-load.php');
global $wpdb;

echo "<h1>Fixing Work Party (SQL)</h1>";

// Find ID by fuzzy title
$rows = $wpdb->get_results("SELECT ID, post_title, post_content FROM {$wpdb->posts} WHERE post_title LIKE '%Work Party%' AND post_status='publish'");

if ($rows) {
    foreach ($rows as $post) {
        $id = $post->ID;
        echo "Processing ID $id: {$post->post_title}<br>";

        $content = $post->post_content;
        $modified = false;

        // 1. Fix Raw CSS (/* Font Imports ... */)
        // If it starts with comment or import and NOT style
        if (strpos($content, '/* Font Imports */') !== false && strpos($content, '<style>/* Font Imports */') === false) {
            $content = str_replace('/* Font Imports */', '<style>/* Font Imports */', $content);

            // Close style at first HTML tag
            if (preg_match('/(\n\s*<(div|p|h[1-6]))/i', $content, $m, PREG_OFFSET_CAPTURE)) {
                $pos = $m[0][1];
                $content = substr_replace($content, "</style>", $pos, 0);
            } else {
                // Fallback: Just close it after some heuristic? or fail safe?
                // Append </style> to end of suspected block? 
                // Let's assume block ends before "Piece Name"
                // Or just append it right after the replacement? NO.
                $content .= "</style>"; // Worst case: wrap entire page? Bad.
            }
            $modified = true;
            echo " -> CSS Wrapped.<br>";
        }

        // 2. Links -> Buttons
        // Regex Replace
        // Matches <a ... href=".../spec_sheets/...">...</a>
        $patSpec = '/<a\s+(?!.*class=)([^>]*href="[^"]*spec_sheets[^"]*"[^>]*)>(.*?)<\/a>/i';
        $patHigh = '/<a\s+(?!.*class=)([^>]*href="[^"]*high_res[^"]*"[^>]*)>(.*?)<\/a>/i';

        if (preg_match($patSpec, $content)) {
            $content = preg_replace($patSpec, '<a class="trade-button" $1>$2</a>', $content);
            $modified = true;
            echo " -> Spec Link Formatted.<br>";
        }

        if (preg_match($patHigh, $content)) {
            $content = preg_replace($patHigh, '<a class="trade-button" $1>$2</a>', $content);
            $modified = true;
            echo " -> HighRes Link Formatted.<br>";
        }

        // 3. Inject CSS
        if (strpos($content, '.trade-button') === false) {
            $css = "<style>.trade-button { display: inline-block; padding: 12px 24px; background-color: #000; color: #fff !important; text-decoration: none; text-transform: uppercase; font-size: 11px; letter-spacing: 1px; margin-top: 10px; margin-right: 10px; border: 1px solid #000; transition: all 0.3s ease; font-family: 'Inter', sans-serif; font-weight: 500; } .trade-button:hover { background-color: #fff; color: #000 !important; }</style>";
            $content .= $css; // Append to end
            $modified = true;
            echo " -> Button CSS Injected.<br>";
        }

        if ($modified) {
            // SQL Update to avoid any WP filter stripping
            $wpdb->update($wpdb->posts, ['post_content' => $content], ['ID' => $id]);
            echo "✅ Saved DB Update for ID $id.<br>";

            // Clear Cache
            if (function_exists('w3tc_flush_all'))
                w3tc_flush_all();
            if (function_exists('wp_cache_flush'))
                wp_cache_flush();
        } else {
            echo "No changes needed.<br>";
        }
    }
} else {
    echo "Work Party page not found via SQL.";
}
?>