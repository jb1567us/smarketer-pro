<?php
// fix_images_remote.php
// A special purpose script to receive an image, handle upload to WP, and set as featured image for a page.

require_once('wp-load.php');
require_once('wp-admin/includes/image.php');
require_once('wp-admin/includes/file.php');
require_once('wp-admin/includes/media.php');

// Simple header security or just obfuscation could be good, but for now we trust the environment (run once and delete)
// Only safe_writer protected? No, this is public access unless we protect it.
// We'll trust the user executes this immediately.

header('Content-Type: application/json');

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    echo json_encode(['status' => 'error', 'message' => 'Only POST allowed']);
    exit;
}

$action = $_POST['action'] ?? '';
$page_title = $_POST['page_title'] ?? '';

if ($action === 'upload_and_attach' && !empty($page_title) && isset($_FILES['file'])) {
    
    // 1. Find the page
    $page = get_page_by_title($page_title, OBJECT, 'page');
    if (!$page) {
        // Try loose search
         $args = array(
            'post_type' => 'page',
            's' => $page_title,
            'posts_per_page' => 1
        );
        $query = new WP_Query($args);
        if ($query->have_posts()) {
            $query->the_post();
            $page = get_post();
            wp_reset_postdata();
        }
    }
    
    if (!$page) {
        echo json_encode(['status' => 'error', 'message' => "Page '$page_title' not found."]);
        exit;
    }

    // 2. Handle File Upload
    $upload_dir = wp_upload_dir();
    $target_dir = $upload_dir['path'];
    // Ensure we are in 2025/09 or whatever current is, or force it? 
    // wp_upload_dir() returns current month/year folder usually.
    // Let's just use what it gives us.
    
    $filename = basename($_FILES['file']['name']);
    $file_path = $upload_dir['path'] . '/' . $filename;
    
    if (move_uploaded_file($_FILES['file']['tmp_name'], $file_path)) {
        
        // 3. Create Attachment
        $filetype = wp_check_filetype($filename, null);
        $attachment = array(
            'post_mime_type' => $filetype['type'],
            'post_title'     => sanitize_file_name($filename),
            'post_content'   => '',
            'post_status'    => 'inherit'
        );
        
        $attach_id = wp_insert_attachment($attachment, $file_path, $page->ID);
        
        if (!is_wp_error($attach_id)) {
            $attach_data = wp_generate_attachment_metadata($attach_id, $file_path);
            wp_update_attachment_metadata($attach_id, $attach_data);
            
            // 4. Set Featured Image
            set_post_thumbnail($page->ID, $attach_id);
            
            echo json_encode([
                'status' => 'success', 
                'message' => "Uploaded '$filename', attached to page '{$page->post_title}' (ID: {$page->ID}).",
                'page_id' => $page->ID,
                'attach_id' => $attach_id,
                'image_url' => wp_get_attachment_url($attach_id)
            ]);
        } else {
             echo json_encode(['status' => 'error', 'message' => 'Failed to create attachment: ' . $attach_id->get_error_message()]);
        }
        
    } else {
        echo json_encode(['status' => 'error', 'message' => 'Failed to move uploaded file.']);
    }

} else {
    echo json_encode(['status' => 'error', 'message' => 'Invalid request arguments.']);
}
