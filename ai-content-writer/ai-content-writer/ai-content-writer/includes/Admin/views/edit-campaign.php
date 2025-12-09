<?php
/**
 * The template for edit a campaign.
 *
 * @since 1.0.0
 * @package AIContentWriter/Admin/Views
 * @var WP_Post $campaign The campaign post object.
 */

defined( 'ABSPATH' ) || exit; // Exit if accessed directly.

$default_field = array(
	'search'  => '',
	'replace' => '',
);
$fields        = get_post_meta( $campaign->ID, '_aicw_search_replaces', true );
?>
<div class="wrap aicw-wrap">
	<div class="aicw__header">
		<h2 class="wp-heading-inline">
			<?php esc_html_e( 'Edit Campaign', 'ai-content-writer' ); ?>
			<a href="<?php echo esc_attr( admin_url( 'admin.php?page=aicw-campaigns&add=yes' ) ); ?>" class="page-title-action">
				<?php esc_html_e( 'Add Another Campaign', 'ai-content-writer' ); ?>
			</a>
		</h2>
		<p><?php esc_html_e( 'You can edit the campaign here. This form will update the campaign.', 'ai-content-writer' ); ?></p>
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
								<input type="text" name="title" id="title" class="regular-text" placeholder="Enter campaign title" value="<?php echo esc_attr( $campaign->post_title ); ?>" required="required"/>
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
							<?php $campaign_type = get_post_meta( $campaign->ID, '_aicw_campaign_type', true ); ?>
							<label for="campaign_type"><strong><?php esc_html_e( 'Campaign Type', 'ai-content-writer' ); ?></strong><abbr class="required" title="required">*</abbr></label>
							<div class="input-group">
								<select name="campaign_type" id="campaign_type">
									<option value="articles" <?php selected( 'articles', $campaign_type ); ?>><?php esc_html_e( 'Articles', 'ai-content-writer' ); ?></option>
									<option value="rss-feed" <?php selected( 'rss-feed', $campaign_type ); ?>><?php esc_html_e( 'RSS Feed', 'ai-content-writer' ); ?></option>
									<option value="gemini" <?php selected( 'gemini', $campaign_type ); ?>><?php esc_html_e( 'Gemini', 'ai-content-writer' ); ?></option>
									<option value="chatgpt" <?php selected( 'chatgpt', $campaign_type ); ?>><?php esc_html_e( 'ChatGPT', 'ai-content-writer' ); ?></option>
								</select>
							</div>
							<p class="description">
								<?php esc_html_e( 'Select the campaign type to generate the campaign content.', 'ai-content-writer' ); ?>
							</p>
						</div>

						<div class="form-field show-if__articles hide-if__rss-feed hide-if__gemini hide-if__chatgpt">
							<label for="campaign_host"><strong><?php esc_html_e( 'Campaign Host', 'ai-content-writer' ); ?></strong></label>
							<div class="input-group">
								<input type="text" name="campaign_host" id="campaign_host" class="regular-text" placeholder="<?php esc_attr_e( 'https://www.bing.com/', 'ai-content-writer' ); ?>" value="<?php echo esc_attr( get_post_meta( $campaign->ID, '_aicw_campaign_host', true ) ); ?>"/>
							</div>
							<p class="description">
								<?php esc_html_e( 'Enter the campaign host URL. This will be used to scrape the content from the allowed hosts. Configure the allowed hosts in the settings page. Currently, we allow only Bing as a host.', 'ai-content-writer' ); ?>
							</p>
						</div>

						<div class="form-field show-if__articles hide-if__rss-feed  show-if__gemini show-if__chatgpt">
							<?php $campaign_source = get_post_meta( $campaign->ID, '_aicw_campaign_source', true ); ?>
							<label for="campaign_source"><strong><?php esc_html_e( 'Campaign Source', 'ai-content-writer' ); ?></strong><abbr class="required" title="required">*</abbr></label>
							<div class="input-group">
								<select name="campaign_source" id="campaign_source">
									<option value="keywords" <?php selected( 'keywords', $campaign_source ); ?>><?php esc_html_e( 'Keywords', 'ai-content-writer' ); ?></option>
								</select>
							</div>
							<p class="description">
								<?php esc_html_e( 'Select the campaign source. This will be used to generate the campaign content.', 'ai-content-writer' ); ?>
							</p>
						</div>
						<div class="form-field show-if__articles hide-if__rss-feed show-if__gemini show-if__chatgpt">
							<label for="keywords"><strong><?php esc_html_e( 'Keywords', 'ai-content-writer' ); ?></strong><abbr class="required" title="required">*</abbr></label>
							<div class="input-group">
								<textarea name="keywords" id="keywords" class="regular-text" placeholder="<?php esc_attr_e( 'keyword, keyword 2, keyword 3, ...', 'ai-content-writer' ); ?>"><?php echo wp_kses_post( $campaign->post_content ); ?></textarea>
							</div>
							<p class="description">
								<?php esc_html_e( 'Enter the keywords to generate the campaign content. Separate each keyword with a comma.', 'ai-content-writer' ); ?>
							</p>
						</div>
						<div class="form-field hide-if__articles show-if__rss-feed hide-if__gemini hide-if__chatgpt display-none">
							<label for="rss_feed_link"><strong><?php esc_html_e( 'RSS Feed Link', 'ai-content-writer' ); ?></strong><abbr class="required" title="required">*</abbr></label>
							<div class="input-group">
								<input type="text" name="rss_feed_link" id="rss_feed_link" class="regular-text" placeholder="<?php esc_attr_e( 'https://www.example.com/feed', 'ai-content-writer' ); ?>" value="<?php echo esc_attr( get_post_meta( $campaign->ID, '_aicw_rss_feed_link', true ) ); ?>"/>
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
								<input type="text" name="block_keywords" id="block_keywords" class="regular-text" placeholder="<?php esc_attr_e( 'keyword, keyword 2, keyword 3, ...', 'ai-content-writer' ); ?>" value="<?php echo esc_attr( get_post_meta( $campaign->ID, '_aicw_block_keywords', true ) ); ?>"/>
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
									<?php if ( ! empty( $fields ) && is_array( $fields ) ) : ?>
										<?php foreach ( $fields as $field ) : ?>
											<?php aicw_search_replace_fields( $field ); ?>
										<?php endforeach; ?>
									<?php else : ?>
										<?php aicw_search_replace_fields( $default_field ); ?>
									<?php endif; ?>
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
								<input type="text" name="html_cleaners" id="html_cleaners" class="regular-text" placeholder="<?php esc_attr_e( '.class-name, #id, div.class-name, ...', 'ai-content-writer' ); ?>" value="<?php echo esc_attr( get_post_meta( $campaign->ID, '_aicw_html_cleaners', true ) ); ?>"/>
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
							<?php $insert_content_position = get_post_meta( $campaign->ID, '_aicw_insert_content_position', true ); ?>
							<label for="insert_content_position"><strong><?php esc_html_e( 'Position', 'ai-content-writer' ); ?></strong></label>
							<div class="input-group">
								<select name="insert_content_position" id="insert_content_position">
									<option value="none" <?php selected( 'none', $insert_content_position ); ?>><?php esc_html_e( 'None (Do not insert)', 'ai-content-writer' ); ?></option>
									<option value="before" <?php selected( 'before', $insert_content_position ); ?>><?php esc_html_e( 'Before Content', 'ai-content-writer' ); ?></option>
									<option value="after" <?php selected( 'after', $insert_content_position ); ?>><?php esc_html_e( 'After Content', 'ai-content-writer' ); ?></option>
								</select>
							</div>
							<p class="description">
								<?php esc_html_e( 'Select the position to insert your custom content.', 'ai-content-writer' ); ?>
							</p>
						</div>
						<div class="form-field">
							<label for="insert_content"><strong><?php esc_html_e( 'Content', 'ai-content-writer' ); ?></strong></label>
							<div class="input-group">
								<textarea name="insert_content" id="insert_content" class="regular-text" placeholder="<?php esc_attr_e( 'Enter your custom content here...', 'ai-content-writer' ); ?>"><?php echo wp_kses_post( get_post_meta( $campaign->ID, '_aicw_insert_content', true ) ); ?></textarea>
							</div>
							<p class="description">
								<?php esc_html_e( 'Enter your custom content to insert into the generated content depending on the selected position. You can use HTML tags to format your content.', 'ai-content-writer' ); ?>
							</p>
						</div>
					</div>
				</div><!-- End: Insert Content -->
				<!-- Campaign Posts -->
				<div class="aicw_posts">
					<h2 class="heading">
						<?php esc_html_e( 'Campaign Posts', 'ai-content-writer' ); ?>
						<sup><?php esc_html_e( 'Processing', 'ai-content-writer' ); ?></sup>
					</h2>
					<p><?php esc_html_e( 'Below are the temporary posts generated for this campaign. The progress bar shows the completion percentage of the post.', 'ai-content-writer' ); ?></p>
					<?php
					// Get all the temporary posts.
					$posts = get_posts(
						array(
							'post_type'      => 'aicw_post',
							'posts_per_page' => -1,
							'meta_query'     => array( // phpcs:ignore WordPress.DB.SlowDBQuery.slow_db_query_meta_query
								array(
									'key'   => '_aicw_campaign_id',
									'value' => $campaign->ID,
								),
							),
							'post_status'    => 'any',
						)
					);
					?>
					<table class="wp-list-table widefat fixed striped">
						<thead>
						<tr>
							<th><?php esc_html_e( 'Title', 'ai-content-writer' ); ?></th>
							<th><?php esc_html_e( 'Progress', 'ai-content-writer' ); ?></th>
							<th class="status"><?php esc_html_e( 'Status', 'ai-content-writer' ); ?></th>
							<th class="status"><?php esc_html_e( 'Source', 'ai-content-writer' ); ?></th>
							<th class="actions"><?php esc_html_e( 'Actions', 'ai-content-writer' ); ?></th>
						</tr>
						</thead>
						<tbody>
						<?php
						if ( $posts ) :

							foreach ( $posts as $post ) :
								?>
								<tr>
									<td class="maybe-has__thumbnail">
										<?php $thumbnail = get_the_post_thumbnail_url( $post->ID, 'thumbnail' ); ?>
										<?php if ( $thumbnail ) : ?>
											<img src="<?php echo esc_url( $thumbnail ); ?>" alt="<?php echo esc_attr( $post->post_title ); ?>"/>
										<?php endif; ?>

										<?php echo esc_html( $post->post_title ); ?>
									</td>
									<td>
										<?php
										$total          = 3;
										$updates_needed = count( aicw_temp_post_needs_update( $post, $campaign->ID ) );
										$completed      = $total - $updates_needed;
										$progress       = ( $completed / $total ) * 100;
										?>
										<div class="progress-indicator">
											<div class="progress-indicator-inner" style="width: <?php echo esc_attr( $progress ); ?>%;">
												<?php echo esc_html( round( $progress ) ); ?>%
											</div>
										</div>
									</td>
									<td><?php echo esc_html( $post->post_status ); ?></td>
									<td>
										<?php
										$source_link = get_post_meta( $post->ID, '_aicw_content_source_link', true );
										if ( $source_link ) :
											?>
											<a href="<?php echo esc_url( $source_link ); ?>" target="_blank">
												<?php esc_html_e( 'View Source', 'ai-content-writer' ); ?>
											</a>
											<?php
										else :
											echo esc_html( '&mdash;' );
										endif;
										?>
									</td>
									<td>
										<a href="#" class="aicw_delete_temp_post" data-post-id="<?php echo esc_attr( $post->ID ); ?>">
											<?php esc_html_e( 'Delete', 'ai-content-writer' ); ?>
										</a>
									</td>
								</tr>
								<?php
							endforeach;
						else :
							?>
							<tr>
								<td colspan="5"><?php esc_html_e( 'No generated posts found for this campaign. Please wait while the posts are being generated. It may take a while. Or maybe already generated and completed the target of this campaign.', 'ai-content-writer' ); ?></td>
							</tr>
							<?php
						endif;
						?>
						</tbody>
					</table>
				</div><!-- End: Campaign Posts -->
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
								<input type="range" name="target" id="target" min="1" max="<?php echo esc_attr( aicw_get_campaign_target_max_limit() ); ?>" value="<?php echo esc_attr( get_post_meta( $campaign->ID, '_aicw_campaign_target', true ) ); ?>"/>
								<span class="range_slider_value"><?php echo esc_attr( get_post_meta( $campaign->ID, '_aicw_campaign_target', true ) ); ?></span><span class="range_slider_max"><?php echo esc_html( '/' . aicw_get_campaign_target_max_limit() ); ?></span>
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
									<option value="publish" <?php selected( 'publish', $campaign->post_status ); ?>><?php esc_html_e( 'Active', 'ai-content-writer' ); ?></option>
									<option value="draft" <?php selected( 'draft', $campaign->post_status ); ?>><?php esc_html_e( 'Draft', 'ai-content-writer' ); ?></option>
									<option value="pending" <?php selected( 'pending', $campaign->post_status ); ?>><?php esc_html_e( 'Pending', 'ai-content-writer' ); ?></option>
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
					<div class="aicw-sidebar__footer space-between">
						<input type="hidden" name="id" value="<?php echo esc_attr( $campaign->ID ); ?>"/>
						<input type="hidden" name="action" value="aicw_edit_campaign"/>
						<?php wp_nonce_field( 'aicw_edit_campaign' ); ?>
						<button type="button" id='aicw_run_campaign' class="button" data-campaign-id="<?php echo esc_attr( $campaign->ID ); ?>"><?php esc_html_e( 'Run Campaign', 'ai-content-writer' ); ?></button>
						<span id ="aicw_run_campaign_spinner" class="spinner"></span>
						<?php submit_button( __( 'Save Changes', 'ai-content-writer' ), 'primary', 'edit_campaign' ); ?>
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
										<option value="<?php echo esc_attr( $post_type->name ); ?>" <?php selected( $post_type->name, get_post_meta( $campaign->ID, '_aicw_post_type', true ) ); ?>>
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
									<option value="publish" <?php selected( 'publish', get_post_meta( $campaign->ID, '_aicw_completed_post_status', true ) ); ?>><?php esc_html_e( 'Publish', 'ai-content-writer' ); ?></option>
									<option value="draft" <?php selected( 'draft', get_post_meta( $campaign->ID, '_aicw_completed_post_status', true ) ); ?>><?php esc_html_e( 'Draft', 'ai-content-writer' ); ?></option>
									<option value="pending" <?php selected( 'pending', get_post_meta( $campaign->ID, '_aicw_completed_post_status', true ) ); ?>><?php esc_html_e( 'Pending', 'ai-content-writer' ); ?></option>
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
								<input type="checkbox" name="generate_thumbnail" id="generate_thumbnail" <?php checked( get_post_meta( $campaign->ID, '_aicw_generate_thumbnail', true ), 'yes' ); ?>/>
								<strong><?php esc_html_e( 'Generate Thumbnail', 'ai-content-writer' ); ?></strong>
							</label>
							<p class="description">
								<?php esc_html_e( 'Enable to generate a thumbnail for the each campaigns generated content.', 'ai-content-writer' ); ?>
							</p>
						</div>
					</div>
				</div><!-- End: Campaign Settings -->
				<!-- Campaign Posts -->
				<div class="aicw-sidebar">
					<div class="aicw-sidebar__header">
						<h2>
							<?php esc_html_e( 'Campaign Posts', 'ai-content-writer' ); ?>
							<sup><?php esc_html_e( 'Completed', 'ai-content-writer' ); ?></sup>
						</h2>
					</div>
					<div class="aicw-sidebar__body">
						<?php
						// Get all the temporary posts.
						$completed_posts = get_posts(
							array(
								'post_type'      => 'post',
								'posts_per_page' => -1,
								'meta_query'     => array( // phpcs:ignore WordPress.DB.SlowDBQuery.slow_db_query_meta_query
									array(
										'key'   => '_aicw_campaign_id',
										'value' => $campaign->ID,
									),
								),
								'post_status'    => 'any',
							)
						);

						if ( $completed_posts ) :
							?>
							<ul>
								<?php
								foreach ( $completed_posts as $post ) :
									?>
									<li class="maybe-has__thumbnail">
										<?php $thumbnail = get_the_post_thumbnail_url( $post->ID, 'thumbnail' ); ?>
										<?php if ( $thumbnail ) : ?>
											<img src="<?php echo esc_url( $thumbnail ); ?>" alt="<?php echo esc_attr( $post->post_title ); ?>"/>
										<?php endif; ?>

										<a href="<?php echo esc_url( get_edit_post_link( $post->ID ) ); ?>" target="_blank">
											<?php echo esc_html( $post->post_title ); ?>
										</a>
									</li>
									<?php
								endforeach;
								?>
							</ul>
							<?php
						else :
							?>
							<p><?php esc_html_e( 'No completed posts found for this campaign.', 'ai-content-writer' ); ?></p>
							<?php
						endif;
						?>
					</div>
				</div><!-- End: Campaign Posts -->
			</div>
		</form>
	</div>
</div>
