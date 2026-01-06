<?php
if ( ! defined( 'ABSPATH' ) ) { exit; }

define( 'TTP_THEME_VERSION', '1.0.1' );
define( 'TTP_THEME_DIR', get_template_directory() );
define( 'TTP_THEME_URL', get_template_directory_uri() );

require_once TTP_THEME_DIR . '/inc/helpers.php';
require_once TTP_THEME_DIR . '/inc/cpt.php';
require_once TTP_THEME_DIR . '/inc/meta-boxes.php';
require_once TTP_THEME_DIR . '/inc/theme-settings.php';
require_once TTP_THEME_DIR . '/inc/schema.php';

function ttp_setup_theme() {
	add_theme_support( 'title-tag' );
	add_theme_support( 'post-thumbnails' );
	add_theme_support( 'html5', array( 'search-form', 'comment-form', 'comment-list', 'gallery', 'caption', 'style', 'script' ) );
	add_theme_support( 'responsive-embeds' );
	add_theme_support( 'align-wide' );
	add_theme_support( 'custom-logo', array( 'height' => 80, 'width' => 320, 'flex-height' => true, 'flex-width' => true ) );

	register_nav_menus( array(
		'primary' => __( 'Primary Menu', 'ttp' ),
		'footer'  => __( 'Footer Menu', 'ttp' ),
	) );

	add_image_size( 'ttp_puppy_card', 900, 700, true );
	add_image_size( 'ttp_happy_home', 900, 900, true );
}
add_action( 'after_setup_theme', 'ttp_setup_theme' );

function ttp_enqueue_assets() {
	wp_enqueue_style( 'ttp-main', TTP_THEME_URL . '/assets/css/main.css', array(), TTP_THEME_VERSION );
	wp_enqueue_script( 'ttp-main', TTP_THEME_URL . '/assets/js/main.js', array(), TTP_THEME_VERSION, true );
	wp_localize_script( 'ttp-main', 'TTP', array( 'ajaxUrl' => admin_url( 'admin-ajax.php' ) ) );
}
add_action( 'wp_enqueue_scripts', 'ttp_enqueue_assets' );

function ttp_body_class( $classes ) {
	$lead_mode = ttp_get_option( 'lead_mode', 'referral' );
	$classes[] = 'ttp-leadmode-' . sanitize_html_class( $lead_mode );
	return $classes;
}
add_filter( 'body_class', 'ttp_body_class' );
