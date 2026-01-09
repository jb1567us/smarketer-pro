<?php
if ( ! defined( 'ABSPATH' ) ) { exit; }

function ttp_register_cpts_and_taxonomies() {
	register_taxonomy( 'ttp_breed', array( 'ttp_puppy', 'ttp_happy_home' ), array(
		'labels' => array(
			'name'          => __( 'Breeds', 'ttp' ),
			'singular_name' => __( 'Breed', 'ttp' ),
		),
		'public'       => true,
		'show_ui'      => true,
		'show_in_rest' => true,
		'hierarchical' => false,
		'rewrite'      => array( 'slug' => 'breed' ),
	) );

	register_post_type( 'ttp_puppy', array(
		'labels' => array(
			'name'          => __( 'Puppies', 'ttp' ),
			'singular_name' => __( 'Puppy', 'ttp' ),
			'add_new_item'  => __( 'Add New Puppy', 'ttp' ),
			'edit_item'     => __( 'Edit Puppy', 'ttp' ),
		),
		'public'             => true,
		'has_archive'        => true,
		'rewrite'            => array( 'slug' => 'available-puppies' ),
		'menu_icon'          => 'dashicons-pets',
		'supports'           => array( 'title', 'editor', 'thumbnail', 'excerpt' ),
		'show_in_rest'       => true,
		'show_in_nav_menus'  => true,
	) );

	register_post_type( 'ttp_happy_home', array(
		'labels' => array(
			'name'          => __( 'Happy Homes', 'ttp' ),
			'singular_name' => __( 'Happy Home', 'ttp' ),
			'add_new_item'  => __( 'Add Happy Home', 'ttp' ),
			'edit_item'     => __( 'Edit Happy Home', 'ttp' ),
		),
		'public'            => true,
		'has_archive'       => false,
		'rewrite'           => array( 'slug' => 'happy-homes' ),
		'menu_icon'         => 'dashicons-format-gallery',
		'supports'          => array( 'title', 'editor', 'thumbnail', 'excerpt' ),
		'show_in_rest'      => true,
		'show_in_nav_menus' => false,
	) );

	if ( ! term_exists( 'Maltipom', 'ttp_breed' ) ) { wp_insert_term( 'Maltipom', 'ttp_breed' ); }
	if ( ! term_exists( 'Morkie', 'ttp_breed' ) ) { wp_insert_term( 'Morkie', 'ttp_breed' ); }
}
add_action( 'init', 'ttp_register_cpts_and_taxonomies' );
