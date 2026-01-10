<?php
// fix_missing_images_v1.php
header("Content-Type: text/plain");
require_once($_SERVER['DOCUMENT_ROOT'] . '/wp-load.php');
require_once(ABSPATH . 'wp-admin/includes/image.php');

$page_id = 2256;
$image_url_suffix = '2025/11/In_the_DarkPainting.jpg';
$upload_dir = wp_upload_dir();
$file_path = $upload_dir['basedir'] . '/' . $image_url_suffix;

echo "Target Page: $page_id\n";
echo "Target File: $file_path\n";

if (!file_exists($file_path)) {
    die("ERROR: File not found at $file_path");
}

echo "File exists on disk.\n";

// Check if attachment already exists (double check)
global $wpdb;
$existing_id = $wpdb->get_var($wpdb->prepare("SELECT ID FROM $wpdb->posts WHERE guid LIKE %s", '%' . $image_url_suffix));

if ($existing_id) {
    echo "Found existing attachment ID: $existing_id\n";
    $attach_id = $existing_id;
} else {
    echo "Creating new attachment...\n";
    $filetype = wp_check_filetype(basename($file_path), null);
    $attachment = array(
        'guid'           => $upload_dir['baseurl'] . '/' . $image_url_suffix, 
        'post_mime_type' => $filetype['type'],
        'post_title'     => preg_replace('/\.[^.]+$/', '', basename($file_path)),
        'post_content'   => '',
        'post_status'    => 'inherit'
    );

    $attach_id = wp_insert_attachment($attachment, $file_path);
    $attach_data = wp_generate_attachment_metadata($attach_id, $file_path);
    wp_update_attachment_metadata($attach_id, $attach_data);
    echo "Created Attachment ID: $attach_id\n";
}

// Set Featured Image
$result = set_post_thumbnail($page_id, $attach_id);

if ($result) {
    echo "SUCCESS: Set featured image for Page $page_id to Attachment $attach_id\n";
} else {
    echo "FAILURE: Could not set featured image.\n";
}
?>
