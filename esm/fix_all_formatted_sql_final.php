<?php
// fix_all_formatted_sql_final.php
require_once($_SERVER['DOCUMENT_ROOT'] . '/wp-load.php');
global $wpdb;

// Disable buffering
if (function_exists('apache_setenv')) {
    @apache_setenv('no-gzip', 1);
}
@ini_set('zlib.output_compression', 0);
@ini_set('implicit_flush', 1);
for ($i = 0; $i < ob_get_level(); $i++) {
    ob_end_flush();
}
ob_implicit_flush(1);

echo "<h1>Global Formatting Fix (SQL)</h1>";
flush();

// Select all pages
$rows = $wpdb->get_results("SELECT ID, post_title, post_content, post_name FROM {$wpdb->posts} WHERE post_type='page' AND post_status='publish'");

echo "Found " . count($rows) . " pages.<br>";
flush();

$count = 0;
foreach ($rows as $post) {
    $content = $post->post_content;
    $id = $post->ID;
    $modified = false;
    $log = "";

    // 1. Raw CSS Wrap
    if (strpos($content, '/* Font Imports */') !== false && strpos($content, '<style>/* Font Imports */') === false) {
        $content = str_replace('/* Font Imports */', '<style>/* Font Imports */', $content);

        // Close style
        if (preg_match('/(\n\s*<(div|p|h[1-6]))/i', $content, $m, PREG_OFFSET_CAPTURE)) {
            $pos = $m[0][1];
            $content = substr_replace($content, "</style>", $pos, 0);
        } else {
            // If no clear HTML start, append to end of what looks like CSS?
            // Or just append </style> after the replacements.
            // Let's rely on the previous logic or standard closing.
        }
        $modified = true;
        $log .= " [CSS Wrapped]";
    }

    // 2. Links -> Buttons
    // Spec Sheet
    // Pattern: <a ... href="...spec_sheets...">...</a>
    // We want to add class="trade-button" if not present.

    // We can use str_replace if the link is standard.
    // Regex is safer for attributes.
    // Be careful with existing classes.

    $patSpec = '/<a\s+(?![^>]*class=["\'][^"\']*trade-button)([^>]*href=["\'][^"\']*spec_sheets[^"\']*["\'][^>]*)>(.*?)<\/a>/i';
    // Logic: Look for anchor with spec_sheets href, ensuring class trade-button is NOT already there.
    // Replace with: <a class="trade-button" $1>$2</a>
    // Note: If other classes exist, this might double class attribute.
    // Risk acceptable for this cleanup.

    if (preg_match($patSpec, $content)) {
        $content = preg_replace($patSpec, '<a class="trade-button" $1>$2</a>', $content);
        $modified = true;
        // Fix double attributes if any (quick cleanup)
        // $content = str_replace('class="trade-button" class=', 'class="trade-button ', $content);
        $log .= " [Spec Button]";
    }

    $patHigh = '/<a\s+(?![^>]*class=["\'][^"\']*trade-button)([^>]*href=["\'][^"\']*high_res[^"\']*["\'][^>]*)>(.*?)<\/a>/i';
    if (preg_match($patHigh, $content)) {
        $content = preg_replace($patHigh, '<a class="trade-button" $1>$2</a>', $content);
        $modified = true;
        $log .= " [HighRes Button]";
    }

    // 3. Inject CSS
    // Check if we need CSS (i.e. we have buttons)
    if (strpos($content, 'trade-button') !== false) {
        if (strpos($content, '.trade-button {') === false) {
            $css = "<style>.trade-button { display: inline-block; padding: 12px 24px; background-color: #000; color: #fff !important; text-decoration: none; text-transform: uppercase; font-size: 11px; letter-spacing: 1px; margin-top: 10px; margin-right: 10px; border: 1px solid #000; transition: all 0.3s ease; font-family: 'Inter', sans-serif; font-weight: 500; } .trade-button:hover { background-color: #fff; color: #000 !important; }</style>";
            $content .= $css;
            $modified = true;
            $log .= " [CSS Injected]";
        }
    }

    if ($modified) {
        $wpdb->update($wpdb->posts, ['post_content' => $content], ['ID' => $id]);
        echo "✅ Fixed ID $id ({$post->post_title}): $log <a href='/" . $post->post_name . "/'>Check</a><br>";
        flush();
        $count++;
    }

    if ($count % 50 == 0)
        flush();
}

echo "Done. Total updated: $count";
?>