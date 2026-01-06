<?php
if ( ! defined( 'ABSPATH' ) ) { exit; }

function ttp_register_theme_settings() {
	register_setting( 'ttp_theme_options_group', 'ttp_theme_options', array(
		'sanitize_callback' => 'ttp_sanitize_theme_options',
		'default' => array(),
	) );

	add_settings_section( 'ttp_section_main', __( 'Site & Lead Settings', 'ttp' ), '__return_false', 'ttp_theme_settings' );

	$fields = array(
		'lead_mode' => array( 'label' => 'Lead Mode', 'type' => 'select', 'options' => array(
			'referral' => 'Referral Request Mode',
			'waitlist' => 'Apply / Waitlist Mode',
		)),
		'waitlist_form_url' => array( 'label' => 'Apply/Waitlist Google Form URL', 'type' => 'url' ),
		'referral_form_url' => array( 'label' => 'Referral Request Google Form URL (optional for now)', 'type' => 'url' ),
		'apply_page_id' => array( 'label' => 'Apply/Waitlist Page', 'type' => 'page' ),
		'referral_page_id' => array( 'label' => 'Referral Request Page', 'type' => 'page' ),
		'featured_puppy_id' => array( 'label' => 'Featured Puppy (optional)', 'type' => 'post', 'post_type' => 'ttp_puppy' ),
		'price_anchor' => array( 'label' => 'Price Anchor Text', 'type' => 'text', 'placeholder' => '$2,000+' ),
		'business_name' => array( 'label' => 'Business Name', 'type' => 'text', 'placeholder' => 'Texas Teacup Morkies' ),
		'phone' => array( 'label' => 'Phone (Call/Text)', 'type' => 'text', 'placeholder' => '(512) 555-1234' ),
		'email' => array( 'label' => 'Email', 'type' => 'email', 'placeholder' => 'info@texasteacupmorkies.com' ),
		'address_line1' => array( 'label' => 'Address Line 1', 'type' => 'text' ),
		'address_city' => array( 'label' => 'City', 'type' => 'text', 'placeholder' => 'Austin' ),
		'address_state' => array( 'label' => 'State', 'type' => 'text', 'placeholder' => 'TX' ),
		'address_zip' => array( 'label' => 'ZIP', 'type' => 'text' ),
		'google_reviews_url' => array( 'label' => 'Google Reviews URL', 'type' => 'url' ),
		'commission_disclosure' => array( 'label' => 'Referral Commission Disclosure', 'type' => 'textarea' ),
	);

	foreach ( $fields as $key => $cfg ) {
		add_settings_field( 'ttp_' . $key, esc_html( $cfg['label'] ), 'ttp_render_setting_field', 'ttp_theme_settings', 'ttp_section_main', array(
			'key' => $key,
			'cfg' => $cfg,
		) );
	}
}
add_action( 'admin_init', 'ttp_register_theme_settings' );

function ttp_sanitize_theme_options( $input ) {
	$out = array();
	$input = is_array( $input ) ? $input : array();

	$out['lead_mode'] = in_array( $input['lead_mode'] ?? 'referral', array( 'referral', 'waitlist' ), true ) ? $input['lead_mode'] : 'referral';
	$out['waitlist_form_url'] = esc_url_raw( $input['waitlist_form_url'] ?? '' );
	$out['referral_form_url'] = esc_url_raw( $input['referral_form_url'] ?? '' );
	$out['apply_page_id'] = absint( $input['apply_page_id'] ?? 0 );
	$out['referral_page_id'] = absint( $input['referral_page_id'] ?? 0 );
	$out['featured_puppy_id'] = absint( $input['featured_puppy_id'] ?? 0 );

	$out['price_anchor'] = sanitize_text_field( $input['price_anchor'] ?? '$2,000+' );
	$out['business_name'] = sanitize_text_field( $input['business_name'] ?? get_bloginfo( 'name' ) );
	$out['phone'] = sanitize_text_field( $input['phone'] ?? '' );
	$out['email'] = sanitize_email( $input['email'] ?? '' );

	$out['address_line1'] = sanitize_text_field( $input['address_line1'] ?? '' );
	$out['address_city'] = sanitize_text_field( $input['address_city'] ?? '' );
	$out['address_state'] = sanitize_text_field( $input['address_state'] ?? '' );
	$out['address_zip'] = sanitize_text_field( $input['address_zip'] ?? '' );

	$out['google_reviews_url'] = esc_url_raw( $input['google_reviews_url'] ?? '' );
	$default_disclosure = 'Disclosure: We may receive a referral commission if you purchase through a breeder we refer you to.';
	$out['commission_disclosure'] = sanitize_textarea_field( $input['commission_disclosure'] ?? $default_disclosure );

	return $out;
}

function ttp_render_setting_field( $args ) {
	$key = $args['key'];
	$cfg = $args['cfg'];
	$options = get_option( 'ttp_theme_options', array() );
	$val = $options[ $key ] ?? '';
	$type = $cfg['type'] ?? 'text';

	if ( 'select' === $type ) {
		echo '<select name="ttp_theme_options[' . esc_attr( $key ) . ']">';
		foreach ( (array) ( $cfg['options'] ?? array() ) as $k => $label ) {
			printf( '<option value="%s"%s>%s</option>', esc_attr( $k ), selected( $val, $k, false ), esc_html( $label ) );
		}
		echo '</select>';
		return;
	}

	if ( 'page' === $type ) {
		wp_dropdown_pages( array(
			'name' => 'ttp_theme_options[' . esc_attr( $key ) . ']',
			'show_option_none' => __( '— Select —', 'ttp' ),
			'option_none_value' => '0',
			'selected' => absint( $val ),
		) );
		return;
	}

	if ( 'post' === $type ) {
		$post_type = $cfg['post_type'] ?? 'post';
		$posts = get_posts( array(
			'post_type' => $post_type,
			'numberposts' => 50,
			'orderby' => 'date',
			'order' => 'DESC',
		) );
		echo '<select name="ttp_theme_options[' . esc_attr( $key ) . ']">';
		echo '<option value="0">' . esc_html__( '— None —', 'ttp' ) . '</option>';
		foreach ( $posts as $p ) {
			printf( '<option value="%d"%s>%s</option>', (int) $p->ID, selected( (int) $val, (int) $p->ID, false ), esc_html( $p->post_title ) );
		}
		echo '</select>';
		return;
	}

	$placeholder = $cfg['placeholder'] ?? '';
	if ( 'textarea' === $type ) {
		echo '<textarea rows="3" style="width:100%;max-width:720px" name="ttp_theme_options[' . esc_attr( $key ) . ']">' . esc_textarea( (string) $val ) . '</textarea>';
		return;
	}

	echo '<input type="' . esc_attr( $type ) . '" style="width:100%;max-width:720px" name="ttp_theme_options[' . esc_attr( $key ) . ']" value="' . esc_attr( (string) $val ) . '" placeholder="' . esc_attr( (string) $placeholder ) . '" />';
}

function ttp_add_theme_settings_menu() {
	add_theme_page( __( 'TTP Settings', 'ttp' ), __( 'TTP Settings', 'ttp' ), 'manage_options', 'ttp-theme-settings', 'ttp_render_theme_settings_page' );
}
add_action( 'admin_menu', 'ttp_add_theme_settings_menu' );

function ttp_render_theme_settings_page() {
	?>
	<div class="wrap">
		<h1><?php esc_html_e( 'TTP Settings', 'ttp' ); ?></h1>
		<p><?php esc_html_e( 'Control lead flow (Waitlist vs Referral), forms, contact info, and other site-wide settings.', 'ttp' ); ?></p>
		<form method="post" action="options.php">
			<?php settings_fields( 'ttp_theme_options_group' ); do_settings_sections( 'ttp_theme_settings' ); submit_button(); ?>
		</form>
	</div>
	<?php
}
