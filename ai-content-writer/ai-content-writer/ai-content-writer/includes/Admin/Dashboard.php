<?php

namespace AIContentWriter\Admin;

defined( 'ABSPATH' ) || exit; // Exit if accessed directly.

/**
 * Dashboard class
 *
 * @package AIContentWriter/Admin
 * @since 1.5.0
 */
class Dashboard {

	/**
	 * Dashboard constructor.
	 *
	 * @since 1.5.0
	 */
	public function __construct() {
		add_action( 'wp_ajax_aicw_get_campaign_statistics', array( __CLASS__, 'get_statistics' ) );
	}

	/**
	 * Get statistics for the dashboard.
	 *
	 * @since 1.5.0
	 * @return void
	 */
	public static function get_statistics() {
		check_ajax_referer( 'aicw_nonce', 'nonce' );

		if ( ! current_user_can( 'manage_options' ) ) {
			wp_send_json_error(
				array(
					'message' => esc_html__( 'You do not have permission to perform this action.', 'ai-content-writer' ),
				)
			);
		}

		$filter = isset( $_POST['filter'] ) ? sanitize_text_field( wp_unslash( $_POST['filter'] ) ) : 'last7days';

		if ( 'today' === $filter ) {
			$labels     = array( gmdate( 'l' ) );
			$start_date = gmdate( 'Y-m-d 00:00:00' );
			$end_date   = gmdate( 'Y-m-d 23:59:59' );
			$data       = self::get_data( $start_date, $end_date );
		} elseif ( 'last7days' === $filter ) {
			$labels = array();
			for ( $i = 6; $i >= 0; $i-- ) {
				$labels[] = gmdate( 'F, j', strtotime( "-$i days" ) );
			}

			$start_date = gmdate( 'Y-m-d 00:00:00', strtotime( '-6 days' ) );
			$end_date   = gmdate( 'Y-m-d 23:59:59' );
			$data       = self::get_data( $start_date, $end_date );
		} elseif ( 'last30days' === $filter ) {
			$labels = array();
			for ( $i = 29; $i >= 0; $i-- ) {
				$labels[] = gmdate( 'F, j', strtotime( "-$i days" ) );
			}

			$start_date = gmdate( 'Y-m-d 00:00:00', strtotime( '-29 days' ) );
			$end_date   = gmdate( 'Y-m-d 23:59:59' );
			$data       = self::get_data( $start_date, $end_date );
		} elseif ( 'lastyear' === $filter ) {
			$labels = array();
			for ( $i = 11; $i >= 0; $i-- ) {
				$labels[] = gmdate( 'F, Y', strtotime( "-$i months" ) );
			}

			$start_date = gmdate( 'Y-m-d 00:00:00', strtotime( '-11 months' ) );
			$end_date   = gmdate( 'Y-m-d 23:59:59' );
			$data       = self::get_data( $start_date, $end_date, $labels );
		} else {
			// Initialize the array.
			$labels = array();

			// Get the current year.
			$current_year = gmdate( 'Y' );

			// Query for the first published or draft post to get its year.
			$args = array(
				'post_type'      => 'post',
				'posts_per_page' => 1,
				'orderby'        => 'date',
				'order'          => 'ASC',
				'post_status'    => array( 'publish', 'pending', 'draft' ),
			);

			$first_post = new \WP_Query( $args );

			if ( $first_post->have_posts() ) {
				// Get the year of the first post.
				$first_post_year = get_the_date( 'Y', $first_post->posts[0] );
				// Generate the years range from the first post year to the current year.
				for ( $year = $first_post_year; $year <= $current_year; $year++ ) {
					$labels[] = (string) $year; // Add the year to the labels array.
				}
			} else {
				// If no posts are found, only use the current year.
				$labels[] = (string) $current_year;
			}

			$data = array(
				'published' => array(),
				'pending'   => array(),
				'draft'     => array(),
			);

			foreach ( $labels as $year ) {
				// Convert the year to a proper date format.
				$start_date = $year . '-01-01';
				$end_date   = $year . '-12-31';

				// Get the data for the year.
				$year_data = self::get_data( $start_date, $end_date );

				// Add the data to the main data array.
				$data['published'][] = array_sum( $year_data['published'] );
				$data['pending'][]   = array_sum( $year_data['pending'] );
				$data['draft'][]     = array_sum( $year_data['draft'] );
			}
		}

		// Return the data.
		wp_send_json_success(
			array(
				'labels'    => $labels,
				'published' => $data['published'],
				'pending'   => $data['pending'],
				'draft'     => $data['draft'],
			),
		);
	}

	/**
	 * Get data for the dashboard.
	 *
	 * @param string $start_date The start date.
	 * @param string $end_date The end date.
	 * @param array  $labels The labels.
	 *
	 * @since 1.5.0
	 * @return array
	 */
	public static function get_data( $start_date, $end_date, $labels = array() ) {
		global $wpdb;

		// Query posts with a non-empty "_aicw_campaign_id" within the date range.
		// phpcs:ignore WordPress.DB.DirectDatabaseQuery.DirectQuery, WordPress.DB.DirectDatabaseQuery.NoCaching
		$results = $wpdb->get_results(
			$wpdb->prepare(
				"SELECT p.ID, p.post_status, DATE(p.post_date) as post_date
        FROM {$wpdb->posts} p
        INNER JOIN {$wpdb->postmeta} pm ON p.ID = pm.post_id
        WHERE pm.meta_key = '_aicw_campaign_id'
        AND pm.meta_value != ''
        AND p.post_date BETWEEN %s AND %s",
				$start_date,
				$end_date
			),
			ARRAY_A
		);

		// Initialize arrays for published and draft posts per date.
		$published = array();
		$pending   = array();
		$draft     = array();

		// Loop through results and count posts per date.
		foreach ( $results as $post ) {
			$date = $post['post_date'];

			if ( 'publish' === $post['post_status'] ) {
				$published[ $date ] = isset( $published[ $date ] ) ? $published[ $date ] + 1 : 1;
			} elseif ( 'pending' === $post['post_status'] ) {
				$pending[ $date ] = isset( $pending[ $date ] ) ? $pending[ $date ] + 1 : 1;
			} elseif ( 'draft' === $post['post_status'] ) {
				$draft[ $date ] = isset( $draft[ $date ] ) ? $draft[ $date ] + 1 : 1;
			}
		}

		if ( ! empty( $labels ) ) {
			$data = array(
				'published' => array(),
				'pending'   => array(),
				'draft'     => array(),
			);

			foreach ( $labels as $month ) {
				// Extract month and year.
				list( $month_name, $year ) = explode( ', ', $month );

				// Convert to proper date format.
				$start_date = gmdate( 'Y-m-01', strtotime( "first day of $month_name $year" ) );
				$end_date   = gmdate( 'Y-m-t', strtotime( "last day of $month_name $year" ) );

				// Ensure every date in the range is accounted for.
				$current = strtotime( $start_date );
				$end     = strtotime( $end_date );
				$monthly = array(
					'published' => 0,
					'pending'   => 0,
					'draft'     => 0,
				);

				while ( $current <= $end ) {
					$date = gmdate( 'Y-m-d', $current );

					// Set to zero if no posts exist for the date.
					$monthly['published'] += $published[ $date ] ?? 0;
					$monthly['pending']   += $pending[ $date ] ?? 0;
					$monthly['draft']     += $draft[ $date ] ?? 0;

					$current = strtotime( '+1 day', $current );
				}

				$data['published'][] = $monthly['published'];
				$data['pending'][]   = $monthly['pending'];
				$data['draft'][]     = $monthly['draft'];
			}
		} else {

			// Ensure every date in the range is accounted for.
			$current = strtotime( $start_date );
			$end     = strtotime( $end_date );
			$data    = array(
				'published' => array(),
				'pending'   => array(),
				'draft'     => array(),
			);

			while ( $current <= $end ) {
				$date = gmdate( 'Y-m-d', $current );

				// Set to zero if no posts exist for the date.
				$data['published'][] = $published[ $date ] ?? 0;
				$data['pending'][]   = $pending[ $date ] ?? 0;
				$data['draft'][]     = $draft[ $date ] ?? 0;

				$current = strtotime( '+1 day', $current );
			}
		}

		return $data;
	}
}
