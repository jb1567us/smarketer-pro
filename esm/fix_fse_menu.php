<?php
// fix_fse_menu.php
// Create a wp_navigation POST for FSE themes

require_once($_SERVER['DOCUMENT_ROOT'] . '/wp-load.php');

echo "<h1>🛠️ FSE Menu Creator</h1>";

// 1. Get Page Data
$about = get_page_by_path('about');
$contact = get_page_by_path('contact');

$about_id = $about ? $about->ID : 0;
$contact_id = $contact ? $contact->ID : 0;

echo "About ID: $about_id | Contact ID: $contact_id<br>";

// 2. Build Block Content
// Portfolio (Home)
$content = '<!-- wp:navigation-link {"label":"Portfolio","url":"/","kind":"custom","isTopLevelLink":true} /-->';

// About
if ($about_id) {
    $content .= sprintf(
        '<!-- wp:navigation-link {"label":"About","type":"page","id":%d,"url":"%s","kind":"post-type","isTopLevelLink":true} /-->',
        $about_id,
        get_permalink($about_id)
    );
}

// Contact
if ($contact_id) {
    $content .= sprintf(
        '<!-- wp:navigation-link {"label":"Contact","type":"page","id":%d,"url":"%s","kind":"post-type","isTopLevelLink":true} /-->',
        $contact_id,
        get_permalink($contact_id)
    );
}

echo "<h3>Block Content:</h3><pre>" . htmlspecialchars($content) . "</pre>";

// 3. Insert wp_navigation Post
$post_arr = [
    'post_title' => 'Main Navigation',
    'post_content' => $content,
    'post_status' => 'publish',
    'post_type' => 'wp_navigation',
    'post_name' => 'main-navigation', // slug
];

// Check if already exists to update
$existing = get_page_by_path('main-navigation', OBJECT, 'wp_navigation');
if ($existing) {
    $post_arr['ID'] = $existing->ID;
    $id = wp_update_post($post_arr);
    echo "✅ Updated existing Navigation Post (ID: $id)<br>";
} else {
    $id = wp_insert_post($post_arr);
    echo "✅ Inserted NEW Navigation Post (ID: $id)<br>";
}

if (is_wp_error($id)) {
    echo "❌ Error: " . $id->get_error_message();
} else {
    // 4. Try to force this menu (Experimental)
    // FSE themes generally pick the most recent, but sometimes mapping is needed.
    echo "Navigation Post Created/Updated.<br>";
}

echo "<a href='/fireworks/'>Check /fireworks/</a>";
?>