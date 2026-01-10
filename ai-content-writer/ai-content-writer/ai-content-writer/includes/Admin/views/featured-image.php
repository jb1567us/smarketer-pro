<?php
/**
 * The featured image selection page form the list of images.
 *
 * @since 1.0.0
 * @package AIContentWriter
 *
 * @var \WP_Post $post The post object.
 */

defined( 'ABSPATH' ) || exit; // Exit if accessed directly.

// Check if the post is valid.
if ( ! isset( $post ) || ! $post instanceof \WP_Post ) {
	ai_content_writer()->flash_notice( esc_html__( 'Invalid post.', 'ai-content-writer' ), 'error' );
	// Redirect back to the previous page.
	wp_safe_redirect( admin_url( 'admin.php?page=ai-content-writer' ) );
	exit();
}

// Generate images for the prompt.
$images = ai_content_writer()->generate_images( $post->post_title );

if ( is_wp_error( $images ) ) {
	ai_content_writer()->flash_notice( $images->get_error_message(), 'error' );
	wp_safe_redirect( admin_url( 'post.php?post=' . $post->ID . '&action=edit' ) );
	exit();
}

?>
<div class="aicw-featured-image">
	<div class="aicw-featured-image__header">
		<h1 class="wp-heading-inline">
			<?php esc_html_e( 'Select Featured Image', 'ai-content-writer' ); ?>
		</h1>
	</div>
	<div class="aicw-featured-image__body">
		<form id="aicw-featured-image-form" method="POST" action="<?php echo esc_url( admin_url( 'admin-post.php' ) ); ?>">
			<div class="aicw-featured-image__content">
				<?php if ( ! empty( $images ) ) : ?>
					<div class="aicw-featured-image__images">
						<?php foreach ( $images as $individual_img ) : ?>
							<?php
							if ( ! isset( $individual_img['src']['medium'] ) || ! isset( $individual_img['src']['original'] ) || ! isset( $individual_img['alt'] ) || ! isset( $individual_img['id'] ) ) {
								continue;
							}
							?>
							<div class="aicw-featured-image__image">
								<label class="aicw-featured-image__image-label">
									<?php echo wp_kses_post( aicw_render_external_image( $individual_img['src']['medium'], $individual_img['alt'] ) ); ?>
									<input type="radio" name="featured_image" value="<?php echo esc_attr( $individual_img['id'] ); ?>">
									<input type="hidden" name="<?php echo esc_attr( $individual_img['id'] ); ?>" value="<?php echo esc_url( $individual_img['src']['original'] ); ?>">
								</label>
							</div>
						<?php endforeach; ?>
					</div>
				<?php else : ?>
					<p><?php esc_html_e( 'No images found.', 'ai-content-writer' ); ?></p>
				<?php endif; ?>
			</div>
			<div class="aicw-featured-image__footer">
				<input type="hidden" name="action" value="aicw_set_featured_image">
				<?php wp_nonce_field( 'aicw_set_featured_image' ); ?>
				<input type="hidden" name="post_id" value="<?php echo esc_attr( $post->ID ); ?>">
				<?php submit_button( __( 'Set Featured Image', 'ai-content-writer' ), 'primary', 'aicw_set_featured_image' ); ?>
			</div>
		</form>
	</div>
</div>
