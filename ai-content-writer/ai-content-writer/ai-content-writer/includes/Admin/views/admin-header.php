<?php
/**
 * AI Content Writer Admin Header
 *
 * @package AIContentWriter/Admin
 * @since 2.0.4
 * @var string $icon_url URL of the plugin icon.
 * @var bool $is_premium Whether the plugin is in premium mode.
 */

defined( 'ABSPATH' ) || exit; // Exit if accessed directly.

?>
<div class="aicw-admin-header">
	<?php
	/**
	 * Action to add content before the page heading.
	 *
	 * @since 2.0.4
	 */
	do_action( 'aicw_before_admin_header' );
	?>
	<div class="aicw-admin-header__info">
		<?php if ( $icon_url ) : ?>
		<div class="aicw-admin-header__logo">
			<img src="<?php echo esc_url( $icon_url ); ?>" alt="<?php esc_html_e( 'AI Content Writer', 'ai-content-writer' ); ?>" />
		</div>
		<?php endif; ?>
		<div class="aicw-admin-header__heading">
			<h1 class="aicw-admin-header__title">
				<?php esc_html_e( 'AI Content Writer', 'ai-content-writer' ); ?>
				<sup><?php echo esc_html( 'v' . AICW_VERSION ); ?></sup>
			</h1>
			<p class="aicw-admin-header__subtitle">
				<?php esc_html_e( 'Automatic content generator & auto poster.', 'ai-content-writer' ); ?>
			</p>
		</div>
	</div>
	<div class="aicw-admin-header__menu">
		<ul class="aicw-admin-header__menu-items">
			<li class="aicw-admin-header__menu-item">
				<a href="<?php echo esc_attr( admin_url( 'admin.php?page=ai-content-writer' ) ); ?>" class="aicw-admin-header__menu-link">
					<?php esc_html_e( 'Dashboard', 'ai-content-writer' ); ?>
				</a>
			</li>
			<li class="aicw-admin-header__menu-item">
				<a href="<?php echo esc_attr( admin_url( 'admin.php?page=aicw-campaigns' ) ); ?>" class="aicw-admin-header__menu-link">
					<?php esc_html_e( 'Campaigns', 'ai-content-writer' ); ?>
				</a>
			</li>
			<li class="aicw-admin-header__menu-item">
				<a href="<?php echo esc_attr( admin_url( 'admin.php?page=aicw-settings' ) ); ?>" class="aicw-admin-header__menu-link">
					<?php esc_html_e( 'Settings', 'ai-content-writer' ); ?>
				</a>
			</li>
			<li class="aicw-admin-header__menu-item">
				<a href="<?php echo esc_attr( admin_url( 'admin.php?page=aicw-help' ) ); ?>" class="aicw-admin-header__menu-link">
					<?php esc_html_e( 'Help', 'ai-content-writer' ); ?>
				</a>
			</li>
			<?php if ( ! $is_premium ) : ?>
			<li class="aicw-admin-header__menu-item">
				<a href="https://beautifulplugins.com/plugins/ai-content-writer-pro/?utm_source=plugin&utm_medium=pro-badge&utm_campaign=plugin-header" class="aicw-admin-header__menu-link go-pro" target="_blank">
					<?php esc_html_e( 'Go Pro', 'ai-content-writer' ); ?>
				</a>
			</li>
			<?php endif; ?>
		</ul>
	</div>
	<?php
	/**
	 * Action to add content after the page heading.
	 *
	 * @since 2.0.4
	 */
	do_action( 'aicw_after_admin_header' );
	?>
</div>
