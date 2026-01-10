<?php
/**
 * The template for adding a campaign.
 *
 * @since 1.0.0
 * @package AIContentWriter/Admin/Views
 */

defined( 'ABSPATH' ) || exit; // Exit if accessed directly.

$default_field = array(
	'search'  => '',
	'replace' => '',
);
?>
<div class="wrap aicw-wrap">
	<div class="aicw__header">
		<h2 class="wp-heading-inline">
			<?php esc_html_e( 'Add Campaign', 'ai-content-writer' ); ?>
			<a href="<?php echo esc_attr( admin_url( 'admin.php?page=aicw-campaigns' ) ); ?>" class="page-title-action">
				<?php esc_html_e( 'Go Back', 'ai-content-writer' ); ?>
			</a>
		</h2>
		<p><?php esc_html_e( 'You can create a new campaign here. This form will create a new campaign.', 'ai-content-writer' ); ?></p>
	</div>
	<div class="aicw__body">
		<form id="aicw-form" method="POST" action="<?php echo esc_url( admin_url( 'admin-post.php' ) ); ?>">
			<div class="aicw-form__content">
				<!-- Campaign Title -->
				<div class="aicw-card">
					<div class="aicw-card__body">
						<div class="form-field">
							<label for="title"><strong><?php esc_html_e( 'Title', 'ai-content-writer' ); ?></strong><abbr class="required" title="required">*</abbr></label>
							<div class="input-group">
								<input type="text" name="title" id="title" class="regular-text" placeholder="Enter campaign title" required="required"/>
							</div>
							<p class="description">
								<?php esc_html_e( 'Enter the campaign title.', 'ai-content-writer' ); ?>
							</p>
						</div>
					</div>
				</div><!-- End: Campaign Title -->
				<!-- Campaign Details -->
				<div class="aicw-card">
					<div class="aicw-card__header">
						<h3 class="aicw-card__title"><?php esc_html_e( 'Campaign Details', 'ai-content-writer' ); ?></h3>
					</div>
					<div class="aicw-card__body">
						<div class="form-field">
							<label for="campaign_type"><strong><?php esc_html_e( 'Campaign Type', 'ai-content-writer' ); ?></strong><abbr class="required" title="required">*</abbr></label>
							<div class="input-group">
								<select name="campaign_type" id="campaign_type">
									<option value="articles"><?php esc_html_e( 'Articles', 'ai-content-writer' ); ?></option>
									<option value="rss-feed"><?php esc_html_e( 'RSS Feed', 'ai-content-writer' ); ?></option>
									<option value="gemini"><?php esc_html_e( 'Gemini', 'ai-content-writer' ); ?></option>
									<option value="chatgpt"><?php esc_html_e( 'ChatGPT', 'ai-content-writer' ); ?></option>
								</select>
							</div>
							<p class="description">
								<?php esc_html_e( 'Select the campaign type to generate the campaign content.', 'ai-content-writer' ); ?>
							</p>
						</div>
						<div class="form-field show-if__articles hide-if__rss-feed hide-if__gemini hide-if__chatgpt">
							<label for="campaign_host"><strong><?php esc_html_e( 'Campaign Host', 'ai-content-writer' ); ?></strong></label>
							<div class="input-group">
								<input type="text" name="campaign_host" id="campaign_host" class="regular-text" placeholder="<?php esc_attr_e( 'https://www.bing.com/', 'ai-content-writer' ); ?>" value="<?php echo esc_attr( get_option( 'aicw_default_host', 'https://www.bing.com/' ) ); ?>"/>
							</div>
							<p class="description">
								<?php esc_html_e( 'Enter the campaign host URL. This will be used to scrape the content from the allowed hosts. Configure the allowed hosts in the settings page. Currently, we allow only Bing as a host.', 'ai-content-writer' ); ?>
							</p>
						</div>
						<div class="form-field show-if__articles hide-if__rss-feed show-if__gemini show-if__chatgpt">
							<label for="campaign_source"><strong><?php esc_html_e( 'Campaign Source', 'ai-content-writer' ); ?></strong><abbr class="required" title="required">*</abbr></label>
							<div class="input-group">
								<select name="campaign_source" id="campaign_source">
									<option value="keywords"><?php esc_html_e( 'Keywords', 'ai-content-writer' ); ?></option>
								</select>
							</div>
							<p class="description">
								<?php esc_html_e( 'Select the campaign source. This will be used to generate the campaign content.', 'ai-content-writer' ); ?>
							</p>
						</div>
						<div class="form-field show-if__articles hide-if__rss-feed show-if__gemini show-if__chatgpt">
							<label for="keywords"><strong><?php esc_html_e( 'Keywords', 'ai-content-writer' ); ?></strong><abbr class="required" title="required">*</abbr></label>
							<div class="input-group">
								<textarea name="keywords" id="keywords" class="regular-text" placeholder="<?php esc_attr_e( 'keyword, keyword 2, keyword 3, ...', 'ai-content-writer' ); ?>"></textarea>
							</div>
							<p class="description">
								<?php esc_html_e( 'Enter the keywords to generate the campaign content. Separate each keyword with a comma.', 'ai-content-writer' ); ?>
							</p>
						</div>
						<div class="form-field hide-if__articles show-if__rss-feed hide-if__gemini hide-if__chatgpt display-none">
							<label for="rss_feed_link"><strong><?php esc_html_e( 'RSS Feed Link', 'ai-content-writer' ); ?></strong><abbr class="required" title="required">*</abbr></label>
							<div class="input-group">
								<input type="text" name="rss_feed_link" id="rss_feed_link" class="regular-text" placeholder="<?php esc_attr_e( 'https://www.example.com/feed', 'ai-content-writer' ); ?>"/>
							</div>
							<p class="description">
								<?php esc_html_e( 'Enter the RSS feed link. This will be used to generate the content from the RSS feed.', 'ai-content-writer' ); ?>
							</p>
						</div>
					</div>
				</div><!-- End: Campaign Details -->
				<!-- Content Filtering -->
				<div class="aicw-card">
					<div class="aicw-card__header">
						<h3 class="aicw-card__title"><?php esc_html_e( 'Content Filtering', 'ai-content-writer' ); ?></h3>
					</div>
					<div class="aicw-card__body">
						<div class="form-field">
							<label for="block_keywords"><strong><?php esc_html_e( 'Block Keywords', 'ai-content-writer' ); ?></strong></label>
							<div class="input-group">
								<input type="text" name="block_keywords" id="block_keywords" class="regular-text" placeholder="<?php esc_attr_e( 'keyword, keyword 2, keyword 3, ...', 'ai-content-writer' ); ?>"/>
							</div>
							<p class="description">
								<?php esc_html_e( 'Enter the keywords to block. Separate each keyword with a comma. This will be used to filter the content while generating the content. Remember, this is case sensitive.', 'ai-content-writer' ); ?>
							</p>
						</div>
						<div class="form-field">
							<label for="search_replaces"><strong><?php esc_html_e( 'Search Replace', 'ai-content-writer' ); ?></strong><abbr class="aicw-pro-badge required" title="<?php esc_attr_e( 'This feature is available in the Pro version', 'ai-content-writer' ); ?>"> &nbsp;&mdash; <a href="https://beautifulplugins.com/plugins/ai-content-writer-pro/?utm_source=plugin&utm_medium=pro-badge&utm_campaign=pro-badge" class="pro-label" target="_blank"><?php esc_html_e( 'Go Pro', 'ai-content-writer' ); ?></a></abbr></label>
							<div class="input-group">
								<table class="widefat striped aicw_repeat_table">
									<thead>
									<tr>
										<th class="search">
											<?php esc_html_e( 'Search', 'ai-content-writer' ); ?>
										</th>
										<th class="replace">
											<?php esc_html_e( 'Replace', 'ai-content-writer' ); ?>
										</th>
										<th class="actions">&nbsp;</th>
									</tr>
									</thead>
									<tbody>
									<?php aicw_search_replace_fields( $default_field ); ?>
									</tbody>
									<tfoot>
									<tr>
										<th colspan="2">
											<a href="#" class="button insert" data-row="
											<?php
											ob_start();
											aicw_search_replace_fields( $default_field );
											echo esc_attr( ob_get_clean() );
											?>
											"><?php esc_html_e( 'Add Row', 'ai-content-writer' ); ?></a>
										</th>
										<th>&nbsp;</th>
									</tr>
									</tfoot>
								</table>
							</div>
							<p class="description">
								<?php esc_html_e( 'Enter the search and replace keywords to filter the content. Click on the Add Row button to add more rows. Remember to use the search and replace keywords in the correct format. For example, if you want to replace "hello" with "hi", enter "hello" in the search field and "hi" in the replace field. It is case sensitive.', 'ai-content-writer' ); ?>
							</p>
						</div>
						<div class="form-field show-if__articles show-if__rss-feed hide-if__gemini hide-if__chatgpt">
							<label for="html_cleaners"><strong><?php esc_html_e( 'HTML Cleaner – Remove by Selector', 'ai-content-writer' ); ?></strong><abbr class="aicw-pro-badge required" title="<?php esc_attr_e( 'This feature is available in the Pro version', 'ai-content-writer' ); ?>"> &nbsp;&mdash; <a href="https://beautifulplugins.com/plugins/ai-content-writer-pro/?utm_source=plugin&utm_medium=pro-badge&utm_campaign=pro-badge" class="pro-label" target="_blank"><?php esc_html_e( 'Go Pro', 'ai-content-writer' ); ?></a></abbr></label>
							<div class="input-group">
								<input type="text" name="html_cleaners" id="html_cleaners" class="regular-text" placeholder="<?php esc_attr_e( '.class-name, #id, div.class-name, ...', 'ai-content-writer' ); ?>"/>
							</div>
							<p class="description">
								<?php esc_html_e( 'Enter the HTML selectors to remove content from the generated HTML dom elements. Separate each selector with a comma.', 'ai-content-writer' ); ?>
							</p>
						</div>
					</div>
				</div><!-- End: Content Filtering -->
				<!-- Insert Content -->
				<div class="aicw-card">
					<div class="aicw-card__header">
						<h3 class="aicw-card__title"><?php esc_html_e( 'Insert Content', 'ai-content-writer' ); ?></h3>
					</div>
					<div class="aicw-card__body">
						<div class="form-field">
							<label for="insert_content_position"><strong><?php esc_html_e( 'Position', 'ai-content-writer' ); ?></strong></label>
							<div class="input-group">
								<select name="insert_content_position" id="insert_content_position">
									<option value="none"><?php esc_html_e( 'None (Do not insert)', 'ai-content-writer' ); ?></option>
									<option value="before"><?php esc_html_e( 'Before Content', 'ai-content-writer' ); ?></option>
									<option value="after"><?php esc_html_e( 'After Content', 'ai-content-writer' ); ?></option>
								</select>
							</div>
							<p class="description">
								<?php esc_html_e( 'Select the position to insert your custom content.', 'ai-content-writer' ); ?>
							</p>
						</div>
						<div class="form-field">
							<label for="insert_content"><strong><?php esc_html_e( 'Content', 'ai-content-writer' ); ?></strong></label>
							<div class="input-group">
								<textarea name="insert_content" id="insert_content" class="regular-text" placeholder="<?php esc_attr_e( 'Enter your custom content here...', 'ai-content-writer' ); ?>"></textarea>
							</div>
							<p class="description">
								<?php esc_html_e( 'Enter your custom content to insert into the generated content depending on the selected position. You can use HTML tags to format your content.', 'ai-content-writer' ); ?>
							</p>
						</div>
					</div>
				</div><!-- End: Insert Content -->
			</div>
			<div class="aicw-form__aside">
				<!-- Campaign Actions -->
				<div class="aicw-sidebar">
					<div class="aicw-sidebar__header">
						<h2><?php esc_html_e( 'Campaign Actions', 'ai-content-writer' ); ?></h2>
					</div>
					<div class="aicw-sidebar__body">
						<div class="form-field">
							<label for="target"><strong><?php esc_html_e( 'Campaign Target', 'ai-content-writer' ); ?></strong></label>
							<div class="input-group range_slider">
								<input type="range" name="target" id="target" min="1" max="<?php echo esc_attr( aicw_get_campaign_target_max_limit() ); ?>" value="<?php echo esc_attr( '10' ); ?>"/>
								<span class="range_slider_value"><?php echo esc_attr( '10' ); ?></span><span class="range_slider_max"><?php echo esc_html( '/' . aicw_get_campaign_target_max_limit() ); ?></span>
							</div>
							<p class="description">
								<?php esc_html_e( 'Target number of posts to generate.', 'ai-content-writer' ); ?>
								<span class="aicw-pro-badge"><?php esc_html_e( 'Upgrading to Pro version will increase the limit.', 'ai-content-writer' ); ?></span>
								<abbr class="aicw-pro-badge required" title="<?php esc_attr_e( 'This feature is available in the Pro version', 'ai-content-writer' ); ?>"> &nbsp;&mdash; <a href="https://beautifulplugins.com/plugins/ai-content-writer-pro/?utm_source=plugin&utm_medium=pro-badge&utm_campaign=pro-badge" class="pro-label" target="_blank"><?php esc_html_e( 'Go Pro', 'ai-content-writer' ); ?></a></abbr>
							</p>
						</div>
						<div class="form-field">
							<label for="status"><strong><?php esc_html_e( 'Campaign Status', 'ai-content-writer' ); ?></strong></label>
							<div class="input-group">
								<select name="status" id="status">
									<option value="publish"><?php esc_html_e( 'Active', 'ai-content-writer' ); ?></option>
									<option value="draft"><?php esc_html_e( 'Draft', 'ai-content-writer' ); ?></option>
									<option value="pending"><?php esc_html_e( 'Pending', 'ai-content-writer' ); ?></option>
								</select>
							</div>
							<p class="description">
								<?php esc_html_e( 'Select the status of the campaign.', 'ai-content-writer' ); ?>
							</p>
						</div>
						<div class="form-field">
							<p class="description">
								<strong><?php esc_html_e( 'Campaign Frequency: ', 'ai-content-writer' ); ?></strong>
								<span><?php echo esc_html( get_option( 'aicwp_campaign_frequency', 'hourly' ) ); ?></span>
								<a href="<?php echo esc_url( admin_url( 'admin.php?page=aicw-settings' ) ); ?>" target="_blank">
									<?php esc_html_e( 'Change', 'ai-content-writer' ); ?>
								</a>
							</p>
						</div>
					</div>
					<div class="aicw-sidebar__footer">
						<input type="hidden" name="action" value="aicw_add_campaign"/>
						<?php wp_nonce_field( 'aicw_add_campaign' ); ?>
						<?php submit_button( __( 'Add Campaign', 'ai-content-writer' ), 'primary', 'add_campaign' ); ?>
					</div>
				</div><!-- End: Campaign Actions -->
				<!-- Publish Content as -->
				<div class="aicw-sidebar">
					<div class="aicw-sidebar__header">
						<h2>
							<?php esc_html_e( 'Publish Content as', 'ai-content-writer' ); ?>
							<sup><?php esc_html_e( 'Type', 'ai-content-writer' ); ?></sup>
						</h2>
					</div>
					<div class="aicw-sidebar__body">
						<div class="form-field">
							<label for="post_type">
								<strong><?php esc_html_e( 'Post Type', 'ai-content-writer' ); ?></strong>
								<abbr class="required" title="required">*</abbr>
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
						<div class="form-field">
							<label for="completed_post_status">
								<strong><?php esc_html_e( 'Completed Post Status', 'ai-content-writer' ); ?></strong>
								<abbr class="required" title="required">*</abbr>
							</label>
							<div class="input-group">
								<select name="completed_post_status" id="completed_post_status" required="required">
									<option value="publish"><?php esc_html_e( 'Publish', 'ai-content-writer' ); ?></option>
									<option value="draft"><?php esc_html_e( 'Draft', 'ai-content-writer' ); ?></option>
									<option value="pending"><?php esc_html_e( 'Pending', 'ai-content-writer' ); ?></option>
								</select>
							</div>
							<p class="description">
								<?php esc_html_e( 'Select the status of the generated posts. This will be used while publishing the generated posts.', 'ai-content-writer' ); ?>
							</p>
						</div>
					</div>
				</div><!-- End: Publish Content as -->
				<!-- Campaign Settings -->
				<div class="aicw-sidebar">
					<div class="aicw-sidebar__header">
						<h2><?php esc_html_e( 'Campaign Settings', 'ai-content-writer' ); ?></h2>
					</div>
					<div class="aicw-sidebar__body">
						<div class="form-field">
							<label for="generate_thumbnail">
								<input type="checkbox" name="generate_thumbnail" id="generate_thumbnail" <?php checked( 'yes', get_option( 'aicw_enable_img_generation' ) ); ?>/>
								<strong><?php esc_html_e( 'Generate Thumbnail', 'ai-content-writer' ); ?></strong>
							</label>
							<p class="description">
								<?php esc_html_e( 'Enable to generate a thumbnail for the each campaigns generated content.', 'ai-content-writer' ); ?>
							</p>
						</div>
					</div>
				</div><!-- End: Campaign Settings -->
			</div>
		</form>
	</div>
</div>
