<?php
/**
 * Plugin Name: Fix JSON Response Errors
 * Description: Fix common JSON response issues in WordPress REST API and admin-ajax
 * Version: 1.0.0
 * Author: System Generated
 */

// Prevent direct access
if (!defined('ABSPATH')) {
    exit;
}

class FixJSONResponse {
    
    public function __construct() {
        // Clean output buffers for REST API
        add_action('rest_api_init', array($this, 'clean_output_buffers'), 1);
        
        // Clean output buffers for admin-ajax
        add_action('admin_init', array($this, 'clean_output_buffers_ajax'), 1);
        add_action('wp_ajax_nopriv_clean_buffers', array($this, 'clean_output_buffers_ajax'), 1);
        
        // Fix content type headers
        add_filter('rest_pre_serve_request', array($this, 'fix_content_type'), 10, 4);
        
        // Remove extra whitespace and BOM
        add_action('init', array($this, 'remove_extra_whitespace'));
        
        // Disable mod_security for REST API if needed
        add_action('init', array($this, 'maybe_disable_mod_security'));
    }
    
    /**
     * Clean all output buffers for REST API requests
     */
    public function clean_output_buffers() {
        if (defined('REST_REQUEST') && REST_REQUEST) {
            $this->clean_all_buffers();
        }
    }
    
    /**
     * Clean output buffers for AJAX requests
     */
    public function clean_output_buffers_ajax() {
        if (defined('DOING_AJAX') && DOING_AJAX) {
            $this->clean_all_buffers();
        }
    }
    
    /**
     * Clean all output buffers
     */
    private function clean_all_buffers() {
        $levels = ob_get_level();
        for ($i = 0; $i < $levels; $i++) {
            ob_end_clean();
        }
    }
    
    /**
     * Fix content type headers for REST API
     */
    public function fix_content_type($served, $result, $request, $server) {
        // Ensure proper content type
        if (!headers_sent()) {
            header('Content-Type: application/json; charset=' . get_option('blog_charset'));
        }
        
        // Clean any extra output
        $this->clean_all_buffers();
        
        return $served;
    }
    
    /**
     * Remove extra whitespace that might break JSON
     */
    public function remove_extra_whitespace() {
        // Remove any whitespace at the start of output
        if (ob_get_length() > 0) {
            ob_clean();
        }
    }
    
    /**
     * Attempt to disable mod_security for REST API routes
     */
    public function maybe_disable_mod_security() {
        // Check if we're in a REST API request
        if (defined('REST_REQUEST') && REST_REQUEST) {
            // Try to disable mod_security if possible
            if (function_exists('apache_setenv')) {
                @apache_setenv('mod_security', 'Off');
            }
            
            // Set environment variable
            @putenv('mod_security=Off');
        }
    }
}

new FixJSONResponse();

/**
 * Additional fixes that run early in the process
 */

// Fix for UTF-8 BOM issues
function fix_utf8_bom() {
    // Remove UTF-8 BOM if it exists
    if (ob_get_length() && substr(ob_get_contents(), 0, 3) == pack('CCC', 0xef, 0xbb, 0xbf)) {
        ob_clean();
    }
}
add_action('init', 'fix_utf8_bom', 1);

// Fix for plugins/themes that output whitespace
function prevent_early_output() {
    // Clean buffers very early
    if (ob_get_level() > 0) {
        ob_clean();
    }
}
add_action('plugins_loaded', 'prevent_early_output', 1);

// Fix for admin AJAX requests
function fix_admin_ajax() {
    if (defined('DOING_AJAX') && DOING_AJAX) {
        // Clean any existing output buffers
        while (ob_get_level()) {
            ob_end_clean();
        }
        
        // Start a fresh buffer
        ob_start();
    }
}
add_action('admin_init', 'fix_admin_ajax', 1);

// Fix for REST API authentication issues
function fix_rest_authentication($result) {
    // If there's already a result, return it
    if (!empty($result)) {
        return $result;
    }
    
    // Only clean buffers for REST requests
    if (defined('REST_REQUEST') && REST_REQUEST) {
        fix_utf8_bom();
    }
    
    return $result;
}
add_filter('rest_authentication_errors', 'fix_rest_authentication', 999);

// Emergency buffer cleaner for critical failures
function emergency_buffer_cleaner() {
    $content_type = headers_list();
    $is_json = false;
    
    foreach ($content_type as $header) {
        if (stripos($header, 'content-type: application/json') !== false) {
            $is_json = true;
            break;
        }
    }
    
    if ($is_json) {
        // Clean all buffers for JSON responses
        while (ob_get_level() > 0) {
            ob_end_clean();
        }
    }
}
add_action('shutdown', 'emergency_buffer_cleaner', 1);

// Fix for specific hosting environments
function hosting_specific_fixes() {
    // Cloudways specific fix
    if (isset($_SERVER['HTTP_X_FORWARDED_FOR'])) {
        @ini_set('output_buffering', 'Off');
    }
    
    // WP Engine specific fix
    if (defined('WPE_PLUGIN_DIR')) {
        @ini_set('output_buffering', 0);
    }
    
    // SiteGround specific fix
    if (strpos($_SERVER['SERVER_SOFTWARE'] ?? '', 'SiteGround') !== false) {
        @ini_set('output_buffering', 0);
    }
}
add_action('init', 'hosting_specific_fixes');