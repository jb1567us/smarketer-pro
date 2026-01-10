<?php
// deploy_collections_refactor.php

// 1. Copy the new template file
$source = __DIR__ . '/esm-collection-template.php';
$dest = $_SERVER['DOCUMENT_ROOT'] . '/wp-content/plugins/esm-collection-template.php';
// Or just put it in mu-plugins or active theme? 
// The artwork template is likely in a similar place. 
// Let's assume user wants it in the root or same place as artwork template.
// Checking previous steps, the artwork template is `esm-artwork-template_NEW.php` in `c:\sandbox\esm`.
// It seems we deploy by copying to the server.

// Let's use the standard deployment method: upload file using copy.
// But we are running locally in `c:\sandbox\esm`. 
// We need to simulate the deployment or just say we are "deploying" if this is a local env.
// Given the user context says "c:\sandbox\esm -> jb1567us/sandbox", this IS the environment.
// So I don't need to move files if the server is running from here.
// But usually there is a deploy step.

// Let's create a script that ensures the new template is loaded.
// If it's a plugin, it needs to be activated or in mu-plugins.
// The artwork template has a header `Plugin Name: ESM Artwork Master Template`.
// This one has `Plugin Name: ESM Collection Template`.
// So it should be in `wp-content/plugins` and activated, OR `wp-content/mu-plugins`.

// Let's copy it to `wp-content/mu-plugins` to force load it, similar to how we might want it to always be active.
// OR we can just put it in the root and require it from `wp-config.php` or similar if that's how they do it.
// BUT, `regenerate_all_collections.php` loads `wp-load.php`.

// Strategy: Copy to `wp-content/mu-plugins/esm-collection-template.php` if mu-plugins exists.
// If not, maybe just `wp-content/plugins`.

if (!is_dir($_SERVER['DOCUMENT_ROOT'] . '/wp-content/mu-plugins')) {
    mkdir($_SERVER['DOCUMENT_ROOT'] . '/wp-content/mu-plugins', 0755, true);
}

$dest = $_SERVER['DOCUMENT_ROOT'] . '/wp-content/mu-plugins/esm-collection-template.php';
if (copy(__DIR__ . '/esm-collection-template.php', $dest)) {
    echo "Successfully deployed esm-collection-template.php to mu-plugins.\n";
} else {
    echo "Failed to deploy template.\n";
}

// Also run the regeneration script to update page content to placeholder
include __DIR__ . '/regenerate_all_collections.php';

?>
