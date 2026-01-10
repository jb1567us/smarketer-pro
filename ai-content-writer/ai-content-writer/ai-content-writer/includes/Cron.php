<?php

namespace AIContentWriter;

use AIContentWriter\Campaigns\Articles;
use AIContentWriter\Campaigns\RSSFeed;

defined( 'ABSPATH' ) || exit; // Exit if accessed directly.

/**
 * Class Cron
 *
 * @since 1.4.0
 * @package AIContentWriter
 */
class Cron {

	/**
	 * Cron constructor.
	 */
	public function __construct() {
		add_action( 'init', array( $this, 'schedule_cron' ) );
		add_filter( 'cron_schedules', array( __CLASS__, 'add_cron_intervals' ) );

		// Execute cron job to generate titles, content & thumbnails.
		add_action( 'aicw_generate_title', array( __CLASS__, 'generate_titles' ) );
		add_action( 'aicw_generate_content', array( __CLASS__, 'generate_content' ) );
		add_action( 'aicw_generate_thumbnail', array( __CLASS__, 'generate_thumbnails' ) );
		add_action( 'aicw_publish_posts', array( __CLASS__, 'publish_posts' ) );
		add_action( 'aicw_cleanup_logs', array( __CLASS__, 'cleanup_logs' ) );
	}

	/**
	 * Schedule cron.
	 *
	 * @since 1.4.0
	 * @return void
	 */
	public function schedule_cron() {
		// Add a filter hook to check the campaign frequency.
		$frequency = apply_filters( 'aicw_campaign_frequency', 'hourly' );

		// Schedule the cron job for generating titles.
		if ( ! wp_next_scheduled( 'aicw_generate_title' ) ) {
			wp_schedule_event( time(), $frequency, 'aicw_generate_title' );
		}

		// Schedule the cron job for generating content.
		if ( ! wp_next_scheduled( 'aicw_generate_content' ) ) {
			wp_schedule_event( time() + 300, $frequency, 'aicw_generate_content' );
		}

		// Schedule the cron job for generating thumbnails.
		if ( ! wp_next_scheduled( 'aicw_generate_thumbnail' ) ) {
			wp_schedule_event( time() + 600, $frequency, 'aicw_generate_thumbnail' );
		}

		// Schedule the cron job for publishing the generated posts.
		if ( ! wp_next_scheduled( 'aicw_publish_posts' ) ) {
			wp_schedule_event( time() + 900, $frequency, 'aicw_publish_posts' );
		}

		// Schedule the cron job for cleaning up old logs.
		if ( ! wp_next_scheduled( 'aicw_cleanup_logs' ) ) {
			wp_schedule_event( time() + 1200, 'daily', 'aicw_cleanup_logs' );
		}
	}

	/**
	 * Add custom cron intervals.
	 *
	 * @param array $schedules The existing cron schedules.
	 *
	 * @since 2.0.5
	 * @return array The modified cron schedules.
	 */
	public static function add_cron_intervals( $schedules ) {
		$schedules['aicw_15_minutes'] = array(
			'interval' => 900, // 15 minutes in seconds.
			'display'  => __( 'Every 15 Minutes', 'ai-content-writer' ),
		);
		$schedules['aicw_30_minutes'] = array(
			'interval' => 1800, // 30 minutes in seconds.
			'display'  => __( 'Every 30 Minutes', 'ai-content-writer' ),
		);

		return $schedules;
	}

	/**
	 * Generate titles.
	 *
	 * @param array $args The arguments.
	 *
	 * @since 1.4.0
	 * @return void
	 */
	public static function generate_titles( $args = array() ) {
		$defaults = array(
			'posts_per_page' => -1,
			'orderby'        => 'modified',
			'order'          => 'ASC',
			'post_status'    => 'publish',
		);

		$args = wp_parse_args( $args, $defaults );

		// Get campaigns.
		$campaigns = aicw_get_campaigns( $args );

		// Loop through each campaign.
		foreach ( $campaigns as $campaign ) {
			// Get the content.
			$campaign_id = $campaign->ID;

			// Get the content.
			$keywords = $campaign->post_content;

			// Check if the campaign needs generating titles.
			$needs_update = aicw_campaign_needs_update( $campaign_id );

			if ( array_key_exists( 'needs_update', $needs_update ) && ! $needs_update['needs_update'] ) {
				aicw_update_last_run_time( $campaign_id );
				continue;
			}

			$type         = get_post_meta( $campaign_id, '_aicw_campaign_type', true );
			$posts_needed = isset( $needs_update['posts_needed'] ) ? absint( $needs_update['posts_needed'] ) : 0;

			if ( 'articles' === $type ) {
				Articles::generate_titles( $campaign_id, $keywords, $posts_needed );
				// Update the last run time.
				aicw_update_last_run_time( $campaign_id );
				break;
			} elseif ( 'rss-feed' === $type ) {
				RSSFeed::generate_titles( $campaign_id, $posts_needed );
				// Update the last run time.
				aicw_update_last_run_time( $campaign_id );
				break;
			} else {
				// Now request the AI Model to generate the titles depending on the keywords.
				$type   = empty( $type ) ? get_option( 'aicw_api_model' ) : $type; // TODO: We will remove this option in the future. It's already remove from the settings page.
				$titles = aicw_generate_titles( $type, $keywords, $posts_needed );
			}

			$counter = 0;
			// Create a new post for each title.
			foreach ( $titles as $title ) {
				if ( empty( $title ) ) {
					continue;
				}

				// Check if the line starts with a number followed by a dot and space OR dash and space (e.g., "10. " OR "- "). If not then skip the line.
				if ( ! preg_match( '/^(\d+\.\s|- )/', $title ) ) {
					continue;
				}

				// Remove leading number, dot, and space OR dash/space (e.g., "10. " OR "- ").
				$title = preg_replace( '/^(\d+\.\s*|- )/', '', $title );

				// Remove surrounding quotes if present.
				$title = trim( $title, '"' );

				// Check if the title already exists.
				$post_exists = aicw_get_post_by_title( $title );

				if ( $post_exists ) {
					continue;
				}

				// Create a new post.
				$post_id = wp_insert_post(
					array(
						'post_type'    => 'aicw_post',
						'post_title'   => $title,
						'post_content' => '',
						'post_status'  => 'pending',
						'post_author'  => get_post_field( 'post_author', $campaign_id ),
					)
				);

				if ( is_wp_error( $post_id ) ) {
					continue;
				}

				// Add the post meta.
				update_post_meta( $post_id, '_aicw_campaign_id', $campaign_id );

				// Update the counter.
				++$counter;

				// If the counter is greater than or equal to the target then break the loop.
				if ( array_key_exists( 'posts_needed', $needs_update ) && $counter >= $needs_update['posts_needed'] ) {
					ai_content_writer()->create_log( sprintf( /* translators: 1: Number of posts created. 2: Campaign ID. 3: Campaign Title. */ esc_html__( 'Created %1$d posts for campaign ID %2$d with title "%3$s".', 'ai-content-writer' ), esc_html( $counter ), esc_html( $campaign_id ), get_the_title( $campaign_id ) ), 'success', $campaign_id );
					break;
				}
			}

			// Update the last run time.
			aicw_update_last_run_time( $campaign_id );

			break; // Break the loop to process only one campaign at a time.
		}
	}

	/**
	 * Generate content.
	 *
	 * @param array $args The arguments.
	 *
	 * @since 1.4.0
	 * @return void
	 */
	public static function generate_content( $args = array() ) {
		$defaults = array(
			'post_type'      => 'aicw_post',
			'posts_per_page' => -1,
			'orderby'        => 'modified',
			'order'          => 'ASC',
			'post_status'    => 'pending',
		);

		$args = wp_parse_args( $args, $defaults );

		// Get all posts.
		$posts = get_posts( $args );

		// Loop through each post.
		foreach ( $posts as $post ) {
			// Get the content.
			$post_id = $post->ID;

			// Get the associated campaign ID.
			$campaign_id = get_post_meta( $post_id, '_aicw_campaign_id', true );

			// Delete the post as it is not associated with any campaign.
			if ( empty( $campaign_id ) || ! aicw_get_campaign( $campaign_id ) ) {
				wp_delete_post( $post_id, true );
				continue;
			}

			// Check if the post needs generating content.
			$needs_update = aicw_temp_post_needs_update( $post, $campaign_id );

			if ( empty( $needs_update ) || ( array_key_exists( 'content', $needs_update ) && ! $needs_update['content'] ) ) {
				aicw_update_last_run_time( $post_id );
				continue;
			}

			// Get the keywords.
			$keywords = get_post_field( 'post_content', $campaign_id );

			// Get the title.
			$title = get_the_title( $post_id );

			if ( empty( $title ) ) {
				continue;
			}

			$campaign_type = get_post_meta( $campaign_id, '_aicw_campaign_type', true );

			if ( empty( $campaign_type ) ) {
				continue;
			}

			// Check if the campaign type is articles or rss-feed.
			if ( 'articles' === $campaign_type ) {
				$is_updated = Articles::generate_content( $post_id, $title, $keywords );
			} elseif ( 'rss-feed' === $campaign_type ) {
				$is_updated = RSSFeed::generate_content( $post_id, $title, $keywords );
			} else {
				$content = aicw_generate_content( $post_id, $title, $keywords );
				$updated = wp_update_post(
					array(
						'ID'           => $post_id,
						'post_content' => wp_kses_post( $content ),
					)
				);

				$is_updated = is_wp_error( $updated ) ? false : true;
			}

			// Check if the content is updated successfully or not.
			if ( ! $is_updated ) {
				// If the content is not updated then handle the iteration occurring. and delete it if the post is not updated with 2 attempts.
				$attempts = get_post_meta( $post_id, '_aicw_generate_content_attempts', true );
				if ( empty( $attempts ) ) {
					$attempts = 0;
				}

				++$attempts;
				// Check if the attempts are greater than or equal to 2 then delete the post.
				if ( $attempts >= 2 ) {
					ai_content_writer()->create_log( sprintf( /* translators: 1: Post ID. 2: Post Title. */ esc_html__( 'Failed to generate content for post ID %1$d with title "%2$s" after %3$d attempts. Deleting the post.', 'ai-content-writer' ), esc_html( $post_id ), get_the_title( $post_id ), esc_html( $attempts ) ), 'error', $campaign_id );
					wp_delete_post( $post_id, true );
					continue;
				} else {
					update_post_meta( $post_id, '_aicw_generate_content_attempts', $attempts );
				}
			}

			// Update the last run time.
			aicw_update_last_run_time( $post_id );

			ai_content_writer()->create_log( sprintf( /* translators: 1: Post ID. 2: Post Title. */ esc_html__( 'Generated content for post ID %1$d with title "%2$s".', 'ai-content-writer' ), esc_html( $post_id ), get_the_title( $post_id ) ), 'success', $campaign_id );
			break; // Break the loop to process only one post at a time.
		}
	}

	/**
	 * Generate thumbnails.
	 *
	 * @param array $args The arguments.
	 *
	 * @since 1.4.0
	 * @return void
	 */
	public static function generate_thumbnails( $args = array() ) {
		$defaults = array(
			'post_type'      => 'aicw_post',
			'posts_per_page' => -1,
			'orderby'        => 'modified',
			'order'          => 'ASC',
			'post_status'    => 'pending',
		);

		$args = wp_parse_args( $args, $defaults );

		// Get all posts.
		$posts = get_posts( $args );

		// Loop through each post.
		foreach ( $posts as $post ) {
			// Get the content.
			$post_id = $post->ID;

			// Get the associated campaign ID.
			$campaign_id = get_post_meta( $post_id, '_aicw_campaign_id', true );

			// Delete the post as it is not associated with any campaign.
			if ( empty( $campaign_id ) || ! aicw_get_campaign( $campaign_id ) ) {
				wp_delete_post( $post_id, true );
				continue;
			}

			// Check if the post needs generating thumbnail.
			$needs_update = aicw_temp_post_needs_update( $post, $campaign_id );

			if ( empty( $needs_update ) || ( array_key_exists( 'thumbnail', $needs_update ) && ! $needs_update['thumbnail'] ) ) {
				aicw_update_last_run_time( $post_id );
				continue;
			}

			// Get the title.
			$title = get_the_title( $post_id );

			if ( empty( $title ) ) {
				continue;
			}

			// Now request the OpenAI to generate the thumbnail depending on the title and content.
			$images = ai_content_writer()->generate_images( $title );

			if ( is_wp_error( $images ) ) {
				continue;
			}

			if ( empty( $images ) ) {
				continue;
			}

			// Get a random image.
			$thumbnail = $images[ array_rand( $images ) ];

			if ( ! isset( $thumbnail['src']['original'] ) ) {
				continue;
			}

			// Get the media URL.
			$media_url = $thumbnail['src']['original'];

			// Check if the media side load function exists. If not then include the required files.
			if ( ! function_exists( 'media_sideload_image' ) ) {
				require_once ABSPATH . 'wp-admin/includes/media.php';
				require_once ABSPATH . 'wp-admin/includes/file.php';
				require_once ABSPATH . 'wp-admin/includes/image.php';
			}

			// Download the image.
			$media_id = media_sideload_image( $media_url, $post_id, $title, 'id' );

			// Set the post thumbnail.
			set_post_thumbnail( $post_id, $media_id );

			// Update the last run time.
			aicw_update_last_run_time( $post_id );

			ai_content_writer()->create_log( sprintf( /* translators: 1: Post ID. 2: Post Title. */ esc_html__( 'Generated thumbnail for post ID %1$d with title "%2$s".', 'ai-content-writer' ), esc_html( $post_id ), get_the_title( $post_id ) ), 'success', $campaign_id );
			break; // Break the loop to process only one post at a time.
		}
	}

	/**
	 * Publish posts.
	 * This will publish the generated posts that are in pending status and completed all the steps.
	 *
	 * @param array $args The arguments.
	 *
	 * @since 1.4.0
	 * @return void
	 */
	public static function publish_posts( $args = array() ) {
		$defaults = array(
			'post_type'      => 'aicw_post',
			'posts_per_page' => -1,
			'orderby'        => 'modified',
			'order'          => 'ASC',
			'post_status'    => 'pending',
		);

		$args = wp_parse_args( $args, $defaults );

		// Get all posts.
		$posts = get_posts( $args );

		// Loop through each post.
		foreach ( $posts as $post ) {
			if ( ! $post && ! $post instanceof \WP_Post ) {
				continue;
			}

			// Get the content.
			$post_id = $post->ID;

			if ( empty( $post_id ) ) {
				continue;
			}

			// Get the associated campaign ID.
			$campaign_id = get_post_meta( $post_id, '_aicw_campaign_id', true );

			if ( empty( $campaign_id ) ) {
				continue;
			}

			// Check if the post needs generating thumbnail.
			$needs_update = aicw_temp_post_needs_update( $post, $campaign_id );

			if ( ! empty( $needs_update ) ) {
				continue;
			}

			// Filter the content to remove the block keywords if any.
			$content        = $post->post_content;
			$block_keywords = get_post_meta( $campaign_id, '_aicw_block_keywords', true );
			$keywords_array = array_filter( array_map( 'trim', explode( ',', $block_keywords ) ) );
			$replacements   = array_fill_keys( $keywords_array, '' );

			/*
			 * Filter the replacements array before filtering the content.
			 *
			 * @param array $replacements The replacements array.
			 * @param int   $campaign_id The campaign ID.
			 * @param int   $post_id The post ID.
			 *
			 * @since 2.0.2
			 * @return array The replacements array.
			 */
			$replacements = apply_filters( 'aicw_before_content_filtering', $replacements, $campaign_id, $post_id );

			if ( ! empty( $replacements ) && is_array( $replacements ) ) {
				$search  = array_keys( $replacements );
				$replace = array_values( $replacements );
				$content = str_replace( $search, $replace, $content );
				$content = preg_replace( '/\s+/', ' ', $content );
				$content = trim( $content );
			}

			// Insert custom content if any.
			$insert_content_position = get_post_meta( $campaign_id, '_aicw_insert_content_position', true );
			$insert_content          = get_post_meta( $campaign_id, '_aicw_insert_content', true );

			if ( ! empty( $insert_content ) && 'none' !== $insert_content_position ) {
				$content = 'before' === $insert_content_position ? $insert_content . ' ' . $content : $content . ' ' . $insert_content;
			}

			// Get the post type and status user selected in the campaign.
			$post_type   = get_post_meta( $campaign_id, '_aicw_post_type', true ) ?? 'post';
			$post_status = get_post_meta( $campaign_id, '_aicw_completed_post_status', true ) ?? 'publish';

			// Update the post type and status.
			wp_update_post(
				array(
					'ID'           => $post_id,
					'post_type'    => $post_type,
					'post_status'  => $post_status,
					'post_content' => wp_kses_post( $content ),
				)
			);

			ai_content_writer()->create_log( sprintf( /* translators: 1: Post ID. 2: Post Title. */ esc_html__( 'Published post ID %1$d with title "%2$s".', 'ai-content-writer' ), esc_html( $post_id ), get_the_title( $post_id ) ), 'success', $campaign_id );
			break; // Break the loop to process only one post at a time.
		}
	}

	/**
	 * Cleanup logs.
	 * Deletes old logs based on the retention period set in the settings.
	 *
	 * @since 2.0.6
	 * @return void
	 */
	public static function cleanup_logs() {
		$retention_period = absint( get_option( 'aicw_log_retention_period', 30 ) );
		if ( $retention_period <= 0 ) {
			return;
		}

		$cutoff_date = gmdate( 'Y-m-d', strtotime( "-{$retention_period} days" ) );
		$logs        = get_posts(
			array(
				'post_type'      => 'aicw_log',
				'posts_per_page' => -1,
				'date_query'     => array(
					array(
						'before'    => $cutoff_date,
						'inclusive' => true,
					),
				),
				'fields'         => 'ids',
				'orderby'        => 'date',
				'order'          => 'ASC',
			)
		);

		// Delete logs if found.
		if ( ! empty( $logs ) ) {
			foreach ( $logs as $log_id ) {
				wp_delete_post( $log_id, true );
			}

			ai_content_writer()->create_log( sprintf( /* translators: 1: Number of logs deleted. 2: Retention period in days. */ esc_html__( 'Deleted %1$d logs older than %2$d days.', 'ai-content-writer' ), count( $logs ), $retention_period ) );
		}
	}
}
