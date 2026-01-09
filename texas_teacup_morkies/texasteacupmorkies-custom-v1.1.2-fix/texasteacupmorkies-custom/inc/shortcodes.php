<?php
if ( ! defined( 'ABSPATH' ) ) { exit; }

/**
 * [ttp_lead_cta]
 */
function ttp_sc_lead_cta( $atts = array() ) {
	$atts = shortcode_atts( array(
		'class' => 'ttp-btn',
		'show_secondary' => 'true',
	), $atts, 'ttp_lead_cta' );

	$available_id = ttp_get_available_puppy_id();
	$lead_mode    = (string) ttp_get_option( 'lead_mode', 'referral' );

	$apply_id = absint( ttp_get_option( 'apply_page_id', 0 ) );
	$ref_id   = absint( ttp_get_option( 'referral_page_id', 0 ) );

	$waitlist_url = $apply_id ? get_permalink( $apply_id ) : home_url( '/apply/' );
	$referral_url = $ref_id ? get_permalink( $ref_id ) : home_url( '/referral-request/' );

	if ( $available_id ) {
		$primary_url = ttp_get_apply_url_for_puppy( $available_id );
		$primary_label = __( 'Apply for the Available Puppy', 'ttp' );
	} else {
		if ( 'waitlist' === $lead_mode ) {
			$primary_url = $waitlist_url;
			$primary_label = __( 'Join the Waitlist', 'ttp' );
		} else {
			$primary_url = $referral_url;
			$primary_label = __( 'Request a Referral', 'ttp' );
		}
	}

	$out  = '<div class="ttp-row">';
	$out .= '<a class="' . esc_attr( $atts['class'] ) . '" href="' . esc_url( $primary_url ) . '">' . esc_html( $primary_label ) . '</a>';

	if ( filter_var( $atts['show_secondary'], FILTER_VALIDATE_BOOLEAN ) ) {
		$phone = (string) ttp_get_option( 'phone', '' );
		if ( $phone ) {
			$out .= '<a class="ttp-btn ttp-btn--ghost" href="' . esc_url( ttp_format_sms_href( $phone ) ) . '">' . esc_html__( 'Text', 'ttp' ) . '</a>';
			$out .= '<a class="ttp-btn ttp-btn--ghost" href="' . esc_url( ttp_format_phone_href( $phone ) ) . '">' . esc_html__( 'Call', 'ttp' ) . '</a>';
		}
	}
	$out .= '</div>';
	return $out;
}
add_shortcode( 'ttp_lead_cta', 'ttp_sc_lead_cta' );

/**
 * [ttp_map_directions from="City, ST" to="3800 Manorwood Rd, Austin, TX 78723" height="420"]
 * Directions from origin to destination.
 */
function ttp_sc_map_directions( $atts = array() ) {
	$atts = shortcode_atts( array(
		'height' => '420',
		'from'   => '',
		'to'     => '',
	), $atts, 'ttp_map_directions' );

	$from = trim( (string) ( $atts['from'] ? $atts['from'] : ttp_get_option( 'locality_center', 'Austin, TX' ) ) );
	$to   = trim( (string) ( $atts['to'] ? $atts['to'] : ttp_get_option( 'pickup_address', '3800 Manorwood Rd, Austin, TX 78723' ) ) );

	$from_q = rawurlencode( $from );
	$to_q   = rawurlencode( $to );

	$src  = 'https://www.google.com/maps?output=embed&f=d&source=s_d&saddr=' . $from_q . '&daddr=' . $to_q;
	$link = 'https://www.google.com/maps/dir/?api=1&origin=' . $from_q . '&destination=' . $to_q . '&travelmode=driving';
	$height = max( 280, min( 900, (int) $atts['height'] ) );

	$out  = '<div class="ttp-embed ttp-embed--map">';
	$out .= '<iframe title="' . esc_attr__( 'Directions map', 'ttp' ) . '" loading="lazy" referrerpolicy="no-referrer-when-downgrade" src="' . esc_url( $src ) . '" height="' . esc_attr( $height ) . '"></iframe>';
	$out .= '</div>';
	$out .= '<p class="ttp-muted" style="margin-top:10px;"><a class="ttp-btn ttp-btn--ghost" href="' . esc_url( $link ) . '" target="_blank" rel="noopener">' . esc_html__( 'Open directions in Google Maps', 'ttp' ) . '</a></p>';
	return $out;
}
add_shortcode( 'ttp_map_directions', 'ttp_sc_map_directions' );
