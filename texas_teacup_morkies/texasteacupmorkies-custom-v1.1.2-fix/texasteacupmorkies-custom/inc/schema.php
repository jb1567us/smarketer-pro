<?php
if ( ! defined( 'ABSPATH' ) ) { exit; }

function ttp_output_basic_schema() {
	if ( is_admin() ) return;
	$address = (string) ttp_get_option( 'pickup_address', '3800 Manorwood Rd, Austin, TX 78723' );
	$phone   = (string) ttp_get_option( 'phone', '' );
	$data = array(
		'@context' => 'https://schema.org',
		'@type'    => 'LocalBusiness',
		'name'     => get_bloginfo( 'name' ),
		'url'      => home_url( '/' ),
		'telephone'=> $phone,
		'address'  => $address,
	);
	echo "\n" . '<script type="application/ld+json">' . wp_json_encode( $data ) . '</script>' . "\n";
}
add_action( 'wp_head', 'ttp_output_basic_schema', 50 );
