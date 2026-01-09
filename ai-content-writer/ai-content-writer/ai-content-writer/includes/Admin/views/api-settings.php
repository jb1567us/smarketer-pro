<?php
/**
 * API Settings View.
 *
 * @since 1.0.0
 * @package AIContentWriter\Admin\Views
 */

defined( 'ABSPATH' ) || exit; // Exit if accessed directly.
?>
<div class="field-group field-section">
	<h3><?php esc_html_e( 'Gemini API', 'ai-content-writer' ); ?></h3>
	<p><?php esc_html_e( 'Configure the Gemini API settings to generation AI content using Google\'s Gemini.', 'ai-content-writer' ); ?></p>
</div>
<div class="field-group">
	<div class="field-label">
		<label for="aicw_gemini_api_key"><strong><?php esc_html_e( 'Gemini API Key:', 'ai-content-writer' ); ?></strong></label>
	</div>
	<div class="field">
		<input type="text" name="aicw_gemini_api_key" id="aicw_gemini_api_key" class="regular-text" value="<?php echo esc_attr( get_option( 'aicw_gemini_api_key' ) ); ?>" />
		<p class="description"><?php esc_html_e( 'Enter your Gemini API key.', 'ai-content-writer' ); ?></p>
	</div>
</div>
<div class="field-group">
	<div class="field-label">
		<label for="aicw_gemini_ai_model"><strong><?php esc_html_e( 'Gemini AI Model:', 'ai-content-writer' ); ?></strong></label>
	</div>
	<div class="field">
		<select name="aicw_gemini_ai_model" id="aicw_gemini_ai_model" class="regular-text">
			<?php foreach ( get_option( 'aicw_gemini_models', array() ) as $key => $value ) : ?>
				<option value="<?php echo esc_attr( $key ); ?>" <?php selected( get_option( 'aicw_gemini_ai_model' ), $key ); ?>><?php echo esc_html( $value ); ?></option>
			<?php endforeach; ?>
		</select>
		<p class="description"><?php esc_html_e( 'Select the Gemini AI model. Make sure the API key saved above is valid to load the models.', 'ai-content-writer' ); ?></p>
	</div>
</div>

<div class="field-group field-section">
	<h3><?php esc_html_e( 'ChatGPT API', 'ai-content-writer' ); ?></h3>
	<p><?php esc_html_e( 'Configure the ChatGPT API settings to generation AI content using OpenAI\'s ChatGPT.', 'ai-content-writer' ); ?></p>
</div>
<div class="field-group">
	<div class="field-label">
		<label for="aicw_chatgpt_api_secret_key"><strong><?php esc_html_e( 'ChatGPT API Secret Key:', 'ai-content-writer' ); ?></strong></label>
	</div>
	<div class="field">
		<input type="text" name="aicw_chatgpt_api_secret_key" id="aicw_chatgpt_api_secret_key" class="regular-text" value="<?php echo esc_attr( get_option( 'aicw_chatgpt_api_secret_key' ) ); ?>" />
		<p class="description"><?php esc_html_e( 'Enter your ChatGPT API secret key.', 'ai-content-writer' ); ?></p>
	</div>
</div>
<div class="field-group">
	<div class="field-label">
		<label for="aicw_chatgpt_ai_model"><strong><?php esc_html_e( 'ChatGPT AI Model:', 'ai-content-writer' ); ?></strong></label>
	</div>
	<div class="field">
		<select name="aicw_chatgpt_ai_model" id="aicw_chatgpt_ai_model" class="regular-text">
			<?php foreach ( get_option( 'aicw_chatgpt_models', array() ) as $key => $value ) : ?>
				<option value="<?php echo esc_attr( $key ); ?>" <?php selected( get_option( 'aicw_chatgpt_ai_model' ), $key ); ?>><?php echo esc_html( $value ); ?></option>
			<?php endforeach; ?>
		</select>
		<p class="description"><?php esc_html_e( 'Select the ChatGPT AI model to generate content. Make sure the API key saved above is valid to load the models.', 'ai-content-writer' ); ?></p>
	</div>
</div>
<div class="field-group field-section">
	<h3><?php esc_html_e( 'Image Settings', 'ai-content-writer' ); ?></h3>
	<p><?php esc_html_e( 'The following options are the image settings for the AI Content Writer plugin.', 'ai-content-writer' ); ?></p>
</div>
<div class="field-group">
	<div class="field-label">
		<label for="aicw_pexels_api_key"><strong><?php esc_html_e( 'Pexels API Key:', 'ai-content-writer' ); ?></strong></label>
	</div>
	<div class="field">
		<input type="text" name="aicw_pexels_api_key" id="aicw_pexels_api_key" class="regular-text" value="<?php echo esc_attr( get_option( 'aicw_pexels_api_key' ) ); ?>"/>
		<p class="description"><?php esc_html_e( 'Enter your Pexels API key. This key is required to generate thumbnails images for the AI generated content.', 'ai-content-writer' ); ?></p>
	</div>
</div>
