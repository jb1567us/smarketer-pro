<?php
/**
 * General Settings View.
 *
 * @since 1.0.0
 * @package AIContentWriter\Admin\Views
 */

defined( 'ABSPATH' ) || exit; // Exit if accessed directly.
?>
<div class="field-group field-section">
	<h3><?php esc_html_e( 'General Settings', 'ai-content-writer' ); ?></h3>
	<p><?php esc_html_e( 'The following options are the general settings for the AI Content Writer plugin.', 'ai-content-writer' ); ?></p>
</div>
<div class="field-group">
	<div class="field-label">
		<label for="aicw_allowed_hosts"><strong><?php esc_html_e( 'Allowed Hosts:', 'ai-content-writer' ); ?></strong></label>
	</div>
	<div class="field">
		<textarea name="aicw_allowed_hosts" id="aicw_allowed_hosts" class="regular-text" rows="3" placeholder="<?php esc_html_e( 'https://bing.com', 'ai-content-writer' ); ?>" disabled><?php echo esc_textarea( get_option( 'aicw_allowed_hosts' ) ); ?></textarea>
		<p class="description"><?php esc_html_e( 'Enter the allowed hosts. Each host should be on a new line. Example: https://bing.com. Currently, we allow only Bing as a host.', 'ai-content-writer' ); ?></p>
	</div>
</div>
<div class="field-group">
	<div class="field-label">
		<label for="aicw_default_host"><strong><?php esc_html_e( 'Default Host:', 'ai-content-writer' ); ?></strong></label>
	</div>
	<div class="field">
		<input type="text" name="aicw_default_host" id="aicw_default_host" class="regular-text" placeholder="<?php esc_html_e( 'https://www.bing.com/', 'ai-content-writer' ); ?>" value="<?php echo esc_attr( get_option( 'aicw_default_host', 'https://www.bing.com/' ) ); ?>" disabled/>
		<p class="description"><?php esc_html_e( 'Enter the default host URL. This will be used as a default host while generating the content.', 'ai-content-writer' ); ?></p>
	</div>
</div>
<div class="field-group field-section">
	<h3><?php esc_html_e( 'Logs Settings', 'ai-content-writer' ); ?></h3>
</div>
<div class="field-group">
	<div class="field-label">
		<label for="aicw_log_retention_period"><strong><?php esc_html_e( 'Log Retention Period:', 'ai-content-writer' ); ?></strong></label>
	</div>
	<div class="field">
		<?php $log_retention_period = absint( get_option( 'aicw_log_retention_period', 30 ) ); ?>
		<select name="aicw_log_retention_period" id="aicw_log_retention_period" class="regular-text">
			<option value="" <?php selected( $log_retention_period, '' ); ?>><?php esc_html_e( 'Keep Forever', 'ai-content-writer' ); ?></option>
			<option value="1" <?php selected( $log_retention_period, 1 ); ?>><?php esc_html_e( 'Daily', 'ai-content-writer' ); ?></option>
			<option value="7" <?php selected( $log_retention_period, 7 ); ?>><?php esc_html_e( '7 Days', 'ai-content-writer' ); ?></option>
			<option value="15" <?php selected( $log_retention_period, 15 ); ?>><?php esc_html_e( '15 Days', 'ai-content-writer' ); ?></option>
			<option value="30" <?php selected( $log_retention_period, 30 ); ?>><?php esc_html_e( '30 Days', 'ai-content-writer' ); ?></option>
			<option value="60" <?php selected( $log_retention_period, 60 ); ?>><?php esc_html_e( '60 Days', 'ai-content-writer' ); ?></option>
			<option value="90" <?php selected( $log_retention_period, 90 ); ?>><?php esc_html_e( '90 Days', 'ai-content-writer' ); ?></option>
			<option value="180" <?php selected( $log_retention_period, 180 ); ?>><?php esc_html_e( '180 Days', 'ai-content-writer' ); ?></option>
			<option value="365" <?php selected( $log_retention_period, 365 ); ?>><?php esc_html_e( '365 Days', 'ai-content-writer' ); ?></option>
		</select>
		<p class="description"><?php esc_html_e( 'Select the log retention period. Logs older than the selected period will be automatically deleted. Default is 30 days.', 'ai-content-writer' ); ?></p>
	</div>
</div>
<div class="field-group field-section">
	<h3><?php esc_html_e( 'Miscellaneous Settings', 'ai-content-writer' ); ?></h3>
	<p><?php esc_html_e( 'The following options are the miscellaneous settings for the AI Content Writer instant content generation feature.', 'ai-content-writer' ); ?></p>
</div>
<div class="field-group">
	<div class="field-label">
		<label for="aicw_api_model"><strong><?php esc_html_e( 'API Model:', 'ai-content-writer' ); ?></strong></label>
	</div>
	<div class="field">
		<select name="aicw_api_model" id="aicw_api_model" class="regular-text">
			<option value="gemini" <?php selected( get_option( 'aicw_api_model' ), 'gemini' ); ?>><?php esc_html_e( 'Gemini', 'ai-content-writer' ); ?></option>
			<option value="chatgpt" <?php selected( get_option( 'aicw_api_model' ), 'chatgpt' ); ?>><?php esc_html_e( 'ChatGPT', 'ai-content-writer' ); ?></option>
		</select>
		<p class="description"><?php esc_html_e( 'Select the AI model to generate content using the instant content Generation feature.', 'ai-content-writer' ); ?></p>
	</div>
</div>
<div class="field-group">
	<div class="field-label">
		<strong><?php esc_html_e( 'Enable Image Generation:', 'ai-content-writer' ); ?></strong>
	</div>
	<div class="field">
		<label for="aicw_enable_img_generation">
			<input name="aicw_enable_img_generation" id="aicw_enable_img_generation" type="checkbox" value="yes" <?php checked( get_option( 'aicw_enable_img_generation' ), 'yes' ); ?>>
			<?php esc_html_e( 'Enable Thumbnail Image Generation', 'ai-content-writer' ); ?>
		</label>
		<p class="description"><?php esc_html_e( 'Enable to activate the thumbnail image generation feature. AI generated content will have a featured image. This feature requires the Pexels API key.', 'ai-content-writer' ); ?></p>
	</div>
</div>
<div class="field-group">
	<div class="field-label">
		<strong><?php esc_html_e( 'Enable Redirection:', 'ai-content-writer' ); ?></strong>
	</div>
	<div class="field">
		<label for="aicw_enable_redirection">
			<input name="aicw_enable_redirection" id="aicw_enable_redirection" type="checkbox" value="yes" <?php checked( get_option( 'aicw_enable_redirection' ), 'yes' ); ?>>
			<?php esc_html_e( 'Enable Redirection', 'ai-content-writer' ); ?>
		</label>
		<p class="description"><?php esc_html_e( 'Enable to redirect to the edit page after successful generation of content from the "Generate Content" page.', 'ai-content-writer' ); ?></p>
	</div>
</div>
