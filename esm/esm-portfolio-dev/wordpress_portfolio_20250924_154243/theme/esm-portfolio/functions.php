<?php
/**
 * ESM Portfolio functions and definitions
 */

if (!defined('ABSPATH')) {
    exit;
}

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
    add_image_size('artwork-large', 1200, 800, false);
}
add_action('after_setup_theme', 'esm_portfolio_setup');

function esm_portfolio_scripts() {
    wp_enqueue_style('esm-portfolio-style', get_stylesheet_uri());
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

// Fallback menu that displays categories if no menu is set
function esm_portfolio_fallback_menu() {
    echo '<ul class="main-menu">';
    echo '<li><a href="' . home_url() . '">Home</a></li>';
    
    // Get all categories
    $categories = get_categories(array(
        'hide_empty' => true,
        'orderby' => 'name',
        'order' => 'ASC'
    ));
    
    foreach ($categories as $category) {
        echo '<li><a href="' . get_category_link($category->term_id) . '">' . $category->name . '</a></li>';
    }
    
    // Static pages
    echo '<li><a href="' . home_url('/about') . '">About</a></li>';
    echo '<li><a href="' . home_url('/contact') . '">Contact</a></li>';
    echo '</ul>';
}

// Auto-create navigation menu on theme activation
function esm_portfolio_create_initial_menu() {
    // Check if the menu exists
    $menu_name = 'Primary Menu';
    $menu_exists = wp_get_nav_menu_object($menu_name);
    
    // If it doesn't exist, let's create it
    if (!$menu_exists) {
        $menu_id = wp_create_nav_menu($menu_name);
        
        // Set up default menu items
        wp_update_nav_menu_item($menu_id, 0, array(
            'menu-item-title' => __('Home'),
            'menu-item-url' => home_url('/'),
            'menu-item-status' => 'publish'
        ));
        
        // Add categories as menu items
        $categories = get_categories(array('hide_empty' => true));
        foreach ($categories as $category) {
            wp_update_nav_menu_item($menu_id, 0, array(
                'menu-item-title' => $category->name,
                'menu-item-url' => get_category_link($category->term_id),
                'menu-item-status' => 'publish'
            ));
        }
        
        // Add About page
        $about_page = get_page_by_path('about');
        if ($about_page) {
            wp_update_nav_menu_item($menu_id, 0, array(
                'menu-item-title' => __('About'),
                'menu-item-object-id' => $about_page->ID,
                'menu-item-object' => 'page',
                'menu-item-type' => 'post_type',
                'menu-item-status' => 'publish'
            ));
        }
        
        // Add Contact page
        $contact_page = get_page_by_path('contact');
        if ($contact_page) {
            wp_update_nav_menu_item($menu_id, 0, array(
                'menu-item-title' => __('Contact'),
                'menu-item-object-id' => $contact_page->ID,
                'menu-item-object' => 'page',
                'menu-item-type' => 'post_type',
                'menu-item-status' => 'publish'
            ));
        }
        
        // Set the menu location
        $locations = get_theme_mod('nav_menu_locations');
        $locations['primary'] = $menu_id;
        set_theme_mod('nav_menu_locations', $locations);
    }
}
add_action('after_switch_theme', 'esm_portfolio_create_initial_menu');
?>
