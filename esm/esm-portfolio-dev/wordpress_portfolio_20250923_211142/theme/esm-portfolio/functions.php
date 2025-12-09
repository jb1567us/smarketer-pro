<?php
/**
 * ESM Portfolio functions and definitions
 */

if (!defined('ABSPATH')) {
    exit; // Exit if accessed directly
}

// Theme setup
function esm_portfolio_setup() {
    add_theme_support('title-tag');
    add_theme_support('post-thumbnails');
    add_theme_support('html5', array(
        'search-form',
        'comment-form',
        'comment-list',
        'gallery',
        'caption',
    ));
    
    // Register navigation menus
    register_nav_menus(array(
        'primary' => __('Primary Menu', 'esm-portfolio'),
    ));
    
    // Add image sizes
    add_image_size('artwork-thumbnail', 400, 300, true);
}
add_action('after_setup_theme', 'esm_portfolio_setup');

// Enqueue styles and scripts
function esm_portfolio_scripts() {
    wp_enqueue_style('esm-portfolio-style', get_stylesheet_uri());
}
add_action('wp_enqueue_scripts', 'esm_portfolio_scripts');

// Custom menu walker for simple navigation
class ESM_Menu_Walker extends Walker_Nav_Menu {
    public function start_l(&$output, $item, $depth = 0, $args = array(), $id = 0) {
        $output .= '<li class="menu-item"><a href="' . $item->url . '">' . $item->title . '</a>';
    }
    
    public function end_l(&$output, $item, $depth = 0, $args = array()) {
        $output .= '</li>';
    }
}
?>
