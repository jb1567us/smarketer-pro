<?php
// fix_header_menu.php
// Programmatically create specific menu to stop the "Page List" madness

require_once($_SERVER['DOCUMENT_ROOT'] . '/wp-load.php');

$menu_name = 'Main Menu';
$menu_exists = wp_get_nav_menu_object($menu_name);

// 1. Delete if exists to start clean (User asked to "Recreate")
if ($menu_exists) {
    wp_delete_nav_menu($menu_name);
    echo "Deleted existing '$menu_name'<br>";
}

// 2. Create Menu
$menu_id = wp_create_nav_menu($menu_name);

if (is_wp_error($menu_id)) {
    die("❌ Error creating menu: " . $menu_id->get_error_message());
}
echo "✅ Created Menu '$menu_name' (ID: $menu_id)<br>";

// 3. Add Items

// Portfolio (Home)
wp_update_nav_menu_item($menu_id, 0, [
    'menu-item-title' => 'Portfolio',
    'menu-item-url' => home_url('/'),
    'menu-item-status' => 'publish',
    'menu-item-type' => 'custom',
]);
echo "Added 'Portfolio' link<br>";

// About
$about = get_page_by_path('about');
if ($about) {
    wp_update_nav_menu_item($menu_id, 0, [
        'menu-item-title' => 'About',
        'menu-item-object' => 'page',
        'menu-item-object-id' => $about->ID,
        'menu-item-type' => 'post_type',
        'menu-item-status' => 'publish',
    ]);
    echo "Added 'About' page<br>";
} else {
    echo "⚠️ 'About' page not found<br>";
}

// Contact
$contact = get_page_by_path('contact');
if ($contact) {
    wp_update_nav_menu_item($menu_id, 0, [
        'menu-item-title' => 'Contact',
        'menu-item-object' => 'page',
        'menu-item-object-id' => $contact->ID,
        'menu-item-type' => 'post_type',
        'menu-item-status' => 'publish',
    ]);
    echo "Added 'Contact' page<br>";
} else {
    echo "⚠️ 'Contact' page not found<br>";
}

// 4. Assign to Themes
// For FSE themes like TwentyTwentyFour, this part is tricky, but often they check 'primary'
$locations = get_theme_mod('nav_menu_locations');
$available = get_registered_nav_menus();

echo "<h3>Available Locations:</h3>";
print_r($available);

// Force assign to ALL locations just to be sure
$new_locs = [];
foreach ($available as $slug => $name) {
    $new_locs[$slug] = $menu_id;
}
// Also standard keys just in case
$new_locs['primary'] = $menu_id;
$new_locs['header'] = $menu_id;

set_theme_mod('nav_menu_locations', $new_locs);
echo "<h3>✅ Assigned locations</h3>";

echo "<a href='/fireworks/'>Check /fireworks/ (Should be clean now)</a>";
?>