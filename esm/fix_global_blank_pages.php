<?php
// fix_global_blank_pages.php
require_once($_SERVER['DOCUMENT_ROOT'] . '/wp-load.php');
ini_set('max_execution_time', 300);
global $wpdb;

// Disable buffering to see real-time output
if (function_exists('apache_setenv')) {
    @apache_setenv('no-gzip', 1);
}
@ini_set('zlib.output_compression', 0);
@ini_set('implicit_flush', 1);
for ($i = 0; $i < ob_get_level(); $i++) {
    ob_end_flush();
}
ob_implicit_flush(1);

echo "<h1>Global Blank Page Rescue</h1>";

$rows = $wpdb->get_results("SELECT ID, post_title, post_content FROM {$wpdb->posts} WHERE post_type='page' AND post_status='publish'");

$count = 0;
foreach ($rows as $p) {
    if (in_array($p->post_title, ['Home', 'About', 'Contact', 'Trade']))
        continue;

    $content = $p->post_content;
    $modified = false;

    // Check for unbalanced style tags
    $open = substr_count($content, '<style>');
    $close = substr_count($content, '</style>');

    if ($open > $close) {
        echo "Processing ID {$p->ID} ({$p->post_title}): Unbalanced Styles ($open vs $close)... ";

        // Find the start of the <style> block
        $styleStart = strpos($content, '<style>');

        // Strategy: We need to close it before the HTML starts.
        // The HTML usually starts with <div class="artwork-page-container">
        // OR <h4 ...

        // Search for the first <div tag AFTER the style start
        $divPos = strpos($content, '<div', $styleStart);

        if ($divPos !== false) {
            // Check if there is already a </style> between styleStart and divPos?
            $checkChunk = substr($content, $styleStart, $divPos - $styleStart);
            if (strpos($checkChunk, '</style>') === false) {
                // IT IS MISSING!
                // Insert </style> before the <div
                $content = substr_replace($content, "</style>", $divPos, 0);
                $modified = true;
                echo " -> Closed before &lt;div&gt; at pos $divPos.<br>";
            } else {
                echo " -> Weird. </style> found before div, but count is off? Checking deeper.<br>";
                // Maybe multiple style blocks?
            }
        } else {
            // Fallback: If no div, look for <h
            if (preg_match('/<h[1-6]/', $content, $m, PREG_OFFSET_CAPTURE, $styleStart)) {
                $pos = $m[0][1];
                $content = substr_replace($content, "</style>", $pos, 0);
                $modified = true;
                echo " -> Closed before &lt;h*&gt;.<br>";
            } else {
                echo " ⚠️ Could not find safe place to close style tag.<br>";
            }
        }
    }

    // Also cleanup the corruption from earlier: class="trade-button" ... class="trade-link"
    if (preg_match('/class="trade-button"\s+([^>]*?)\s+class="trade-link"/i', $content)) {
        $content = preg_replace('/class="trade-button"\s+([^>]*?)\s+class="trade-link"/i', 'class="trade-button trade-link" $1', $content);
        $modified = true;
        echo " -> Merged double classes.<br>";
    }

    if ($modified) {
        $wpdb->update($wpdb->posts, ['post_content' => $content], ['ID' => $p->ID]);
        $count++;
        flush();
    }
}
echo "<h2>Done. Rescued $count pages.</h2>";
?>