<?php

namespace AIContentWriter\Admin;

defined( 'ABSPATH' ) || exit; // Exit if accessed directly.

/**
 * The settings class.
 *
 * @since 1.0.0
 * @package AIContentWriter\Admin
 */
class Settings {

	/**
	 * Settings constructor.
	 *
	 * @since 1.0.0
	 */
	public function __construct() {
		add_action( 'aicw_general_settings', array( __CLASS__, 'general_settings' ) );
		add_action( 'aicw_api_settings', array( __CLASS__, 'api_settings' ) );
		add_action( 'aicw_general_settings', array( __CLASS__, 'general_settings_fields' ), 20 );
	}

	/**
	 * Add general settings.
	 *
	 * @since 1.0.0
	 */
	public static function general_settings() {
		include __DIR__ . '/views/general-settings.php';
	}

	/**
	 * Add API settings.
	 *
	 * @since 1.0.0
	 */
	public static function api_settings() {
		include __DIR__ . '/views/api-settings.php';
	}

	/**
	 * Add general settings fields.
	 *
	 * @since 1.0.0
	 */
	public static function general_settings_fields() {
		?>
		<div class="field-group">
			<div class="field-label">
				<label for="aicwp_campaign_frequency">
					<strong><?php esc_html_e( 'Campaign Frequency:', 'ai-content-writer' ); ?></strong></label>
			</div>
			<div class="field">
				<select name="aicwp_campaign_frequency" id="aicwp_campaign_frequency" class="regular-text" disabled>
					<option value="hourly"><?php esc_html_e( 'Once Hourly (hourly)', 'ai-content-writer' ); ?></option>
				</select>
				<abbr class="aicw-pro-badge required" title="<?php esc_attr_e( 'This feature is available in the Pro version', 'ai-content-writer' ); ?>"> &nbsp;&mdash; <a href="https://beautifulplugins.com/plugins/ai-content-writer-pro/?utm_source=plugin&utm_medium=pro-badge&utm_campaign=pro-badge" class="pro-label" target="_blank"><?php esc_html_e( 'Go Pro', 'ai-content-writer' ); ?></a></abbr>
				<p class="description"><?php esc_html_e( 'Select the frequency (every 15 minutes, every 30 minutes, hourly, twice daily, daily, weekly) for the campaign to run automatically. This will be used to schedule the campaigns to run at the specified frequency to generate content.', 'ai-content-writer' ); ?></p>
			</div>
		</div>
		<?php
	}
}
