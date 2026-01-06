<?php
if ( ! defined( 'ABSPATH' ) ) { exit; }

function ttp_register_puppy_cpt() {
	register_post_type( 'ttp_puppy', array(
		'labels' => array(
			'name'          => __( 'Puppies', 'ttp' ),
			'singular_name' => __( 'Puppy', 'ttp' ),
			'add_new_item'  => __( 'Add New Puppy', 'ttp' ),
			'edit_item'     => __( 'Edit Puppy', 'ttp' ),
		),
		'public'       => true,
		'has_archive'  => 'available-puppies',
		'rewrite'      => array( 'slug' => 'puppies' ),
		'menu_icon'    => 'dashicons-pets',
		'supports'     => array( 'title', 'editor', 'thumbnail', 'excerpt' ),
		'show_in_rest' => true,
	) );

	register_taxonomy( 'ttp_breed', 'ttp_puppy', array(
		'labels' => array(
			'name'          => __( 'Breeds', 'ttp' ),
			'singular_name' => __( 'Breed', 'ttp' ),
		),
		'public'       => true,
		'hierarchical' => false,
		'rewrite'      => array( 'slug' => 'breed' ),
		'show_in_rest' => true,
	) );
}
add_action( 'init', 'ttp_register_puppy_cpt' );

function ttp_add_puppy_metaboxes() {
	add_meta_box( 'ttp_puppy_details', __( 'Puppy Details', 'ttp' ), 'ttp_render_puppy_metabox', 'ttp_puppy', 'normal', 'high' );
}
add_action( 'add_meta_boxes', 'ttp_add_puppy_metaboxes' );

function ttp_render_puppy_metabox( $post ) {
	wp_nonce_field( 'ttp_save_puppy', 'ttp_puppy_nonce' );

	$status = (string) get_post_meta( $post->ID, '_ttp_status', true );
	$price  = (string) get_post_meta( $post->ID, '_ttp_price', true );
	$sex    = (string) get_post_meta( $post->ID, '_ttp_sex', true );
	$color  = (string) get_post_meta( $post->ID, '_ttp_color', true );
	$gohome = (string) get_post_meta( $post->ID, '_ttp_go_home_date', true );
	if ( ! $status ) { $status = 'available'; }

	echo '<p><label><strong>Status</strong></label><br>';
	echo '<select name="ttp_status">';
	foreach ( array( 'available' => 'Available', 'reserved' => 'Reserved', 'sold' => 'Sold' ) as $k => $label ) {
		echo '<option value="' . esc_attr( $k ) . '"' . selected( $status, $k, false ) . '>' . esc_html( $label ) . '</option>';
	}
	echo '</select></p>';

	echo '<p><label><strong>Price</strong> (e.g. 2500)</label><br>';
	echo '<input type="text" name="ttp_price" value="' . esc_attr( $price ) . '" class="regular-text" /></p>';

	echo '<p><label><strong>Sex</strong> (optional)</label><br>';
	echo '<input type="text" name="ttp_sex" value="' . esc_attr( $sex ) . '" class="regular-text" placeholder="Female / Male" /></p>';

	echo '<p><label><strong>Color/Markings</strong> (optional)</label><br>';
	echo '<input type="text" name="ttp_color" value="' . esc_attr( $color ) . '" class="regular-text" /></p>';

	echo '<p><label><strong>Go-home date</strong> (optional)</label><br>';
	echo '<input type="date" name="ttp_go_home_date" value="' . esc_attr( $gohome ) . '" /></p>';

	echo '<p class="description">Tip: set the featured image — it powers the home “featured puppy” card.</p>';
}

function ttp_save_puppy_meta( $post_id ) {
	if ( ! isset( $_POST['ttp_puppy_nonce'] ) || ! wp_verify_nonce( $_POST['ttp_puppy_nonce'], 'ttp_save_puppy' ) ) return;
	if ( defined( 'DOING_AUTOSAVE' ) && DOING_AUTOSAVE ) return;
	if ( ! current_user_can( 'edit_post', $post_id ) ) return;

	$status = sanitize_text_field( isset($_POST['ttp_status']) ? $_POST['ttp_status'] : 'available' );
	if ( ! in_array( $status, array( 'available', 'reserved', 'sold' ), true ) ) { $status = 'available'; }

	$price  = sanitize_text_field( isset($_POST['ttp_price']) ? $_POST['ttp_price'] : '' );
	$sex    = sanitize_text_field( isset($_POST['ttp_sex']) ? $_POST['ttp_sex'] : '' );
	$color  = sanitize_text_field( isset($_POST['ttp_color']) ? $_POST['ttp_color'] : '' );
	$gohome = sanitize_text_field( isset($_POST['ttp_go_home_date']) ? $_POST['ttp_go_home_date'] : '' );

	update_post_meta( $post_id, '_ttp_status', $status );
	update_post_meta( $post_id, '_ttp_price', $price );
	update_post_meta( $post_id, '_ttp_sex', $sex );
	update_post_meta( $post_id, '_ttp_color', $color );
	update_post_meta( $post_id, '_ttp_go_home_date', $gohome );
}
add_action( 'save_post_ttp_puppy', 'ttp_save_puppy_meta' );
