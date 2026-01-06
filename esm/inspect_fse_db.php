<?php
// inspect_fse_db.php
require_once($_SERVER['DOCUMENT_ROOT'] . '/wp-load.php');

echo "<h1>🕵️ FSE DB Inspector</h1>";

$types = ['wp_template', 'wp_template_part', 'wp_navigation'];

foreach ($types as $type) {
    echo "<h2>Type: $type</h2>";
    $query = new WP_Query([
        'post_type' => $type,
        'posts_per_page' => -1,
        'post_status' => 'any'
    ]);

    if ($query->have_posts()) {
        echo "<table border='1' cellpadding='5'><tr><th>ID</th><th>Title</th><th>Slug</th><th>Theme (Tax check)</th><th>Area (Tax check)</th></tr>";
        while ($query->have_posts()) {
            $query->the_post();
            $id = get_the_ID();

            // Get wp_theme terms
            $themes = wp_get_post_terms($id, 'wp_theme', ['fields' => 'names']);
            $theme_str = implode(', ', $themes);

            // Get wp_template_part_area
            $areas = wp_get_post_terms($id, 'wp_template_part_area', ['fields' => 'names']);
            $area_str = implode(', ', $areas);

            echo "<tr>";
            echo "<td>$id</td>";
            echo "<td>" . get_the_title() . "</td>";
            echo "<td>" . get_post_field('post_name', $id) . "</td>";
            echo "<td>" . ($theme_str ?: '❌ NONE') . "</td>";
            echo "<td>" . ($area_str ?: '-') . "</td>";
            echo "</tr>";
        }
        echo "</table>";
    } else {
        echo "No posts found for $type.<br>";
    }
}
?>