<?php
if ( ! defined( 'ABSPATH' ) ) { exit; }

function ttp_register_theme_settings() {
	register_setting( 'ttp_theme_options_group', 'ttp_theme_options', 'ttp_sanitize_theme_options' );

	add_settings_section( 'ttp_section_general', 'General', '__return_null', 'ttp_theme_options' );
	add_settings_section( 'ttp_section_leads', 'Leads', '__return_null', 'ttp_theme_options' );
	add_settings_section( 'ttp_section_local', 'Local / Map', '__return_null', 'ttp_theme_options' );

	$fields = array(
		'phone' => array( 'label' => 'Phone', 'type' => 'text', 'section' => 'ttp_section_general' ),
		'email' => array( 'label' => 'Email', 'type' => 'text', 'section' => 'ttp_section_general' ),
		'google_reviews_url' => array( 'label' => 'Google Reviews URL', 'type' => 'text', 'section' => 'ttp_section_general' ),
		'price_anchor' => array( 'label' => 'Price Anchor (e.g. $2,000+)', 'type' => 'text', 'section' => 'ttp_section_general' ),

		'lead_mode' => array(
			'label' => 'Lead Mode',
			'type' => 'select',
			'choices' => array(
				'referral' => 'Referral Request mode (between seasons)',
				'waitlist' => 'Apply / Waitlist mode (around breeding season)',
			),
			'section' => 'ttp_section_leads',
		),
		'waitlist_form_url' => array( 'label' => 'Waitlist Google Form URL', 'type' => 'text', 'section' => 'ttp_section_leads' ),
		'referral_form_url' => array( 'label' => 'Referral Request Form URL', 'type' => 'text', 'section' => 'ttp_section_leads' ),
		'commission_disclosure' => array( 'label' => 'Referral Commission Disclosure', 'type' => 'textarea', 'section' => 'ttp_section_leads' ),

		'pickup_address' => array( 'label' => 'Pickup Address (destination)', 'type' => 'text', 'section' => 'ttp_section_local' ),
		'locality_center' => array( 'label' => 'Default Locality Center (origin)', 'type' => 'text', 'section' => 'ttp_section_local' ),
	);

	foreach ( $fields as $key => $f ) {
		add_settings_field( $key, esc_html( $f['label'] ), 'ttp_render_theme_setting_field', 'ttp_theme_options', esc_attr( $f['section'] ), array( 'key' => $key, 'field' => $f ) );
	}
}
add_action( 'admin_init', 'ttp_register_theme_settings' );

function ttp_add_theme_options_page() {
	add_theme_page( 'TTP Theme Settings', 'TTP Settings', 'manage_options', 'ttp-theme-settings', 'ttp_render_theme_options_page' );
}
add_action( 'admin_menu', 'ttp_add_theme_options_page' );

function ttp_render_theme_options_page() {
	?>
	<div class="wrap">
		<h1>TTP Theme Settings</h1>
		<p>Tip: switch <strong>Lead Mode</strong> to <em>Waitlist</em> about ~40 days before birth (when you want to start taking leads). Keep it on <em>Referral</em> between seasons.</p>
		<form method="post" action="options.php">
			<?php
			settings_fields( 'ttp_theme_options_group' );
			do_settings_sections( 'ttp_theme_options' );
			submit_button();
			?>
		</form>
	</div>
	<?php
}

function ttp_render_theme_setting_field( $args ) {
	$key = $args['key'];
	$field = $args['field'];
	$opts = get_option( 'ttp_theme_options', array() );
	$val = is_array( $opts ) && isset( $opts[ $key ] ) ? $opts[ $key ] : '';

	$type = isset($field['type']) ? $field['type'] : 'text';

	if ( 'select' === $type ) {
		echo '<select name="ttp_theme_options[' . esc_attr( $key ) . ']">';
		foreach ( (array) ( isset($field['choices']) ? $field['choices'] : array() ) as $k => $label ) {
			echo '<option value="' . esc_attr( $k ) . '"' . selected( $val, $k, false ) . '>' . esc_html( $label ) . '</option>';
		}
		echo '</select>';
		return;
	}

	if ( 'textarea' === $type ) {
		echo '<textarea name="ttp_theme_options[' . esc_attr( $key ) . ']" rows="4" cols="60">' . esc_textarea( $val ) . '</textarea>';
		return;
	}

	echo '<input type="text" class="regular-text" name="ttp_theme_options[' . esc_attr( $key ) . ']" value="' . esc_attr( $val ) . '" />';
}

function ttp_sanitize_theme_options( $input ) {
	$out = array();
	$out['phone'] = sanitize_text_field( isset($input['phone']) ? $input['phone'] : '' );
	$out['email'] = sanitize_text_field( isset($input['email']) ? $input['email'] : '' );
	$out['google_reviews_url'] = esc_url_raw( isset($input['google_reviews_url']) ? $input['google_reviews_url'] : '' );
	$out['price_anchor'] = sanitize_text_field( isset($input['price_anchor']) ? $input['price_anchor'] : '$2,000+' );

	$lead_mode = sanitize_text_field( isset($input['lead_mode']) ? $input['lead_mode'] : 'referral' );
	$out['lead_mode'] = in_array( $lead_mode, array( 'referral', 'waitlist' ), true ) ? $lead_mode : 'referral';

	$out['waitlist_form_url'] = esc_url_raw( isset($input['waitlist_form_url']) ? $input['waitlist_form_url'] : '' );
	$out['referral_form_url'] = esc_url_raw( isset($input['referral_form_url']) ? $input['referral_form_url'] : '' );
	$out['commission_disclosure'] = sanitize_textarea_field( isset($input['commission_disclosure']) ? $input['commission_disclosure'] : 'Disclosure: We may receive a referral commission if you purchase through a breeder we refer you to.' );

	$out['pickup_address'] = sanitize_text_field( isset($input['pickup_address']) ? $input['pickup_address'] : '3800 Manorwood Rd, Austin, TX 78723' );
	$out['locality_center'] = sanitize_text_field( isset($input['locality_center']) ? $input['locality_center'] : 'Austin, TX' );

	$existing = get_option( 'ttp_theme_options', array() );
	if ( is_array( $existing ) ) {
		foreach ( array( 'apply_page_id', 'referral_page_id' ) as $k ) {
			if ( isset( $existing[ $k ] ) ) $out[ $k ] = absint( $existing[ $k ] );
		}
	}

	return $out;
}
