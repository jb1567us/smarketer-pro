<?php
require_once('wp-load.php');

// Enable detailed logging
ini_set('display_errors', 1);
error_reporting(E_ALL);

echo "<pre>Fixing Page Markup (Adding <style> and <script> tags)...<br>";

// Get all pages
$args = [
    'post_type' => 'page',
    'posts_per_page' => -1,
    'post_status' => 'publish',
];
$query = new WP_Query($args);

$count = 0;
$fixed_css = 0;
$fixed_json = 0;

foreach ($query->posts as $post) {
    $content = $post->post_content;
    $original_content = $content;
    $pid = $post->ID;

    // 1. Fix CSS
    // Check if it has Raw CSS but NO <style> tag around "Font Imports"
    if (strpos($content, '/* Font Imports */') !== false && strpos($content, '<style>/* Font Imports */') === false) {
        // Range: From "/* Font Imports */" to "<!-- VisualArtwork Schema -->"
        // Regex: Match the block, replace with <style>$0</style>
        // Note: The comment <!-- Premium Artwork Page Styles --> is before it.
        // Let's just wrap from Start of CSS to end of CSS.

        $pattern_css = '/(\/\* Font Imports \*\/.*?)\s*(?=<!-- VisualArtwork Schema -->)/s';
        if (preg_match($pattern_css, $content)) {
            $content = preg_replace($pattern_css, "<style>$1</style>", $content);
            $fixed_css++;
        }
    }

    // 2. Fix JSON Schema
    // Check if it has Schema but NO <script> tag
    if (strpos($content, '{ "@context"') !== false && strpos($content, '<script type="application/ld+json">{ "@context"') === false) {
        // Range: From '{ "@context"' to the closing brace before '<div'
        // The previous step might have shifted things.
        // Regex: look for the JSON block. It ends before <div class="artwork... or <div class="artwork-page-container"

        // Robust match: { "@context" ... } 
        // We can match balanced braces but PHP regex is tricky.
        // Simpler: Match until <div class="artwork-page-container">

        $pattern_json = '/(\{ "@context":.*?\})\s*(?=<div class="artwork-page-container">)/s';
        if (preg_match($pattern_json, $content)) {
            $content = preg_replace($pattern_json, '<script type="application/ld+json">$1</script>', $content);
            $fixed_json++;
        }
    }

    if ($content !== $original_content) {
        wp_update_post(['ID' => $pid, 'post_content' => $content]);
        echo "✅ Fixed Page $pid ({$post->post_title})<br>";
        $count++;
    }
}

echo "<br>Summary:<br>";
echo "Total Pages Scanned: " . count($query->posts) . "<br>";
echo "Pages Updated: $count<br>";
echo "CSS Fixes Applied: $fixed_css<br>";
echo "JSON Fixes Applied: $fixed_json<br>";
echo "</pre>";
?>