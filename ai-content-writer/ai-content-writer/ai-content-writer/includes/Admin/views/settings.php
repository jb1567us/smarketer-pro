<?php
/**
 * Settings.
 *
 * @since 1.0.0
 * @package AIContentWriter\Admin
 *
 * @var array $settings_tabs The settings tabs.
 */

defined( 'ABSPATH' ) || exit; // Exit if accessed directly.

$current_tab = isset( $_GET['tab'] ) ? sanitize_key( $_GET['tab'] ) : array_key_first( $settings_tabs ); // phpcs:ignore WordPress.Security.NonceVerification.Recommended -- Current tab for display only.

?>
<div class="wrap aicw-wrap aicw-settings">
	<div class="aicw__header">
		<h2 class="wp-heading-inline">
			<?php esc_html_e( 'Settings', 'ai-content-writer' ); ?>
		</h2>
	</div>
	<hr class="wp-header-end">
	<nav class="nav-tab-wrapper aicw-navbar">
		<?php foreach ( $settings_tabs as $tab_id => $settings_tab ) : ?>
			<a href="?page=aicw-settings&tab=<?php echo esc_attr( $tab_id ); ?>" class="nav-tab <?php echo $current_tab === $tab_id ? 'nav-tab-active' : ''; ?>">
				<?php echo esc_html( $settings_tab ?? ucfirst( $tab_id ) ); ?>
			</a>
		<?php endforeach; ?>
	</nav>
	<div class="aicw__body">
		<form id="aicw-settings-form" method="post" action="<?php echo esc_html( admin_url( 'admin-post.php' ) ); ?>">

			<?php
			/*
			 * Add settings fields common to all tabs.
			 * This action can be used to add settings fields that are not specific to any tab.
			 *
			 * @since 1.0.0
			 */
			do_action( 'aicw_settings' );

			/*
			 * Add settings fields for the current tab.
			 * This action can be used to add settings fields specific to the current tab.
			 *
			 * @since 1.0.0
			 */
			do_action( 'aicw_' . $current_tab . '_settings' );
			?>

			<input type="hidden" name="action" value="aicw_save_<?php echo esc_attr( $current_tab ); ?>_settings">
			<?php wp_nonce_field( 'aicw_save_' . $current_tab . '_settings' ); ?>
			<div class="field-group">
				<div class="field-submit-btn">
					<button class="button button-primary"><?php esc_html_e( 'Save Changes', 'ai-content-writer' ); ?></button>
				</div>
			</div>
		</form>

		<!-- Sidebar -->
		<div class="aicw__aside">
			<div class="aicw-sidebar">
				<div class="aicw-sidebar__header">
					<h2><?php esc_html_e( 'Support', 'ai-content-writer' ); ?></h2>
				</div>
				<div class="aicw-sidebar__body">
					<p><?php esc_html_e( 'If you need help, please contact us.', 'ai-content-writer' ); ?></p>
					<p>
						<a href="https://beautifulplugins.com/support" target="_blank" class="button button-secondary">
							<?php esc_html_e( 'Contact Support', 'ai-content-writer' ); ?>
						</a>
					</p>
				</div>
			</div>
			<div class="aicw-sidebar">
				<div class="aicw-sidebar__header">
					<h2><?php esc_html_e( 'Our Popular Plugins', 'ai-content-writer' ); ?></h2>
				</div>
				<div class="aicw-sidebar__body">
					<ul>
						<li>&rarr;
							<a href="https://wordpress.org/plugins/send-emails/" target="_blank">
								<?php esc_html_e( 'Send Emails – Newsletters, Automation & Email Marketing for WordPress', 'ai-content-writer' ); ?>
							</a>
						</li>
						<li>&rarr;
							<a href="https://wordpress.org/plugins/essential-elements/" target="_blank">
								<?php esc_html_e( 'Essential Elements for WordPress', 'ai-content-writer' ); ?>
							</a>
						</li>
						<li>&rarr;
							<a href="https://wordpress.org/plugins/advanced-shortcodes/" target="_blank">
								<?php esc_html_e( 'Shortcodes – Advanced Shortcode Manager', 'ai-content-writer' ); ?>
							</a>
						</li>
						<li>&rarr;
							<a href="https://wordpress.org/plugins/post-showcase/" target="_blank">
								<?php esc_html_e( 'Post Showcase', 'ai-content-writer' ); ?>
							</a>
						</li>
						<li>&rarr;
							<a href="https://wordpress.org/plugins/sms-manager/" target="_blank">
								<?php esc_html_e( 'SMS Manager – SMS Notifications for WooCommerce', 'ai-content-writer' ); ?>
							</a>
						</li>
						<li>&rarr;
							<a href="https://wordpress.org/plugins/invoice-payment/" target="_blank">
								<?php esc_html_e( 'Invoice Payment', 'ai-content-writer' ); ?>
							</a>
						</li>
					</ul>
				</div>
			</div>
			<?php
			/**
			 * Action hook to add content to the settings sidebar.
			 *
			 * @since 1.0.0
			 */
			do_action( 'aicw_settings_sidebar' );
			?>
		</div>
	</div>
</div>
<?php
