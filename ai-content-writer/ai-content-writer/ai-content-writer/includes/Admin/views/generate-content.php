<?php
/**
 * The template for generating AI content.
 *
 * @since 1.0.0
 * @package AIContentWriter/Admin/Views
 */

defined( 'ABSPATH' ) || exit; // Exit if accessed directly.

?>
<div class="wrap aicw-wrap">
	<div class="aicw__header">
		<h2 class="wp-heading-inline">
			<?php esc_html_e( 'Generate Content', 'ai-content-writer' ); ?>
			<a href="<?php echo esc_attr( admin_url( 'admin.php?page=aicw-settings' ) ); ?>" class="page-title-action">
				<?php esc_html_e( 'Configure API Settings', 'ai-content-writer' ); ?>
			</a>
		</h2>
		<p><?php esc_html_e( 'You can generate content here. This form will generate content based on the below configurations.', 'ai-content-writer' ); ?></p>
	</div>
	<div class="aicw__body">
		<form id="aicw-form" class="inline-fields" method="POST" action="<?php echo esc_url( admin_url( 'admin-post.php' ) ); ?>">
			<div class="aicw-form__content has-padding">
				<div class="form-field">
					<label for="prompt"><strong><?php esc_html_e( 'Prompt', 'ai-content-writer' ); ?></strong><abbr title="required">*</abbr></label>
					<div class="input-group">
						<textarea name="prompt" id="prompt" class="regular-text" placeholder="<?php esc_attr_e( 'Write a detailed, well-structured article on...', 'ai-content-writer' ); ?>" required="required"></textarea>
					</div>
					<p class="description">
						<?php esc_html_e( 'Enter the prompt title to generate content. Please, start with "Write an article on..."', 'ai-content-writer' ); ?>
					</p>
				</div>
				<div class="form-field">
					<label for="keywords"><strong><?php esc_html_e( 'Related Keywords', 'ai-content-writer' ); ?></strong></label>
					<div class="input-group">
						<input type="text" name="keywords" id="keywords" class="regular-text" placeholder="<?php esc_attr_e( 'keyword, keyword 2, keyword 3, ...', 'ai-content-writer' ); ?>"/>
					</div>
					<p class="description">
						<?php esc_html_e( 'Enter the related keywords to generate the article content. Separate each keyword with a comma.', 'ai-content-writer' ); ?>
					</p>
				</div>
				<div class="form-field">
					<label for="prompt_type"><strong><?php esc_html_e( 'Prompt Type', 'ai-content-writer' ); ?></strong><abbr title="required">*</abbr></label>
					<div class="input-group">
						<select name="prompt_type" id="prompt_type">
							<option value="Prompt"><?php esc_html_e( 'Prompt', 'ai-content-writer' ); ?></option>
							<option value="Completion"><?php esc_html_e( 'Completion', 'ai-content-writer' ); ?></option>
						</select>
					</div>
					<p class="description">
						<?php esc_html_e( 'Select the type of prompt to generate the article content.', 'ai-content-writer' ); ?>
					</p>
				</div>
				<div class="form-field">
					<label for="language"><strong><?php esc_html_e( 'Language', 'ai-content-writer' ); ?></strong><abbr title="required">*</abbr></label>
					<div class="input-group">
						<select name="language" id="language">
							<option value="English"><?php esc_html_e( 'English', 'ai-content-writer' ); ?></option>
						</select>
					</div>
					<p class="description">
						<?php esc_html_e( 'Select the language of the article. Currently, only English is supported.', 'ai-content-writer' ); ?>
					</p>
				</div>
				<div class="form-field">
					<label for="min_words"><strong><?php esc_html_e( 'Min Words', 'ai-content-writer' ); ?></strong></label>
					<div class="input-group">
						<input type="number" name="min_words" id="min_words" class="regular-text" placeholder="Example: 1000" min="0"/>
					</div>
					<p class="description">
						<?php esc_html_e( 'Enter the minimum words to generate the article content. Leave empty for default. *Keep it lower for reducing unexpected results.', 'ai-content-writer' ); ?>
					</p>
				</div>

				<!-- These fields for the ChatGPT API -->
				<h3><?php esc_html_e( 'Below fields are optional for ChatGPT API', 'ai-content-writer' ); ?></h3>
				<div class="form-field">
					<label for="system_tone"><strong><?php esc_html_e( 'System Tone', 'ai-content-writer' ); ?></strong></label>
					<div class="input-group">
						<textarea name="system_tone" id="system_tone" class="regular-text" placeholder="<?php esc_attr_e( 'You are an expert SEO content writer. Generate factually accurate, engaging, and well-structured articles optimized for readability and search engines.', 'ai-content-writer' ); ?>"></textarea>
					</div>
					<p class="description">
						<?php esc_html_e( 'Select the system tone for the ChatGPT API. Leave empty for default. For best results, use a tone that matches the content. Example: "You are an expert SEO content writer. Generate factually accurate, engaging, and well-structured articles optimized for readability and search engines."', 'ai-content-writer' ); ?>
					</p>
				</div>
				<div class="form-field">
					<label for="max_tokens"><strong><?php esc_html_e( 'Max Tokens', 'ai-content-writer' ); ?></strong></label>
					<div class="input-group">
						<input type="number" name="max_tokens" id="max_tokens" class="regular-text" placeholder="Example: 8000"/>
					</div>
					<p class="description">
						<?php esc_html_e( 'Enter the maximum tokens for the ChatGPT API. Leave empty for default. *Try to keep it at least 8000 for better results.', 'ai-content-writer' ); ?>
					</p>
				</div>
				<div class="form-field">
					<label for="temperature"><strong><?php esc_html_e( 'Temperature', 'ai-content-writer' ); ?></strong></label>
					<div class="input-group">
						<input type="number" name="temperature" id="temperature" class="regular-text" placeholder="0.7" min="0" max="1" step="0.1"/>
					</div>
					<p class="description">
						<?php esc_html_e( 'Enter the temperature for the ChatGPT API. Leave empty for default. Example: 0.7', 'ai-content-writer' ); ?>
					</p>
				</div>
			</div>
			<div class="aicw-form__aside">
				<div class="aicw-sidebar">
					<div class="aicw-sidebar__header">
						<h2><?php esc_html_e( 'Publish content as', 'ai-content-writer' ); ?>
							<small title="<?php esc_attr_e( 'Type', 'ai-content-writer' ); ?>"><?php esc_html_e( 'Type', 'ai-content-writer' ); ?></small>
						</h2>
					</div>
					<div class="aicw-sidebar__body">
						<div class="form-field">
							<label for="post_type">
								<strong><?php esc_html_e( 'Post Type', 'ai-content-writer' ); ?></strong>
								<abbr title="required">*</abbr>
							</label>
							<div class="input-group">
								<select name="post_type" id="post_type" required="required">
									<?php
									$post_types = get_post_types( array( 'public' => true ), 'objects' );
									// Remove attachment post type.
									unset( $post_types['attachment'] );
									foreach ( $post_types as $post_type ) {
										?>
										<option value="<?php echo esc_attr( $post_type->name ); ?>">
											<?php echo esc_html( $post_type->label ); ?>
										</option>
										<?php
									}
									?>
								</select>
							</div>
							<p class="description">
								<?php esc_html_e( 'Select the post type to publish the content.', 'ai-content-writer' ); ?>
							</p>
						</div>
					</div>
				</div>
				<div class="aicw-sidebar">
					<div class="aicw-sidebar__header">
						<h2><?php esc_html_e( 'Actions', 'ai-content-writer' ); ?></h2>
					</div>
					<div class="aicw-sidebar__body">
						<div class="form-field">
							<label for="status"><strong><?php esc_html_e( 'Status', 'ai-content-writer' ); ?></strong></label>
							<div class="input-group">
								<select name="status" id="status">
									<option value="publish"><?php esc_html_e( 'Publish', 'ai-content-writer' ); ?></option>
									<option value="draft"><?php esc_html_e( 'Draft', 'ai-content-writer' ); ?></option>
									<option value="pending"><?php esc_html_e( 'Pending', 'ai-content-writer' ); ?></option>
								</select>
							</div>
							<p class="description">
								<?php esc_html_e( 'Select the status of the campaign.', 'ai-content-writer' ); ?>
							</p>
						</div>
					</div>
					<div class="aicw-sidebar__footer">
						<input type="hidden" name="action" value="aicw_generate_content"/>
						<?php wp_nonce_field( 'aicw_generate_content' ); ?>
						<span class="spinner"></span>
						<?php submit_button( __( 'Generate Content', 'ai-content-writer' ), 'primary', 'generate_content' ); ?>
					</div>
				</div>
			</div>
		</form>
	</div>
</div>
