<?php
if ( ! defined( 'ABSPATH' ) ) { exit; }

define( 'TTP_THEME_VERSION', '1.1.1' );
define( 'TTP_THEME_DIR', get_template_directory() );
define( 'TTP_THEME_URL', get_template_directory_uri() );

require_once TTP_THEME_DIR . '/inc/helpers.php';
require_once TTP_THEME_DIR . '/inc/cpt-puppy.php';
require_once TTP_THEME_DIR . '/inc/theme-settings.php';
require_once TTP_THEME_DIR . '/inc/shortcodes.php';
require_once TTP_THEME_DIR . '/inc/schema.php';
require_once TTP_THEME_DIR . '/inc/onboarding.php';

function ttp_setup_theme() {
	add_theme_support( 'title-tag' );
	add_theme_support( 'post-thumbnails' );
	add_theme_support( 'html5', array( 'search-form', 'comment-form', 'comment-list', 'gallery', 'caption', 'style', 'script' ) );
	add_theme_support( 'custom-logo', array( 'height' => 140, 'width' => 560, 'flex-height' => true, 'flex-width' => true ) );

	register_nav_menus( array(
		'primary' => __( 'Primary Menu', 'ttp' ),
		'footer'  => __( 'Footer Menu', 'ttp' ),
	) );
}
add_action( 'after_setup_theme', 'ttp_setup_theme' );

function ttp_enqueue_assets() {
	wp_enqueue_style( 'ttp-main', TTP_THEME_URL . '/assets/css/main.css', array(), TTP_THEME_VERSION );
	wp_enqueue_script( 'ttp-main', TTP_THEME_URL . '/assets/js/main.js', array(), TTP_THEME_VERSION, true );
}
add_action( 'wp_enqueue_scripts', 'ttp_enqueue_assets' );

function ttp_excerpt_fallback( $post_id, $fallback = '' ) {
	$ex = get_the_excerpt( $post_id );
	if ( $ex ) return $ex;
	$raw = wp_strip_all_tags( get_post_field( 'post_content', $post_id ) );
	$raw = trim( preg_replace( '/\s+/', ' ', $raw ) );
	if ( ! $raw ) return $fallback;
	return wp_trim_words( $raw, 22, '…' );
}
