<?php
require_once('wp-load.php');

echo "<pre>";
// 1. Verify Tags on a specific Page
// We know ID 1927 is 'Portal' (Page) from previous logs
$page_id = 1927;
echo "Checking Page ID $page_id (Portal)...\n";
$post = get_post($page_id);
echo "Type: " . $post->post_type . "\n";

$tags = get_the_tags($page_id);
echo "Tags on Page:\n";
if ($tags) {
    foreach ($tags as $t) {
        echo "- " . $t->name . " (ID: " . $t->term_id . ")\n";
    }
} else {
    echo "NONE FOUND.\n";
}

echo "\n------------------------------\n";

// 2. Simulate what happens when you click "Black" (or a known tag)
// using the filter we added ('post_type' => 'any')
$test_tag = 'Abstract';
echo "Simulating Tag Archive for '$test_tag':\n";

$query = new WP_Query(array(
    'tag' => $test_tag,
    'post_type' => 'any', // mirroring the functions.php change
    'posts_per_page' => 20
));

if ($query->have_posts()) {
    while ($query->have_posts()) {
        $query->the_post();
        $type = get_post_type();
        $icon = ($type == 'page') ? '✅' : '⚠️';
        echo "$icon [$type] " . get_the_title() . " (ID: " . get_the_ID() . ")\n";
    }
} else {
    echo "No results found for tag '$test_tag'.\n";
}
echo "</pre>";
?>