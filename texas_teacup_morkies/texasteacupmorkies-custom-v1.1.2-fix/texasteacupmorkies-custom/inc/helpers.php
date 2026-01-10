<?php
if ( ! defined( 'ABSPATH' ) ) { exit; }

function ttp_get_option( $key, $default = '' ) {
	$opts = get_option( 'ttp_theme_options', array() );
	if ( ! is_array( $opts ) ) { $opts = array(); }
	return array_key_exists( $key, $opts ) ? $opts[ $key ] : $default;
}

function ttp_format_phone_href( $phone ) {
	$digits = preg_replace( '/[^0-9+]/', '', (string) $phone );
	return 'tel:' . $digits;
}

function ttp_format_sms_href( $phone ) {
	$digits = preg_replace( '/[^0-9+]/', '', (string) $phone );
	return 'sms:' . $digits;
}

function ttp_get_puppy_meta( $post_id, $key, $default = '' ) {
	$val = get_post_meta( $post_id, $key, true );
	return ( '' === $val || null === $val ) ? $default : $val;
}

function ttp_get_puppy_status( $post_id ) {
	$status = (string) ttp_get_puppy_meta( $post_id, '_ttp_status', 'available' );
	$status = strtolower( $status );
	if ( ! in_array( $status, array( 'available', 'reserved', 'sold' ), true ) ) {
		$status = 'available';
	}
	return $status;
}

function ttp_get_available_puppy_id() {
	$q = new WP_Query( array(
		'post_type'      => 'ttp_puppy',
		'posts_per_page' => 1,
		'meta_key'       => '_ttp_status',
		'meta_value'     => 'available',
		'orderby'        => 'date',
		'order'          => 'DESC',
		'no_found_rows'  => true,
	) );
	if ( $q->have_posts() ) { return (int) $q->posts[0]->ID; }
	return 0;
}

function ttp_get_apply_url_for_puppy( $puppy_id ) {
	$apply_page_id = absint( ttp_get_option( 'apply_page_id', 0 ) );
	if ( $apply_page_id ) {
		return add_query_arg( array( 'puppy_id' => (int) $puppy_id ), get_permalink( $apply_page_id ) );
	}
	return home_url( '/apply/' );
}

function ttp_badge_html( $status ) {
	$label = ucfirst( $status );
	$class = 'ttp-badge ttp-badge--' . esc_attr( $status );
	return '<span class="' . $class . '">' . esc_html( $label ) . '</span>';
}
