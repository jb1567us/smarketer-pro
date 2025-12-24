<?php
ini_set('display_errors', 1);
error_reporting(E_ALL);

include('wp-config.php');

global $wpdb;

$json_file = 'wp-content/mu-plugins/artwork_data.json';
$data = json_decode(file_get_contents($json_file), true);

echo "<h1>Fixing Slugs</h1>";

$updates = [
    'Caviar' => 'caviarpainting',
    'Dog on a bike Painting' => 'dog_on_a_bikepainting',
    'Bold Painting' => 'boldpainting-4',
    'Dance Painting' => 'dancepainting',
    'Microscope 7 Painting' => 'microscope_7painting-4',
    'Microscope 6 Painting' => 'microscope_6painting-4',
    'Microscope 5 Painting' => 'microscope_5painting-4',
    'Microscope 4 Painting' => 'microscope_4painting-4',
    'Microscope 3 Painting' => 'microscope_3painting-4',
    'Microscope 2 Painting' => 'microscope_2painting-4',
    'Microscope 1 Painting' => 'microscope_1painting-4',
    'Honeycomb - Mulch Series Collage' => 'honeycomb_-_mulch_seriesCollage',
    'Wild Zebra 2 - Mulch Series Collage' => 'wild_zebra_2_-_mulch_seriesCollage',
    'Wild Zebra 1 - Mulch Series Collage' => 'wild_zebra_1_-_mulch_seriesCollage',
    'Work Party - Mulch Series Collage' => 'work_party_-_mulch_seriesCollage',
    'Purple Night - Mulch Series Collage' => 'purple_night_-_mulch_seriesCollage',
    'Purple 1 - Mulch Series Collage' => 'purple_1_-_mulch_seriesCollage',
    'Society - Mulch Series Collage' => 'society_-_mulch_seriesCollage',
    'Floating 6 - Rabbit Sculpture' => 'floating_6_-_rabbitSculpture',
    'Floating 5 - Moth Sculpture' => 'floating_5_-_mothSculpture',
    'Floating 4 - Vines Sculpture' => 'floating_4_-_vinesSculpture',
    'Floating 3 - Tree Sculpture' => 'floating_3_-_treeSculpture',
    'Floating 2 - Butterfly Sculpture' => 'floating_2_-_butterflySculpture',
    'Floating 1 - Cicada Sculpture' => 'floating_1_-_cicadaSculpture'
];

foreach ($updates as $title => $target_slug) {
    // Find page by title
    $page = $wpdb->get_row($wpdb->prepare("SELECT ID, post_name FROM $wpdb->posts WHERE post_title = %s AND post_type = 'page'", $title));
    
    if (!$page) {
         $clean_title = str_replace(' Painting', '', $title);
         $page = $wpdb->get_row($wpdb->prepare("SELECT ID, post_name FROM $wpdb->posts WHERE post_title = %s AND post_type = 'page'", $clean_title));
    }

    if ($page) {
        if ($page->post_name !== $target_slug) {
            // Update
            // Force lowercase for standard WP behavior compliance unless we really want mixed case
            // But wait, if JSON has mixed case, we might need mixed case for exact match if checking string?
            // Actually WP treats post_name as unique key.
            // Let's try setting it exactly as JSON to be safe, even if WP likes lwrcase.
            
            // Check for collision
            $exists = $wpdb->get_var($wpdb->prepare("SELECT ID FROM $wpdb->posts WHERE post_name = %s AND ID != %d", $target_slug, $page->ID));
            if ($exists) {
                echo "⚠️ Collision for <b>$target_slug</b> (ID $exists). Skipping.<br>";
                continue;
            }

            $wpdb->update($wpdb->posts, ['post_name' => $target_slug], ['ID' => $page->ID]);
            echo "✅ Updated <b>$title</b>: $page->post_name -> $target_slug<br>";
        } else {
            echo "ℹ️ Already correct: <b>$title</b><br>";
        }
    } else {
        echo "❌ Page not found: <b>$title</b><br>";
    }
}
?>
