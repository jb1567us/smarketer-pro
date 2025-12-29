<?php
// debug_missing_images.php
// JSON Report of Content
header('Content-Type: application/json');

require_once($_SERVER['DOCUMENT_ROOT'] . '/wp-load.php');

$results = check_type('page');
$results_posts = check_type('post');

$final = array_merge($results, $results_posts);

echo json_encode($final, JSON_PRETTY_PRINT);

function check_type($type) {
    $args = array(
        'post_type'      => $type,
        'posts_per_page' => -1,
        'post_status'    => 'publish',
    );

    $query = new WP_Query($args);
    $data = [];

    if ($query->have_posts()) {
        while ($query->have_posts()) {
            $query->the_post();
            $id = get_the_ID();
            $thumb_id = get_post_thumbnail_id($id);
            $img_url = wp_get_attachment_image_url($thumb_id, 'large');
            
            $status = 'OK';
            if (!$thumb_id) $status = 'NO_THUMB_ID';
            elseif (!$img_url) $status = 'NO_URL';
            
            $data[] = [
                'id' => $id,
                'type' => $type,
                'title' => get_the_title(),
                'status' => $status,
                'thumb_id' => $thumb_id,
                'url' => $img_url
            ];
        }
    }
    return $data;
}
?>
