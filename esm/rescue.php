<?php
/**
 * Plugin Name: Rescue Display
 * Description: Emergency fix to bypass block filters for blank pages.
 */

add_action('shutdown', function () {
    // Last ditch verification
});

add_filter('template_include', function ($template) {
    if (is_page('anemones') || is_single('anemones')) {
        echo "<h1 style='background:purple;color:white;padding:20px;z-index:9999;position:relative;'>TEMPLATE: $template</h1>";
    }
    return $template;
}, 9999);
?>