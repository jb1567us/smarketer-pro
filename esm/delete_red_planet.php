<?php
ini_set('display_errors', 1);
error_reporting(E_ALL);

require_once($_SERVER['DOCUMENT_ROOT'] . '/wp-load.php');

echo "<h1>Red Planet Cleanup</h1>";

$title = "Red Planet";
$slug = "red_planet";
$found = false;

// 1. Delete Post by Title
$page = get_page_by_title($title, OBJECT, ['post', 'page', 'product']);
if ($page) {
    echo "Found Post by Title: " . $page->ID . " (" . $page->post_title . ")<br>";
    if (wp_delete_post($page->ID, true)) {
        echo "✅ Deleted Post (ID: " . $page->ID . ")<br>";
        $found = true;
    } else {
        echo "❌ Failed to delete post.<br>";
    }
} else {
    echo "Post not found by title '$title'. Checking slug...<br>";
}

// 2. Delete Post by Slug
if (!$found) {
    $args = [
        'name'        => $slug,
        'post_type'   => 'any',
        'post_status' => 'any',
        'numberposts' => 1
    ];
    $posts = get_posts($args);
    if ($posts) {
        $p = $posts[0];
        echo "Found Post by Slug: " . $p->ID . " (" . $p->post_title . ")<br>";
        if (wp_delete_post($p->ID, true)) {
            echo "✅ Deleted Post (ID: " . $p->ID . ")<br>";
        } else {
            echo "❌ Failed to delete post.<br>";
        }
    } else {
        echo "Post not found by slug '$slug'.<br>";
    }
}

// 3. Delete Related Files
$files_to_check = [
    $_SERVER['DOCUMENT_ROOT'] . '/downloads/spec_sheets/Red Planet_spec.pdf',
    $_SERVER['DOCUMENT_ROOT'] . '/downloads/spec_sheets/Red_Planet_spec.pdf',
    $_SERVER['DOCUMENT_ROOT'] . '/downloads/spec_sheets/Red Planet_Sheet.pdf',
    $_SERVER['DOCUMENT_ROOT'] . '/downloads/high_res/Red Planet_HighRes.zip',
    $_SERVER['DOCUMENT_ROOT'] . '/downloads/high_res/Red_Planet_HighRes.zip'
];

echo "<h2>File Cleanup</h2>";
foreach ($files_to_check as $file) {
    if (file_exists($file)) {
        if (unlink($file)) {
            echo "✅ Deleted file: $file<br>";
        } else {
            echo "❌ Failed to delete: $file<br>";
        }
    } else {
        echo "File not found: " . basename($file) . "<br>";
    }
}

echo "<h2>Done.</h2>";
?>
