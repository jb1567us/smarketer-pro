<?php
/**
 * ESM Portfolio functions and definitions
 */

if (!defined('ABSPATH')) {
    exit;
}

function esm_portfolio_setup() {
    // Make theme available for translation
    load_theme_textdomain('esm-portfolio', get_template_directory() . '/languages');
    
    // Add default posts and comments RSS feed links to head
    add_theme_support('automatic-feed-links');
    
    // Let WordPress manage the document title
    add_theme_support('title-tag');
    
    // Enable support for Post Thumbnails
    add_theme_support('post-thumbnails');
    
    // HTML5 support
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
    add_image_size('artwork-large', 1200, 800, false);
}
add_action('after_setup_theme', 'esm_portfolio_setup');

function esm_portfolio_scripts() {
    // Enqueue styles
    wp_enqueue_style('esm-portfolio-style', get_stylesheet_uri());
    
    // Enqueue scripts
    wp_enqueue_script('esm-portfolio-script', get_template_directory_uri() . '/js/script.js', array(), '1.0.0', true);
}
add_action('wp_enqueue_scripts', 'esm_portfolio_scripts');

// Remove single post view - redirect to Saatchi Art
function esm_redirect_single_post() {
    if (is_single() && 'post' == get_post_type()) {
        $saatchi_url = get_post_meta(get_the_ID(), 'saatchi_url', true);
        if ($saatchi_url) {
            wp_redirect($saatchi_url, 301);
            exit;
        }
    }
}
add_action('template_redirect', 'esm_redirect_single_post');

// Simple menu fallback
function esm_portfolio_fallback_menu() {
    return '<ul><li><a href="' . home_url() . '">' . __('Home', 'esm-portfolio') . '</a></li><li><a href="' . home_url('/about') . '">' . __('About', 'esm-portfolio') . '</a></li><li><a href="' . home_url('/contact') . '">' . __('Contact', 'esm-portfolio') . '</a></li></ul>';
}

// Add body class for better styling
function esm_portfolio_body_classes($classes) {
    if (is_home() || is_archive()) {
        $classes[] = 'artwork-archive-page';
    }
    return $classes;
}
add_filter('body_class', 'esm_portfolio_body_classes');
?>