<?php
if ( ! defined( 'ABSPATH' ) ) { exit; }

function ttp_schema_json( $data ) {
	return wp_json_encode( $data, JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE );
}

function ttp_output_schema() {
	$business_name = ttp_get_option( 'business_name', get_bloginfo( 'name' ) );
	$phone = ttp_get_option( 'phone', '' );
	$email = ttp_get_option( 'email', '' );
	$addr1 = ttp_get_option( 'address_line1', '' );
	$city = ttp_get_option( 'address_city', '' );
	$state = ttp_get_option( 'address_state', '' );
	$zip = ttp_get_option( 'address_zip', '' );

	if ( is_front_page() ) {
		$schema = array(
			'@context' => 'https://schema.org',
			'@type' => 'LocalBusiness',
			'name' => $business_name,
			'url' => home_url( '/' ),
		);
		if ( $phone ) { $schema['telephone'] = $phone; }
		if ( $email ) { $schema['email'] = $email; }
		if ( $addr1 || $city || $state || $zip ) {
			$schema['address'] = array(
				'@type' => 'PostalAddress',
				'streetAddress' => $addr1,
				'addressLocality' => $city,
				'addressRegion' => $state,
				'postalCode' => $zip,
				'addressCountry' => 'US',
			);
		}
		echo "\n<script type=\"application/ld+json\">" . ttp_schema_json( $schema ) . "</script>\n";
	}

	if ( is_singular( 'ttp_puppy' ) ) {
		$post_id = get_the_ID();
		$meta = ttp_get_puppy_meta( $post_id );
		$img = get_the_post_thumbnail_url( $post_id, 'large' );
		$desc = wp_strip_all_tags( get_the_excerpt( $post_id ) ?: get_the_content( null, false, $post_id ) );
		$price_raw = (string) ( $meta['price'] ?? '' );
		$price_num = '';
		if ( preg_match( '/([0-9][0-9,\.]+)/', $price_raw, $m ) ) {
			$price_num = str_replace( ',', '', $m[1] );
		}

		$product = array(
			'@context' => 'https://schema.org',
			'@type' => 'Product',
			'name' => get_the_title( $post_id ),
			'image' => $img ? array( $img ) : array(),
			'description' => $desc,
			'brand' => array( '@type' => 'Brand', 'name' => $business_name ),
		);
		if ( $price_num ) {
			$product['offers'] = array(
				'@type' => 'Offer',
				'priceCurrency' => 'USD',
				'price' => $price_num,
				'availability' => ( 'available' === ( $meta['status'] ?? '' ) ) ? 'https://schema.org/InStock' : 'https://schema.org/OutOfStock',
				'url' => get_permalink( $post_id ),
			);
		}
		echo "\n<script type=\"application/ld+json\">" . ttp_schema_json( $product ) . "</script>\n";
	}
}
add_action( 'wp_head', 'ttp_output_schema', 20 );
