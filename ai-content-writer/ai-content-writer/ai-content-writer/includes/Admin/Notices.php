<?php

namespace AIContentWriter\Admin;

defined( 'ABSPATH' ) || exit; // Exit if accessed directly.

/**
 * Notices Class
 *
 * Handles admin notices for the AI Content Writer plugin including promotional notices,
 * important announcements, and other admin notifications.
 *
 * Notice Array Structure:
 * - id (required)          : Unique identifier for the notice
 * - type (optional)        : Notice type (promotional, info, warning, error)
 * - title (optional)       : Notice title/headline
 * - description (optional) : Notice description/message
 * - button_text (optional) : Primary button text
 * - button_url (optional)  : Primary button URL
 * - start_date (optional)  : Start date in Y-m-d format
 * - end_date (optional)    : End date in Y-m-d format
 * - remind_days (optional) : Days to remind later (default: 2)
 *
 * @since 1.0.0
 * @package AIContentWriter\Admin
 */
class Notices {

	/**
	 * Notice option name prefix.
	 *
	 * @var string
	 */
	const OPTION_PREFIX = 'aicw_notice_';

	/**
	 * Constructor
	 */
	public function __construct() {
		add_action( 'admin_notices', array( $this, 'display_notices' ) );
		add_action( 'admin_init', array( $this, 'maybe_cleanup_notices' ) );
		add_action( 'admin_enqueue_scripts', array( $this, 'enqueue_scripts' ) );
		add_action( 'wp_ajax_aicw_dismiss_notice', array( $this, 'ajax_dismiss_notice' ) );
		add_action( 'wp_ajax_aicw_remind_later_notice', array( $this, 'ajax_remind_later_notice' ) );
	}

	/**
	 * Get all available notices.
	 *
	 * @since 1.0.0
	 * @return array Array of notices.
	 */
	public function get_notices() {
		$notices = array(
			array(
				'id'          => 'black_friday_sale_2025',
				'type'        => 'promotional',
				'title'       => __( '🖤 Black Friday & Cyber Monday Mega Sale - Flat 70% OFF!', 'ai-content-writer' ),
				'description' => __( 'Don\'t miss out on our biggest sale of the year! Get 70% off on <strong>AI Content Writer Pro</strong> with code "<strong>MEGASALE70</strong>". Upgrade now for unlimited content generation, advanced AI models, and premium support. Offer valid for a limited time only!', 'ai-content-writer' ),
				'button_text' => __( 'Claim Flat 70% Off Now', 'ai-content-writer' ),
				'button_url'  => 'https://beautifulplugins.com/ai-content-writer-pro/?utm_source=plugin&utm_medium=notice&utm_campaign=black-friday-sale&discount=MEGASALE70',
				'start_date'  => '2025-11-20',
				'end_date'    => '2025-12-03',
				'remind_days' => 2,
			),
		);

		/**
		 * Filter available notices.
		 *
		 * @since 1.0.0
		 * @param array $notices Available notices.
		 */
		return apply_filters( 'aicw_admin_notices', $notices );
	}

	/**
	 * Check if notice should be displayed.
	 *
	 * @since 1.0.0
	 * @param array $notice Notice data.
	 * @return bool
	 */
	public function should_display_notice( $notice ) {
		// Check if user has capability.
		if ( ! current_user_can( 'manage_options' ) ) {
			return false;
		}

		// Check if notice is dismissed permanently.
		$dismissed = get_option( self::OPTION_PREFIX . $notice['id'] . '_dismissed', false );
		if ( $dismissed ) {
			return false;
		}

		// Check if notice is reminded later.
		$reminded_until = get_option( self::OPTION_PREFIX . $notice['id'] . '_reminded_until', false );
		if ( $reminded_until && time() < $reminded_until ) {
			return false;
		}

		// Check date range if provided.
		if ( ! empty( $notice['start_date'] ) ) {
			$start_date = strtotime( $notice['start_date'] );
			if ( time() < $start_date ) {
				return false;
			}
		}

		if ( ! empty( $notice['end_date'] ) ) {
			$end_date = strtotime( $notice['end_date'] . ' 23:59:59' );
			if ( time() > $end_date ) {
				return false;
			}
		}

		return true;
	}

	/**
	 * Display admin notices.
	 *
	 * @since 1.0.0
	 * @return void
	 */
	public function display_notices() {
		$notices = $this->get_notices();

		foreach ( $notices as $notice ) {
			if ( $this->should_display_notice( $notice ) ) {
				$this->render_notice( $notice );
			}
		}
	}

	/**
	 * Render notice HTML.
	 *
	 * @since 1.0.0
	 * @param array $notice Notice data.
	 * @return void
	 */
	public function render_notice( $notice ) {
		$notice_id   = esc_attr( $notice['id'] );
		$notice_type = isset( $notice['type'] ) ? esc_attr( $notice['type'] ) : 'info';
		$title       = isset( $notice['title'] ) ? $notice['title'] : '';
		$description = isset( $notice['description'] ) ? $notice['description'] : '';
		$button_text = isset( $notice['button_text'] ) ? $notice['button_text'] : __( 'Learn More', 'ai-content-writer' );
		$button_url  = isset( $notice['button_url'] ) ? esc_url( $notice['button_url'] ) : '';
		?>
		<div class="notice notice-info is-dismissible aicw-admin-notice aicw-notice-<?php echo esc_attr( $notice_type ); ?>" data-notice-id="<?php echo esc_attr( $notice_id ); ?>">
			<div class="aicw-notice-content">
				<?php if ( ! empty( $title ) ) : ?>
					<h3 class="aicw-notice-title"><?php echo wp_kses_post( $title ); ?></h3>
				<?php endif; ?>

				<?php if ( ! empty( $description ) ) : ?>
					<p class="aicw-notice-description"><?php echo wp_kses_post( $description ); ?></p>
				<?php endif; ?>

				<div class="aicw-notice-actions">
					<?php if ( ! empty( $button_url ) ) : ?>
						<a href="<?php echo esc_url( $button_url ); ?>" class="button button-primary aicw-notice-button" target="_blank">
							<?php echo esc_html( $button_text ); ?>
						</a>
					<?php endif; ?>

					<button type="button" class="button aicw-notice-remind-later" data-notice-id="<?php echo esc_attr( $notice_id ); ?>">
						<?php esc_html_e( 'Remind Me Later', 'ai-content-writer' ); ?>
					</button>

					<button type="button" class="button aicw-notice-dismiss" data-notice-id="<?php echo esc_attr( $notice_id ); ?>">
						<?php esc_html_e( 'Dismiss (Never Show Again)', 'ai-content-writer' ); ?>
					</button>
				</div>
			</div>
		</div>
		<?php
	}

	/**
	 * Cleanup old notice options that are no longer in use.
	 *
	 * @since 1.0.0
	 * @return void
	 */
	public function maybe_cleanup_notices() {
		$last_cleanup = get_transient( 'aicw_notices_last_cleanup' );

		if ( false !== $last_cleanup ) {
			return;
		}

		// Get all active notice IDs.
		$notices           = $this->get_notices();
		$active_notice_ids = wp_list_pluck( $notices, 'id' );

		// Get all options starting with the notice prefix.
		global $wpdb;
		$like_pattern = $wpdb->esc_like( self::OPTION_PREFIX ) . '%';

		// phpcs:ignore WordPress.DB.DirectDatabaseQuery.DirectQuery, WordPress.DB.DirectDatabaseQuery.NoCaching
		$options = $wpdb->get_col(
			$wpdb->prepare(
				"SELECT option_name FROM {$wpdb->options} WHERE option_name LIKE %s",
				$like_pattern
			)
		);

		// Handle potential database errors.
		if ( ! is_array( $options ) || empty( $options ) ) {
			$interval = apply_filters( 'aicw_notices_cleanup_interval', 30 * DAY_IN_SECONDS );
			set_transient( 'aicw_notices_last_cleanup', time(), $interval );
			return;
		}

		// Delete options for notices that are no longer active.
		foreach ( $options as $option_name ) {
			$notice_id = str_replace( self::OPTION_PREFIX, '', $option_name );
			$notice_id = preg_replace( '/_(dismissed|reminded_until)$/', '', $notice_id );

			// Delete option if notice is not in the active notices array.
			if ( ! in_array( $notice_id, $active_notice_ids, true ) ) {
				delete_option( $option_name );
			}
		}

		// Set transient to avoid frequent cleanups.
		$interval = apply_filters( 'aicw_notices_cleanup_interval', 30 * DAY_IN_SECONDS );
		set_transient( 'aicw_notices_last_cleanup', time(), $interval );
	}

	/**
	 * Enqueue admin scripts and styles.
	 *
	 * @since 1.0.0
	 * @return void
	 */
	public function enqueue_scripts() {
		wp_enqueue_script( 'aicw-notices', AICW_ASSETS_URL . 'js/aicw-notices.js', array( 'jquery' ), AICW_VERSION, true );

		// Localize script.
		wp_localize_script(
			'aicw-notices',
			'aicw_notices_object',
			array(
				'ajax_url' => admin_url( 'admin-ajax.php' ),
				'nonce'    => wp_create_nonce( 'aicw_notices_nonce' ),
			)
		);

		// Enqueue inline styles for notices.
		wp_add_inline_style( 'common', $this->get_notice_styles() );
	}

	/**
	 * Get notice styles.
	 *
	 * @since 1.0.0
	 * @return string
	 */
	public function get_notice_styles() {
		return '
			.aicw-admin-notice {
				border-left-color: #2271b1;
				padding-top: 0.8rem!important;
				padding-bottom: 0.8rem!important;
			}
			.aicw-admin-notice .aicw-notice-title {
				margin: 0 0 10px 0;
			}
			.aicw-admin-notice .aicw-notice-description {
				margin: 0 0 15px 0;
			}
			.aicw-admin-notice .aicw-notice-actions {
				display: flex;
				gap: 10px;
				flex-wrap: wrap;
			}
			.aicw-notice-promotional {
				border-left-color: #D63638;
			}
			.aicw-notice-promotional .aicw-notice-title {
				color: #D63638;
			}
		';
	}

	/**
	 * AJAX handler for dismissing notice permanently.
	 *
	 * @since 1.0.0
	 * @return void
	 */
	public function ajax_dismiss_notice() {
		check_ajax_referer( 'aicw_notices_nonce', 'nonce' );

		if ( ! current_user_can( 'manage_options' ) ) {
			wp_send_json_error( array( 'message' => __( 'Permission denied.', 'ai-content-writer' ) ) );
		}

		// Get notice ID.
		$notice_id = isset( $_POST['notice_id'] ) ? sanitize_text_field( wp_unslash( $_POST['notice_id'] ) ) : '';

		if ( empty( $notice_id ) ) {
			wp_send_json_error( array( 'message' => __( 'Invalid notice ID.', 'ai-content-writer' ) ) );
		}

		// Save dismissed status.
		update_option( self::OPTION_PREFIX . $notice_id . '_dismissed', true, false );

		// Remove remind later option if exists.
		delete_option( self::OPTION_PREFIX . $notice_id . '_reminded_until' );

		wp_send_json_success( array( 'message' => __( 'Notice dismissed successfully.', 'ai-content-writer' ) ) );
	}

	/**
	 * AJAX handler for remind me later.
	 *
	 * @since 1.0.0
	 * @return void
	 */
	public function ajax_remind_later_notice() {
		check_ajax_referer( 'aicw_notices_nonce', 'nonce' );

		if ( ! current_user_can( 'manage_options' ) ) {
			wp_send_json_error( array( 'message' => __( 'Permission denied.', 'ai-content-writer' ) ) );
		}

		// Get notice ID.
		$notice_id = isset( $_POST['notice_id'] ) ? sanitize_text_field( wp_unslash( $_POST['notice_id'] ) ) : '';

		if ( empty( $notice_id ) ) {
			wp_send_json_error( array( 'message' => __( 'Invalid notice ID.', 'ai-content-writer' ) ) );
		}

		// Get notice data to check remind_days.
		$notices     = $this->get_notices();
		$notice_data = null;
		foreach ( $notices as $notice ) {
			if ( $notice['id'] === $notice_id ) {
				$notice_data = $notice;
				break;
			}
		}

		// Default remind after 2 days.
		$remind_days  = isset( $notice_data['remind_days'] ) ? absint( $notice_data['remind_days'] ) : 2;
		$remind_until = time() + ( $remind_days * DAY_IN_SECONDS );

		// Save remind later status.
		update_option( self::OPTION_PREFIX . $notice_id . '_reminded_until', $remind_until, false );

		wp_send_json_success( array( 'message' => __( 'You will be reminded later.', 'ai-content-writer' ) ) );
	}
}
