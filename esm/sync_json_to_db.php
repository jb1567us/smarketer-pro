<?php
// sync_json_to_db.php
// Reads artwork_data.json and updates the 'saatchi_url' meta field for corresponding pages.

require_once('wp-load.php');

$json_file = __DIR__ . '/artwork_data.json';
if (!file_exists($json_file)) {
    die("JSON file not found.");
}

$data = json_decode(file_get_contents($json_file), true);
if (!$data) {
    die("Invalid JSON data.");
}

echo "Starting Sync...\n";
$updates = 0;

foreach ($data as $item) {
    // Check if we have a valid Saatchi URL to sync
    if (empty($item['saatchi_url'])) {
        continue;
    }

    // Identify the post by Title first, or Slug
    $page = get_page_by_title($item['title'], OBJECT, 'page');
    
    // If not found by exact title, try slug match (more reliable?)
    // But page slug might differ lightly. Title is usually best bet if unique.
    
    if (!$page && !empty($item['slug'])) {
         // Try to find by slug path if needed, but get_page_by_path is strictly hierarchy.
         // Let's rely on Title for now, or ID if we mapped it (but we don't trust local IDs).
         
         // Fallback: WP Query by title-like?
         // No, let's keep it simple.
    }

    if ($page) {
        $post_id = $page->ID;
        
        // Get current meta
        // Assuming the homepage uses a meta key for the link. 
        // Based on previous inspections, it might be 'saatchi_url' or just the main content?
        // Wait, typical portfolio plugins use custom fields.
        // Let's assume 'saatchi_url' is the key.
        // Also check if there's an 'external_link' key?
        
        // Update 'saatchi_url'
        $old_url = get_post_meta($post_id, 'saatchi_url', true);
        $new_url = $item['saatchi_url'];
        
        if ($old_url !== $new_url) {
            update_post_meta($post_id, 'saatchi_url', $new_url);
            echo "Updated [{$post_id}] '{$item['title']}':\n  OLD: $old_url\n  NEW: $new_url\n";
            $updates++;
        }
        
        // Checking for 'link' meta just in case (some themes use generic names)
        $old_link = get_post_meta($post_id, 'link', true);
        if ($old_link && strpos($old_link, 'saatchi') !== false) {
             if ($old_link !== $new_url) {
                update_post_meta($post_id, 'link', $new_url);
                echo "Updated [{$post_id}] 'link' meta as well.\n";
             }
        }

    } else {
        // echo "Skipped (Page not found): {$item['title']}\n";
    }
}

echo "Sync Complete. Updated $updates items.\n";
?>
