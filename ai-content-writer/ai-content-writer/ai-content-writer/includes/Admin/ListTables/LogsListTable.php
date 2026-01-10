<?php

namespace AIContentWriter\Admin\ListTables;

defined( 'ABSPATH' ) || exit; // Exit if accessed directly.

// WP_List_Table is not loaded automatically, so we need to load it in our application.
if ( ! class_exists( 'WP_List_Table' ) ) {
	require_once ABSPATH . 'wp-admin/includes/class-wp-list-table.php';
}

/**
 * Class LogsListTable.
 *
 * @since 2.0.6
 * @package AIContentWriter\Admin\ListTables
 */
class LogsListTable extends \WP_List_Table {

	/**
	 * Constructor.
	 *
	 * @since 2.0.6
	 */
	public function __construct() {
		$this->screen = get_current_screen();
		parent::__construct(
			array(
				'singular' => 'log',
				'plural'   => 'logs',
				'ajax'     => false,
			)
		);
	}

	/**
	 * Prepare items.
	 *
	 * @since 2.0.6
	 * @return void
	 */
	public function prepare_items() {
		wp_verify_nonce( '_wpnonce' );
		$columns               = $this->get_columns();
		$hidden                = $this->get_hidden_columns();
		$sortable              = $this->get_sortable_columns();
		$this->_column_headers = array( $columns, $hidden, $sortable );
		$per_page              = $this->get_items_per_page( 'aicw_logs_per_page', 20 );
		$paged                 = $this->get_pagenum();
		$order_by              = isset( $_GET['orderby'] ) ? sanitize_text_field( wp_unslash( $_GET['orderby'] ) ) : '';
		$order                 = isset( $_GET['order'] ) ? sanitize_text_field( wp_unslash( $_GET['order'] ) ) : '';

		$args = array(
			'post_type'      => 'aicw_log',
			'posts_per_page' => $per_page,
			'paged'          => $paged,
			'orderby'        => $order_by,
			'order'          => $order,
			'post_status'    => 'any',
		);

		/**
		 * Filter the query arguments for the list table.
		 *
		 * @param array $args An associative array of arguments.
		 *
		 * @since 2.0.6
		 */
		$args = apply_filters( 'aicw_logs_table_query_args', $args );

		$this->items = get_posts( $args );
		$total       = count(
			get_posts(
				array(
					'post_type'      => 'aicw_log',
					'posts_per_page' => -1,
					'post_status'    => 'any',
					'fields'         => 'ids',
				)
			)
		);

		$this->set_pagination_args(
			array(
				'total_items' => $total,
				'per_page'    => $per_page,
			)
		);
	}

	/**
	 * No items found text.
	 *
	 * @since 2.0.6
	 * @return void
	 */
	public function no_items() {
		esc_html_e( 'No logs found.', 'ai-content-writer' );
	}


	/**
	 * Get the table columns
	 *
	 * @return array
	 * @since 2.0.6
	 */
	public function get_columns() {
		$columns = array(
			'cb'            => '<input type="checkbox" />',
			'type'          => __( 'Type', 'ai-content-writer' ),
			'log'           => __( 'Log', 'ai-content-writer' ),
			'related_event' => __( 'Related Event', 'ai-content-writer' ),
			'date'          => __( 'Date', 'ai-content-writer' ),
		);

		return $columns;
	}

	/**
	 * Get hidden columns.
	 */
	public function get_hidden_columns() {
		return get_hidden_columns( get_current_screen() );
	}

	/**
	 * Get sortable columns.
	 */
	public function get_sortable_columns() {
		return array(
			'type' => array( 'post_title', true ),
			'date' => array( 'date', true ),
		);
	}

	/**
	 * Get primary columns name. or define the primary column name.
	 */
	public function get_primary_column_name() {
		return 'type';
	}

	/**
	 * Renders the checkbox column in the items list table.
	 *
	 * @param Object $item The current master key object.
	 *
	 * @return string Displays a checkbox.
	 * @since  1.0.0
	 */
	public function column_cb( $item ) {
		return sprintf( '<input type="checkbox" name="ids[]" value="%d"/>', esc_attr( $item->ID ) );
	}

	/**
	 * Renders the master_key column in the items list table.
	 *
	 * @param Object $item The current master key object.
	 *
	 * @return string Displays the Master key.
	 * @since  1.0.0
	 */
	public function column_type( $item ) {
		$delete_url = add_query_arg(
			array(
				'ids'    => $item->ID,
				'action' => 'delete',
			),
			admin_url( 'admin.php?page=aicw-logs' )
		);
		$item_title = esc_html( $item->post_title );
		// translators: %d: key id.
		$actions['ids']    = sprintf( __( 'ID: %d', 'ai-content-writer' ), esc_html( $item->ID ) );
		$actions['delete'] = sprintf( '<a href="%1$s">%2$s</a>', wp_nonce_url( $delete_url, 'bulk-' . $this->_args['plural'] ), __( 'Delete', 'ai-content-writer' ) );

		return sprintf( '%1$s %2$s', $item_title, $this->row_actions( $actions ) );
	}

	/**
	 * Get bulk actions.
	 *
	 * @since 2.0.6
	 * @return array
	 */
	public function get_bulk_actions() {
		return array(
			'delete' => __( 'Delete', 'ai-content-writer' ),
		);
	}

	/**
	 * Display column description.
	 *
	 * @param Object $item Item.
	 *
	 * @since 2.0.6
	 * @return string Description.
	 */
	protected function column_log( $item ) {
		return wp_kses_post( $item->post_content ?? '&mdash;' );
	}

	/**
	 * Display column related_event.
	 *
	 * @param Object $item Item.
	 *
	 * @since 2.0.6
	 * @return string Related Event.
	 */
	protected function column_related_event( $item ) {
		$value            = '&mdash;';
		$related_campaign = absint( get_post_meta( $item->ID, '_aicw_related_campaign', true ) );

		if ( $related_campaign ) {
			$campaign_title = get_the_title( $related_campaign );
			$campaign_link  = add_query_arg(
				array(
					'page' => 'aicw-campaigns',
					'edit' => $related_campaign,
				),
				admin_url( 'admin.php' )
			);
			if ( $campaign_title && $campaign_link ) {
				$value = sprintf( '<a href="%s">%s</a>', esc_url( $campaign_link ), esc_html( $campaign_title ) );
			}
		}

		return wp_kses_post( $value );
	}

	/**
	 * Display column date.
	 *
	 * @param Object $item Item.
	 *
	 * @since 2.0.6
	 * @return string Date.
	 */
	protected function column_date( $item ) {
		$value = '&mdash;';
		$date  = $item->post_date;
		if ( $date ) {
			$value = sprintf( '<time datetime="%s">%s</time>', esc_attr( $date ), esc_html( date_i18n( get_option( 'date_format' ) . ' | ' . get_option( 'time_format' ), strtotime( $date ) ) ) );
		}

		return wp_kses_post( $value );
	}
}
