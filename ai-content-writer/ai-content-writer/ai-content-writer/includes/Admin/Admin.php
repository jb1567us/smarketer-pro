<?php

namespace AIContentWriter\Admin;

use AIContentWriter\Admin\ListTables\CampaignsListTable;
use AIContentWriter\Admin\ListTables\LogsListTable;

defined( 'ABSPATH' ) || exit; // Exit if accessed directly.

/**
 * The main admin class.
 *
 * @since 1.0.0
 * @package AIContentWriter\Admin
 */
class Admin {

	/**
	 * Constructor.
	 */
	public function __construct() {
		// Add admin menu.
		add_action( 'admin_menu', array( $this, 'admin_menu' ) );
		// Add Campaigns sub menu.
		add_action( 'admin_menu', array( $this, 'campaigns_menu' ) );
		// Add Generate Content sub menu.
		add_action( 'admin_menu', array( $this, 'generate_content_menu' ) );
		// Add Logs sub menu.
		add_action( 'admin_menu', array( $this, 'logs_menu' ) );
		// Add Settings sub menu.
		add_action( 'admin_menu', array( $this, 'settings_menu' ) );
		// Add Help sub menu.
		add_action( 'admin_menu', array( $this, 'help_menu' ) );
		// Add screen options.
		add_filter( 'set-screen-option', array( $this, 'screen_option' ), 10, 3 );
		// Load campaigns page.
		add_action( 'load-ai-content-writer_page_aicw-campaigns', array( $this, 'handle_campaigns_table_actions' ) );
		// Lod logs page.
		add_action( 'load-ai-content-writer_page_aicw-logs', array( $this, 'handle_logs_table_actions' ) );
		// Inject content in admin header.
		add_action( 'in_admin_header', array( __CLASS__, 'in_admin_header' ) );
		// Enqueue admin scripts.
		add_action( 'admin_enqueue_scripts', array( __CLASS__, 'enqueue_scripts' ) );
	}

	/**
	 * Add admin menu.
	 *
	 * @since 1.0.0
	 * @return void
	 */
	public function admin_menu() {
		add_menu_page(
			__( 'AI Content Writer', 'ai-content-writer' ),
			__( 'AI Content Writer', 'ai-content-writer' ),
			'manage_options',
			'ai-content-writer',
			null,
			'dashicons-edit-page',
			25,
		);

		// Add dashboard menu page as submenu of AI Content Writer.
		add_submenu_page(
			'ai-content-writer',
			__( 'Dashboard', 'ai-content-writer' ),
			__( 'Dashboard', 'ai-content-writer' ),
			'manage_options',
			'ai-content-writer',
			array( $this, 'dashboard_page' ),
		);
	}

	/**
	 * Admin Dashboard page.
	 *
	 * @since 1.5.0
	 * @return void
	 */
	public function dashboard_page() {
		// Include the dashboard view.
		include __DIR__ . '/views/dashboard.php';
	}

	/**
	 * Add campaigns menu.
	 *
	 * @since 1.0.0
	 * @return void
	 */
	public function campaigns_menu() {
		$load = add_submenu_page(
			'ai-content-writer',
			__( 'Campaigns', 'ai-content-writer' ),
			__( 'Campaigns', 'ai-content-writer' ),
			'manage_options',
			'aicw-campaigns',
			array( $this, 'campaigns_page' ),
		);

		// Load screen options.
		add_action( 'load-' . $load, array( __CLASS__, 'load_pages' ) );
	}

	/**
	 * Add generate content menu.
	 *
	 * @since 1.0.0
	 * @return void
	 */
	public function generate_content_menu() {
		add_submenu_page(
			'ai-content-writer',
			__( 'Generate Content', 'ai-content-writer' ),
			__( 'Generate Content', 'ai-content-writer' ),
			'manage_options',
			'aicw-generate-content',
			array( $this, 'generate_content_page' ),
		);
	}

	/**
	 * Add logs menu.
	 *
	 * @since 2.0.6
	 * @return void
	 */
	public function logs_menu() {
		$load = add_submenu_page(
			'ai-content-writer',
			__( 'Logs', 'ai-content-writer' ),
			__( 'Logs', 'ai-content-writer' ),
			'manage_options',
			'aicw-logs',
			array( $this, 'logs_page' ),
		);

		// Load screen options.
		add_action( 'load-' . $load, array( __CLASS__, 'load_pages' ) );
	}

	/**
	 * Add settings menu.
	 *
	 * @since 1.0.0
	 * @return void
	 */
	public function settings_menu() {
		add_submenu_page(
			'ai-content-writer',
			__( 'Settings', 'ai-content-writer' ),
			__( 'Settings', 'ai-content-writer' ),
			'manage_options',
			'aicw-settings',
			array( $this, 'settings_page' ),
		);
	}

	/**
	 * Add help menu.
	 *
	 * @since 1.0.0
	 * @return void
	 */
	public function help_menu() {
		add_submenu_page(
			'ai-content-writer',
			__( 'Help', 'ai-content-writer' ),
			__( 'Help', 'ai-content-writer' ),
			'manage_options',
			'aicw-help',
			array( $this, 'help_page' ),
		);
	}

	/**
	 * Set screen option.
	 *
	 * @param mixed  $status Screen option value. Default false.
	 * @param string $option Option name.
	 * @param mixed  $value New option value.
	 *
	 * @since 1.0.0
	 * @return mixed
	 */
	public function screen_option( $status, $option, $value ) {
		$options = apply_filters(
			'aicw_set_screen_options',
			array(
				'aicw_campaigns_per_page',
				'aicw_logs_per_page',
			)
		);
		if ( in_array( $option, $options, true ) ) {
			return $value;
		}

		return $status;
	}

	/**
	 * Load pages & set screen options.
	 *
	 * @since 1.0.0
	 * @return void
	 */
	public static function load_pages() {
		$screen = get_current_screen();
		if ( 'ai-content-writer_page_aicw-campaigns' === $screen->id ) {
			add_screen_option(
				'per_page',
				array(
					'label'   => __( 'Campaigns per page', 'ai-content-writer' ),
					'default' => 20,
					'option'  => 'aicw_campaigns_per_page',
				)
			);
		}

		if ( 'ai-content-writer_page_aicw-logs' === $screen->id ) {
			add_screen_option(
				'per_page',
				array(
					'label'   => __( 'Logs per page', 'ai-content-writer' ),
					'default' => 20,
					'option'  => 'aicw_logs_per_page',
				)
			);
		}
	}

	/**
	 * Determine if current page is add screen.
	 *
	 * @since 1.0.0
	 * @return bool
	 */
	public static function is_add_screen() {
		return filter_input( INPUT_GET, 'add' ) !== null;
	}

	/**
	 * Determine if current page is edit screen.
	 *
	 * @since 1.0.0
	 * @return false|int False if not edit screen, id if edit screen.
	 */
	public static function is_edit_screen() {
		return filter_input( INPUT_GET, 'edit', FILTER_VALIDATE_INT );
	}

	/**
	 * Campaigns page.
	 *
	 * @since 1.0.0
	 * @return void
	 */
	public function campaigns_page() {
		wp_verify_nonce( '_nonce' );

		$edit     = self::is_edit_screen();
		$campaign = get_post( $edit );

		if ( ! empty( $campaign ) && ! $campaign instanceof \WP_Post ) {
			wp_safe_redirect( remove_query_arg( 'edit' ) );
			exit();
		}

		if ( self::is_add_screen() ) {
			include __DIR__ . '/views/add-campaign.php';
		} elseif ( $edit ) {
			include __DIR__ . '/views/edit-campaign.php';
		} else {
			$list_table = new CampaignsListTable();
			$list_table->prepare_items();
			include __DIR__ . '/views/campaigns.php';
		}
	}

	/**
	 * Logs page.
	 *
	 * @since 2.0.6
	 * @return void
	 */
	public function logs_page() {
		$list_table = new LogsListTable();
		$list_table->prepare_items();
		include __DIR__ . '/views/logs.php';
	}

	/**
	 * Generate content page.
	 *
	 * @since 1.0.0
	 * @return void
	 */
	public function generate_content_page() {
		wp_verify_nonce( '_nonce' );
		$is_featured_image = filter_input( INPUT_GET, 'featured_image', FILTER_VALIDATE_INT );
		$post_id           = filter_input( INPUT_GET, 'post_id', FILTER_VALIDATE_INT );

		if ( $is_featured_image && $post_id ) {
			// Get the post object.
			$post = get_post( $post_id );
			include __DIR__ . '/views/featured-image.php';
		} else {
			// Include the admin view.
			include __DIR__ . '/views/generate-content.php';
		}
	}

	/**
	 * Settings page.
	 *
	 * @since 1.0.0
	 * @return void
	 */
	public function settings_page() {
		$settings_tabs = apply_filters(
			'aicw_settings_tabs',
			array(
				'general' => __( 'General', 'ai-content-writer' ),
				'api'     => __( 'API Settings', 'ai-content-writer' ),
			)
		);

		include __DIR__ . '/views/settings.php';
	}

	/**
	 * Help page.
	 *
	 * @since 1.0.0
	 * @return void
	 */
	public function help_page() {
		include __DIR__ . '/views/help.php';
	}

	/**
	 * Handle campaigns list table actions.
	 *
	 * @since 1.0.0
	 * @return void
	 */
	public function handle_campaigns_table_actions() {
		if ( ! current_user_can( 'manage_options' ) ) {
			ai_content_writer()->flash_notice( esc_html__( 'You do not have permission to perform this action.', 'ai-content-writer' ), 'error' );
			$redirect_url = remove_query_arg( array( 'action', 'action2', 'ids', '_wpnonce', '_wp_http_referer' ) );
			wp_safe_redirect( $redirect_url );
			exit;
		}

		$list_table = new CampaignsListTable();
		$list_table->process_bulk_action();

		if ( 'delete' === $list_table->current_action() ) {
			check_admin_referer( 'bulk-campaigns' );

			$ids       = isset( $_GET['ids'] ) ? map_deep( wp_unslash( $_GET['ids'] ), 'intval' ) : array();
			$ids       = wp_parse_id_list( $ids );
			$performed = 0;

			foreach ( $ids as $id ) {
				$shortcode = get_post( $id );
				if ( $shortcode && wp_delete_post( $shortcode->ID, true ) ) {
					++$performed;
				}
			}

			if ( ! empty( $performed ) ) {
				// translators: %s: number of accounts.
				ai_content_writer()->flash_notice( sprintf( esc_html__( '%s item(s) deleted successfully.', 'ai-content-writer' ), number_format_i18n( $performed ) ) );
			}

			if ( ! headers_sent() ) {
				// Redirect to avoid resubmission.
				$redirect_url = remove_query_arg( array( 'action', 'action2', 'ids', '_wpnonce', '_wp_http_referer' ) );
				wp_safe_redirect( $redirect_url );
				exit;
			}
		}
	}

	/**
	 * Handle logs list table actions.
	 *
	 * @since 2.0.6
	 * @return void
	 */
	public function handle_logs_table_actions() {
		if ( ! current_user_can( 'manage_options' ) ) {
			ai_content_writer()->flash_notice( esc_html__( 'You do not have permission to perform this action.', 'ai-content-writer' ), 'error' );
			$redirect_url = remove_query_arg( array( 'action', 'action2', 'ids', '_wpnonce', '_wp_http_referer' ) );
			wp_safe_redirect( $redirect_url );
			exit;
		}

		$list_table = new LogsListTable();
		$list_table->process_bulk_action();

		if ( 'delete' === $list_table->current_action() ) {
			check_admin_referer( 'bulk-logs' );

			$ids       = isset( $_GET['ids'] ) ? map_deep( wp_unslash( $_GET['ids'] ), 'intval' ) : array();
			$ids       = wp_parse_id_list( $ids );
			$performed = 0;

			foreach ( $ids as $id ) {
				$log = get_post( $id );
				if ( $log && wp_delete_post( $log->ID, true ) ) {
					++$performed;
				}
			}

			if ( ! empty( $performed ) ) {
				// translators: %s: number of accounts.
				ai_content_writer()->flash_notice( sprintf( esc_html__( '%s item(s) deleted successfully.', 'ai-content-writer' ), number_format_i18n( $performed ) ) );
			}

			if ( ! headers_sent() ) {
				// Redirect to avoid resubmission.
				$redirect_url = remove_query_arg( array( 'action', 'action2', 'ids', '_wpnonce', '_wp_http_referer' ) );
				wp_safe_redirect( $redirect_url );
				exit;
			}
		}
	}

	/**
	 * Get screen ids.
	 *
	 * @since 1.0.0
	 * @return array
	 */
	public static function get_screen_ids() {
		return array(
			'toplevel_page_ai-content-writer',
			'ai-content-writer_page_aicw-campaigns',
			'ai-content-writer_page_aicw-logs',
			'ai-content-writer_page_aicw-settings',
			'ai-content-writer_page_aicw-help',
			'ai-content-writer_page_aicw-generate-content',
		);
	}

	/**
	 * Inject content in admin header.
	 *
	 * @since 1.0.0
	 * @return void
	 */
	public static function in_admin_header() {
		$current_screen = get_current_screen()->id;
		$screens        = self::get_screen_ids();
		if ( in_array( $current_screen, $screens, true ) ) {
			$icon_url   = AICW_ASSETS_URL . 'images/plugin-icon.png';
			$is_premium = defined( 'AICW_PRO_VERSION' ) ? true : false;
			include __DIR__ . '/views/admin-header.php';
		}
	}

	/**
	 * Enqueue admin scripts.
	 *
	 * @param string $hook The current page ID.
	 *
	 * @since 1.0.0
	 * @return void
	 */
	public static function enqueue_scripts( $hook ) {
		$screens = self::get_screen_ids();

		if ( in_array( $hook, $screens, true ) ) {
			wp_enqueue_style( 'aicw-admin', AICW_ASSETS_URL . 'css/aicw-admin.css', array(), AICW_VERSION );
			wp_enqueue_script( 'aicw-admin', AICW_ASSETS_URL . 'js/aicw-admin.js', array( 'jquery' ), AICW_VERSION, true );

			// Localizations..
			wp_localize_script(
				'aicw-admin',
				'aicw_object',
				array(
					'ajax_url' => admin_url( 'admin-ajax.php' ),
					'nonce'    => wp_create_nonce( 'aicw_nonce' ),
				)
			);
		}

		// Enqueue Chart.js.
		if ( 'toplevel_page_ai-content-writer' === $hook ) {
			wp_register_script( 'aicw-chart', AICW_ASSETS_URL . 'js/chart.js', array( 'jquery' ), AICW_VERSION, true );
			wp_enqueue_script( 'aicw-chart-js', AICW_ASSETS_URL . 'js/aicw-chart.js', array( 'aicw-chart', 'jquery' ), AICW_VERSION, true );

			// Localizations.
			wp_localize_script(
				'aicw-chart-js',
				'aicw_statistics_object',
				array(
					'ajax_url' => admin_url( 'admin-ajax.php' ),
					'nonce'    => wp_create_nonce( 'aicw_nonce' ),
				)
			);
		}
	}
}
