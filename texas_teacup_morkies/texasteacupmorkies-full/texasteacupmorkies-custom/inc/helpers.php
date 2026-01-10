<?php
if ( ! defined( 'ABSPATH' ) ) { exit; }

function ttp_get_option( $key, $default = '' ) {
	$options = get_option( 'ttp_theme_options', array() );
	if ( is_array( $options ) && array_key_exists( $key, $options ) ) {
		return $options[ $key ];
	}
	return $default;
}

function ttp_format_phone_href( $phone ) {
	$digits = preg_replace( '/[^0-9\+]/', '', (string) $phone );
	return $digits ? 'tel:' . $digits : '';
}

function ttp_format_sms_href( $phone ) {
	$digits = preg_replace( '/[^0-9\+]/', '', (string) $phone );
	return $digits ? 'sms:' . $digits : '';
}

function ttp_get_available_puppy_id() {
	$featured = absint( ttp_get_option( 'featured_puppy_id', 0 ) );
	if ( $featured ) {
		$status = get_post_meta( $featured, '_ttp_status', true );
		if ( 'available' === $status && 'ttp_puppy' === get_post_type( $featured ) ) {
			return $featured;
		}
	}

	$q = new WP_Query( array(
		'post_type'      => 'ttp_puppy',
		'posts_per_page' => 1,
		'orderby'        => 'date',
		'order'          => 'DESC',
		'meta_key'       => '_ttp_status',
		'meta_value'     => 'available',
		'no_found_rows'  => true,
	) );
	if ( $q->have_posts() ) {
		return (int) $q->posts[0]->ID;
	}
	return 0;
}

function ttp_get_puppy_meta( $post_id ) {
	$meta = array(
		'status'      => get_post_meta( $post_id, '_ttp_status', true ),
		'price'       => get_post_meta( $post_id, '_ttp_price', true ),
		'dob'         => get_post_meta( $post_id, '_ttp_dob', true ),
		'ready_date'  => get_post_meta( $post_id, '_ttp_ready_date', true ),
		'est_weight'  => get_post_meta( $post_id, '_ttp_est_weight', true ),
		'gender'      => get_post_meta( $post_id, '_ttp_gender', true ),
		'color_coat'  => get_post_meta( $post_id, '_ttp_color_coat', true ),
		'video_url'   => get_post_meta( $post_id, '_ttp_video_url', true ),
		'temperament' => get_post_meta( $post_id, '_ttp_temperament', true ),
		'training'    => get_post_meta( $post_id, '_ttp_training', true ),
	);
	$terms = get_the_terms( $post_id, 'ttp_breed' );
	if ( $terms && ! is_wp_error( $terms ) ) {
		$meta['breed'] = $terms[0]->name;
	} else {
		$meta['breed'] = '';
	}
	return $meta;
}

function ttp_badge_label( $status ) {
	$status = strtolower( (string) $status );
	if ( 'available' === $status ) return __( 'Available', 'ttp' );
	if ( 'reserved' === $status ) return __( 'Reserved', 'ttp' );
	if ( 'sold' === $status ) return __( 'Sold', 'ttp' );
	return __( 'Status', 'ttp' );
}

function ttp_escape_multiline_bullets( $text ) {
	$lines = preg_split( '/\r\n|\r|\n/', (string) $text );
	$lines = array_map( 'trim', $lines );
	$lines = array_filter( $lines, function($v){ return $v !== ''; } );
	return $lines;
}

function ttp_get_apply_url_for_puppy( $puppy_id = 0 ) {
	$apply_page_id = absint( ttp_get_option( 'apply_page_id', 0 ) );
	if ( $apply_page_id ) {
		$url = get_permalink( $apply_page_id );
		if ( $puppy_id ) {
			return add_query_arg( array( 'puppy' => $puppy_id ), $url );
		}
		return $url;
	}
	$form = trim( (string) ttp_get_option( 'waitlist_form_url', '' ) );
	if ( $form ) return $form;
	return home_url( '/' );
}
