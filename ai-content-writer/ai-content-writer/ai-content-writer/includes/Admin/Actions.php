<?php

namespace AIContentWriter\Admin;

use AIContentWriter\Cron;

defined( 'ABSPATH' ) || exit; // Exit if accessed directly.

/**
 * Actions Class.
 *
 * @since 1.0.0
 * @package AIContentWriter\Admin
 */
class Actions {

	/**
	 * Constructor.
	 */
	public function __construct() {
		// Handle save settings.
		add_action( 'admin_post_aicw_save_general_settings', array( __CLASS__, 'save_general_settings' ) );
		add_action( 'admin_post_aicw_save_api_settings', array( __CLASS__, 'save_api_settings' ) );

		// Handle instant content generation.
		add_action( 'admin_post_aicw_generate_content', array( __CLASS__, 'handle_generate_content' ) );
		add_action( 'admin_post_aicw_set_featured_image', array( __CLASS__, 'handle_set_featured_image' ) );

		// Handle the campaign form submission.
		add_action( 'admin_post_aicw_add_campaign', array( __CLASS__, 'handle_add_campaign' ) );
		add_action( 'admin_post_aicw_edit_campaign', array( __CLASS__, 'handle_edit_campaign' ) );

		// Handle ajax request for deleting the campaigns temporarily post.
		add_action( 'wp_ajax_aicw_delete_temp_post', array( __CLASS__, 'handle_delete_temp_post' ) );

		// Handle ajax request for running the campaign instantly.
		add_action( 'wp_ajax_aicw_run_campaign', array( __CLASS__, 'handle_run_campaign' ) );
	}

	/**
	 * Save general settings.
	 *
	 * @since 1.0.0
	 * @return void
	 */
	public static function save_general_settings() {
		check_admin_referer( 'aicw_save_general_settings' );
		$referer = wp_get_referer();

		if ( ! current_user_can( 'manage_options' ) ) {
			ai_content_writer()->flash_notice( esc_html__( 'You do not have permission to perform this action.', 'ai-content-writer' ), 'error' );
			wp_safe_redirect( $referer );
			exit();
		}

		/*
		 * Allow third-party plugins to modify the settings before saving.
		 *
		 * @param array $settings The settings array.
		 *
		 * @since 1.7.0
		 */
		do_action( 'aicw_before_save_general_settings' );

		$allowed_hosts        = isset( $_POST['aicw_allowed_hosts'] ) ? sanitize_textarea_field( wp_unslash( $_POST['aicw_allowed_hosts'] ) ) : 'https://www.bing.com';
		$default_host         = isset( $_POST['aicw_default_host'] ) ? sanitize_text_field( wp_unslash( $_POST['aicw_default_host'] ) ) : 'https://www.bing.com/';
		$api_model            = isset( $_POST['aicw_api_model'] ) ? sanitize_text_field( wp_unslash( $_POST['aicw_api_model'] ) ) : '';
		$redirect_is_enabled  = isset( $_POST['aicw_enable_redirection'] ) ? sanitize_text_field( wp_unslash( $_POST['aicw_enable_redirection'] ) ) : '';
		$enabled_img_gen      = isset( $_POST['aicw_enable_img_generation'] ) ? sanitize_text_field( wp_unslash( $_POST['aicw_enable_img_generation'] ) ) : '';
		$log_retention_period = isset( $_POST['aicw_log_retention_period'] ) ? absint( wp_unslash( $_POST['aicw_log_retention_period'] ) ) : '';

		if ( 'https://www.bing.com' === $allowed_hosts ) {
			update_option( 'aicw_allowed_hosts', $allowed_hosts );
		}
		update_option( 'aicw_default_host', $default_host );
		update_option( 'aicw_api_model', $api_model );
		update_option( 'aicw_enable_redirection', $redirect_is_enabled );
		update_option( 'aicw_enable_img_generation', $enabled_img_gen );
		update_option( 'aicw_log_retention_period', $log_retention_period );

		ai_content_writer()->flash_notice( esc_html__( 'General settings saved successfully.', 'ai-content-writer' ), 'success' );
		wp_safe_redirect( $referer );
		exit();
	}

	/**
	 * Save API settings.
	 *
	 * @since 1.0.0
	 * @return void
	 */
	public static function save_api_settings() {
		check_admin_referer( 'aicw_save_api_settings' );
		$referer = wp_get_referer();

		if ( ! current_user_can( 'manage_options' ) ) {
			ai_content_writer()->flash_notice( esc_html__( 'You do not have permission to perform this action.', 'ai-content-writer' ), 'error' );
			wp_safe_redirect( $referer );
			exit();
		}

		$gemini_api_key         = isset( $_POST['aicw_gemini_api_key'] ) ? sanitize_text_field( wp_unslash( $_POST['aicw_gemini_api_key'] ) ) : '';
		$gemini_ai_model        = isset( $_POST['aicw_gemini_ai_model'] ) ? sanitize_text_field( wp_unslash( $_POST['aicw_gemini_ai_model'] ) ) : '';
		$chatgpt_api_secret_key = isset( $_POST['aicw_chatgpt_api_secret_key'] ) ? sanitize_text_field( wp_unslash( $_POST['aicw_chatgpt_api_secret_key'] ) ) : '';
		$chatgpt_ai_model       = isset( $_POST['aicw_chatgpt_ai_model'] ) ? sanitize_text_field( wp_unslash( $_POST['aicw_chatgpt_ai_model'] ) ) : '';
		$pexels_api_key         = isset( $_POST['aicw_pexels_api_key'] ) ? sanitize_text_field( wp_unslash( $_POST['aicw_pexels_api_key'] ) ) : '';

		// Update common options.
		update_option( 'aicw_gemini_ai_model', $gemini_ai_model );
		update_option( 'aicw_chatgpt_ai_model', $chatgpt_ai_model );
		update_option( 'aicw_pexels_api_key', $pexels_api_key );

		// Check if the Gemini API key is valid or not.
		if ( ! empty( $gemini_api_key ) ) {
			// Create Gemini service instance.
			$service = new \AIContentWriter\Services\Gemini( $gemini_api_key );

			// Call the service to get models.
			$models = $service->get_models();

			if ( is_wp_error( $models ) ) {
				ai_content_writer()->flash_notice( esc_html( 'Gemini: ' . $models->get_error_message() ), 'error' );
				update_option( 'aicw_gemini_api_key', '' );
				update_option( 'aicw_gemini_models', array() );
			} else {
				update_option( 'aicw_gemini_api_key', $gemini_api_key );
				update_option( 'aicw_gemini_models', $models );
			}
		}

		// Check if the ChatGPT API secret key is valid or not.
		if ( ! empty( $chatgpt_api_secret_key ) ) {
			// Create OpenAI service instance.
			$service = new \AIContentWriter\Services\OpenAI( $chatgpt_api_secret_key );

			// Call the service to get models.
			$models = $service->get_models();

			if ( is_wp_error( $models ) ) {
				ai_content_writer()->flash_notice( esc_html( 'OpenAI: ' . $models->get_error_message() ), 'error' );
				update_option( 'aicw_chatgpt_api_secret_key', '' );
				update_option( 'aicw_chatgpt_models', array() );
			} else {
				update_option( 'aicw_chatgpt_api_secret_key', $chatgpt_api_secret_key );
				update_option( 'aicw_chatgpt_models', $models );
			}
		}

		ai_content_writer()->flash_notice( esc_html__( 'API settings saved successfully.', 'ai-content-writer' ), 'success' );
		wp_safe_redirect( $referer );
		exit();
	}

	/**
	 * Add campaign.
	 *
	 * @since 1.0.0
	 * @return void
	 */
	public static function handle_add_campaign() {
		check_admin_referer( 'aicw_add_campaign' );
		$referer = wp_get_referer();

		if ( ! current_user_can( 'manage_options' ) ) {
			ai_content_writer()->flash_notice( esc_html__( 'You do not have permission to perform this action.', 'ai-content-writer' ), 'error' );
			wp_safe_redirect( $referer );
			exit();
		}

		$type     = isset( $_POST['campaign_type'] ) ? sanitize_text_field( wp_unslash( $_POST['campaign_type'] ) ) : 'articles';
		$title    = isset( $_POST['title'] ) ? sanitize_text_field( wp_unslash( $_POST['title'] ) ) : '';
		$keywords = isset( $_POST['keywords'] ) ? wp_kses_post( wp_unslash( $_POST['keywords'] ) ) : '';
		$status   = isset( $_POST['status'] ) ? sanitize_text_field( wp_unslash( $_POST['status'] ) ) : 'publish';
		$rss_feed = isset( $_POST['rss_feed_link'] ) ? sanitize_text_field( wp_unslash( $_POST['rss_feed_link'] ) ) : '';

		// Validate the input fields.
		if ( empty( $title ) ) {
			ai_content_writer()->flash_notice( esc_html__( 'Title is required. Please enter the campaign title.', 'ai-content-writer' ), 'error' );
			wp_safe_redirect( $referer );
			exit();
		}

		if ( empty( $type ) ) {
			ai_content_writer()->flash_notice( esc_html__( 'Campaign type is required. Please select the campaign type.', 'ai-content-writer' ), 'error' );
			wp_safe_redirect( $referer );
			exit();
		}

		if ( empty( $keywords ) && 'rss-feed' !== $type ) {
			ai_content_writer()->flash_notice( esc_html__( 'Keywords are required. Please enter the keywords.', 'ai-content-writer' ), 'error' );
			wp_safe_redirect( $referer );
			exit();
		}

		if ( 'rss-feed' === $type && empty( $rss_feed ) ) {
			ai_content_writer()->flash_notice( esc_html__( 'RSS feed link is required. Please enter the RSS feed link.', 'ai-content-writer' ), 'error' );
			wp_safe_redirect( $referer );
			exit();
		}

		// Create a new campaign.
		$campaign_id = wp_insert_post(
			array(
				'post_title'   => wp_strip_all_tags( $title ),
				'post_content' => wp_kses_post( $keywords ),
				'post_status'  => $status,
				'post_type'    => 'aicw_campaign',
			)
		);

		if ( is_wp_error( $campaign_id ) ) {
			ai_content_writer()->flash_notice( $campaign_id->get_error_message(), 'error' );
			wp_safe_redirect( $referer );
			exit();
		}

		// Update the campaign meta.
		$host                    = isset( $_POST['campaign_host'] ) ? sanitize_text_field( wp_unslash( $_POST['campaign_host'] ) ) : 'https://bing.com';
		$source                  = isset( $_POST['campaign_source'] ) ? sanitize_text_field( wp_unslash( $_POST['campaign_source'] ) ) : '';
		$block_keywords          = isset( $_POST['block_keywords'] ) ? sanitize_text_field( wp_unslash( $_POST['block_keywords'] ) ) : '';
		$search_replaces         = isset( $_POST['search_replaces'] ) ? map_deep( wp_unslash( $_POST['search_replaces'] ), 'sanitize_text_field' ) : array();
		$html_cleaners           = isset( $_POST['html_cleaners'] ) ? sanitize_text_field( wp_unslash( $_POST['html_cleaners'] ) ) : '';
		$insert_content_position = isset( $_POST['insert_content_position'] ) ? sanitize_text_field( wp_unslash( $_POST['insert_content_position'] ) ) : 'none';
		$insert_content          = isset( $_POST['insert_content'] ) ? wp_kses_post( wp_unslash( $_POST['insert_content'] ) ) : '';
		$target                  = isset( $_POST['target'] ) ? sanitize_text_field( wp_unslash( $_POST['target'] ) ) : '';
		$generate_thumb          = isset( $_POST['generate_thumbnail'] ) ? 'yes' : '';
		$post_type               = isset( $_POST['post_type'] ) ? sanitize_text_field( wp_unslash( $_POST['post_type'] ) ) : 'post';
		$completed_post_status   = isset( $_POST['completed_post_status'] ) ? sanitize_text_field( wp_unslash( $_POST['completed_post_status'] ) ) : 'publish';

		update_post_meta( $campaign_id, '_aicw_campaign_type', $type );
		update_post_meta( $campaign_id, '_aicw_campaign_host', $host );
		update_post_meta( $campaign_id, '_aicw_campaign_source', $source );
		update_post_meta( $campaign_id, '_aicw_rss_feed_link', $rss_feed );
		update_post_meta( $campaign_id, '_aicw_block_keywords', $block_keywords );
		update_post_meta( $campaign_id, '_aicw_search_replaces', $search_replaces );
		update_post_meta( $campaign_id, '_aicw_html_cleaners', $html_cleaners );
		update_post_meta( $campaign_id, '_aicw_insert_content_position', $insert_content_position );
		update_post_meta( $campaign_id, '_aicw_insert_content', $insert_content );
		update_post_meta( $campaign_id, '_aicw_campaign_target', $target );
		update_post_meta( $campaign_id, '_aicw_generate_thumbnail', $generate_thumb );
		update_post_meta( $campaign_id, '_aicw_post_type', $post_type );
		update_post_meta( $campaign_id, '_aicw_completed_post_status', $completed_post_status );

		ai_content_writer()->flash_notice( esc_html__( 'Campaign added successfully.', 'ai-content-writer' ), 'success' );

		// Remove 'add' query arg from the referer URL.
		$referer = remove_query_arg( 'add', $referer );
		// Redirect to the campaign edit page by adding the edit=campaign_id query arg.
		wp_safe_redirect( add_query_arg( 'edit', $campaign_id, $referer ) );
		exit();
	}

	/**
	 * Edit campaign.
	 *
	 * @since 1.0.0
	 * @return void
	 */
	public static function handle_edit_campaign() {
		check_admin_referer( 'aicw_edit_campaign' );
		$referer = wp_get_referer();

		if ( ! current_user_can( 'manage_options' ) ) {
			ai_content_writer()->flash_notice( esc_html__( 'You do not have permission to perform this action.', 'ai-content-writer' ), 'error' );
			wp_safe_redirect( $referer );
			exit();
		}

		$id       = isset( $_POST['id'] ) ? absint( wp_unslash( $_POST['id'] ) ) : 0;
		$type     = isset( $_POST['campaign_type'] ) ? sanitize_text_field( wp_unslash( $_POST['campaign_type'] ) ) : 'articles';
		$title    = isset( $_POST['title'] ) ? sanitize_text_field( wp_unslash( $_POST['title'] ) ) : '';
		$keywords = isset( $_POST['keywords'] ) ? wp_kses_post( wp_unslash( $_POST['keywords'] ) ) : '';
		$status   = isset( $_POST['status'] ) ? sanitize_text_field( wp_unslash( $_POST['status'] ) ) : 'publish';
		$rss_feed = isset( $_POST['rss_feed_link'] ) ? sanitize_text_field( wp_unslash( $_POST['rss_feed_link'] ) ) : '';

		// Validate the input fields.
		if ( empty( $id ) ) {
			ai_content_writer()->flash_notice( esc_html__( 'Invalid campaign. Please try again.', 'ai-content-writer' ), 'error' );
			wp_safe_redirect( $referer );
			exit();
		}

		if ( empty( $title ) ) {
			ai_content_writer()->flash_notice( esc_html__( 'Title is required. Please enter the campaign title.', 'ai-content-writer' ), 'error' );
			wp_safe_redirect( $referer );
			exit();
		}

		if ( empty( $type ) ) {
			ai_content_writer()->flash_notice( esc_html__( 'Campaign type is required. Please select the campaign type.', 'ai-content-writer' ), 'error' );
			wp_safe_redirect( $referer );
			exit();
		}

		if ( empty( $keywords ) && 'rss-feed' !== $type ) {
			ai_content_writer()->flash_notice( esc_html__( 'Keywords are required. Please enter the keywords.', 'ai-content-writer' ), 'error' );
			wp_safe_redirect( $referer );
			exit();
		}

		if ( 'rss-feed' === $type && empty( $rss_feed ) ) {
			ai_content_writer()->flash_notice( esc_html__( 'RSS feed link is required. Please enter the RSS feed link.', 'ai-content-writer' ), 'error' );
			wp_safe_redirect( $referer );
			exit();
		}

		// Update the campaign.
		$campaign_id = wp_update_post(
			array(
				'ID'           => $id,
				'post_title'   => wp_strip_all_tags( $title ),
				'post_content' => wp_kses_post( $keywords ),
				'post_status'  => $status,
			)
		);

		if ( is_wp_error( $campaign_id ) ) {
			ai_content_writer()->flash_notice( $campaign_id->get_error_message(), 'error' );
			wp_safe_redirect( $referer );
			exit();
		}

		// Update the campaign meta.
		$host                    = isset( $_POST['campaign_host'] ) ? sanitize_text_field( wp_unslash( $_POST['campaign_host'] ) ) : 'https://bing.com';
		$source                  = isset( $_POST['campaign_source'] ) ? sanitize_text_field( wp_unslash( $_POST['campaign_source'] ) ) : '';
		$block_keywords          = isset( $_POST['block_keywords'] ) ? sanitize_text_field( wp_unslash( $_POST['block_keywords'] ) ) : '';
		$search_replaces         = isset( $_POST['search_replaces'] ) ? map_deep( wp_unslash( $_POST['search_replaces'] ), 'sanitize_text_field' ) : array();
		$html_cleaners           = isset( $_POST['html_cleaners'] ) ? sanitize_text_field( wp_unslash( $_POST['html_cleaners'] ) ) : '';
		$insert_content_position = isset( $_POST['insert_content_position'] ) ? sanitize_text_field( wp_unslash( $_POST['insert_content_position'] ) ) : 'none';
		$insert_content          = isset( $_POST['insert_content'] ) ? wp_kses_post( wp_unslash( $_POST['insert_content'] ) ) : '';
		$target                  = isset( $_POST['target'] ) ? sanitize_text_field( wp_unslash( $_POST['target'] ) ) : '';
		$generate_thumb          = isset( $_POST['generate_thumbnail'] ) ? 'yes' : '';
		$post_type               = isset( $_POST['post_type'] ) ? sanitize_text_field( wp_unslash( $_POST['post_type'] ) ) : 'post';
		$completed_post_status   = isset( $_POST['completed_post_status'] ) ? sanitize_text_field( wp_unslash( $_POST['completed_post_status'] ) ) : 'publish';

		update_post_meta( $campaign_id, '_aicw_campaign_type', $type );
		update_post_meta( $campaign_id, '_aicw_campaign_host', $host );
		update_post_meta( $campaign_id, '_aicw_campaign_source', $source );
		update_post_meta( $campaign_id, '_aicw_rss_feed_link', $rss_feed );
		update_post_meta( $campaign_id, '_aicw_block_keywords', $block_keywords );
		update_post_meta( $campaign_id, '_aicw_search_replaces', $search_replaces );
		update_post_meta( $campaign_id, '_aicw_html_cleaners', $html_cleaners );
		update_post_meta( $campaign_id, '_aicw_insert_content_position', $insert_content_position );
		update_post_meta( $campaign_id, '_aicw_insert_content', $insert_content );
		update_post_meta( $campaign_id, '_aicw_campaign_target', $target );
		update_post_meta( $campaign_id, '_aicw_generate_thumbnail', $generate_thumb );
		update_post_meta( $campaign_id, '_aicw_post_type', $post_type );
		update_post_meta( $campaign_id, '_aicw_completed_post_status', $completed_post_status );

		ai_content_writer()->flash_notice( esc_html__( 'Campaign updated successfully.', 'ai-content-writer' ), 'success' );
		wp_safe_redirect( $referer );
		exit();
	}

	/**
	 * Generate content.
	 *
	 * @since 1.0.0
	 * @return void
	 */
	public static function handle_generate_content() {
		check_admin_referer( 'aicw_generate_content' );
		$referer = wp_get_referer();

		if ( ! current_user_can( 'manage_options' ) ) {
			ai_content_writer()->flash_notice( esc_html__( 'You do not have permission to perform this action.', 'ai-content-writer' ), 'error' );
			wp_safe_redirect( $referer );
			exit();
		}

		$prompt_content = isset( $_POST['prompt'] ) ? sanitize_textarea_field( wp_unslash( $_POST['prompt'] ) ) : '';
		$keywords       = isset( $_POST['keywords'] ) ? sanitize_text_field( wp_unslash( $_POST['keywords'] ) ) : '';
		$prompt_type    = isset( $_POST['prompt_type'] ) ? sanitize_text_field( wp_unslash( $_POST['prompt_type'] ) ) : 'Prompt';
		$language       = isset( $_POST['language'] ) ? sanitize_text_field( wp_unslash( $_POST['language'] ) ) : esc_html__( 'English', 'ai-content-writer' );
		$min_words      = isset( $_POST['min_words'] ) ? absint( wp_unslash( $_POST['min_words'] ) ) : '';
		$post_type      = isset( $_POST['post_type'] ) ? sanitize_text_field( wp_unslash( $_POST['post_type'] ) ) : '';
		$status         = isset( $_POST['status'] ) ? sanitize_text_field( wp_unslash( $_POST['status'] ) ) : 'draft';
		// For ChatGPT OpenAI API model.
		$system_tone = isset( $_POST['system_tone'] ) ? sanitize_textarea_field( wp_unslash( $_POST['system_tone'] ) ) : '';
		if ( empty( $system_tone ) ) {
			$system_tone = esc_html__( 'You are an expert SEO content writer. Generate factually accurate, engaging, and well-structured articles optimized for readability and search engines.', 'ai-content-writer' );
		}

		$max_tokens  = isset( $_POST['max_tokens'] ) ? absint( wp_unslash( $_POST['max_tokens'] ) ) : '';
		$temperature = isset( $_POST['temperature'] ) ? floatval( wp_unslash( $_POST['temperature'] ) ) : '';

		// Validate the input fields.
		if ( empty( $prompt_content ) ) {
			ai_content_writer()->flash_notice( esc_html__( 'Title is required. Please, start with "Write an article on..."', 'ai-content-writer' ), 'error' );
			wp_safe_redirect( $referer );
			exit();
		}

		if ( empty( $prompt_type ) ) {
			ai_content_writer()->flash_notice( esc_html__( 'Prompt type is required. Please, select the prompt type.', 'ai-content-writer' ), 'error' );
			wp_safe_redirect( $referer );
			exit();
		}

		if ( empty( $language ) ) {
			ai_content_writer()->flash_notice( esc_html__( 'Language is required. Please, select the language.', 'ai-content-writer' ), 'error' );
			wp_safe_redirect( $referer );
			exit();
		}

		if ( empty( $post_type ) ) {
			ai_content_writer()->flash_notice( esc_html__( 'Post type is required. Please, select the post type.', 'ai-content-writer' ), 'error' );
			wp_safe_redirect( $referer );
			exit();
		}

		// Check the API model.
		$title     = $prompt_content;
		$api_model = get_option( 'aicw_api_model' );
		if ( 'gemini' === $api_model ) {
			$api_key = get_option( 'aicw_gemini_api_key' );
			if ( empty( $api_key ) ) {
				ai_content_writer()->flash_notice( esc_html__( 'Please configure the API settings. A valid Gemini API key is required to generate the content.', 'ai-content-writer' ), 'error' );
				wp_safe_redirect( $referer );
				exit();
			}

			// Generating prompt for the Gemini API model.
			$prompt = $prompt_type . ': ' . $prompt_content . ' in ' . $language;
			if ( ! empty( $keywords ) ) {
				$prompt = $prompt . ' with keywords: ' . $keywords . ',';
			}

			if ( ! empty( $min_words ) ) {
				$prompt = $prompt . ' with minimum words: ' . $min_words;
			}

			// Generate content using the Google Gemini Open AI API.
			$prompt_data = array(
				'text' => $prompt,
			);

			$content = ai_content_writer()->generate_content( $prompt_data );

			if ( is_wp_error( $content ) ) {
				ai_content_writer()->flash_notice( $content->get_error_message(), 'error' );
				wp_safe_redirect( $referer );
				exit();
			}

			// Get all the matches from the generated content string starting form "**" and end with "**" as array.
			$pattern = '/\*\*(.*?)\*\*/';
			preg_match_all( $pattern, $content, $matches );

			// Get the title.
			$title = $matches[1][0];
			// Remove the title from the content.
			$content = str_replace( $matches[0][0], '', $content );

			if ( is_array( $matches[0] ) && is_array( $matches[1] ) ) {
				foreach ( $matches[0] as $key => $match ) {
					// replaces the strings.
					$content = str_replace( $match, '<h2>' . $matches[1][ $key ] . '</h2>', $content );
				}
			}

			// only matches exactly match string "<h2>1." and end with "</h2>".
			$pattern = '/<h2>1\.(.*?)<\/h2>/';
			preg_match_all( $pattern, $content, $matches_h2_1 );

			if ( is_array( $matches_h2_1[0] ) & is_array( $matches_h2_1[1] ) ) {
				foreach ( $matches_h2_1[0] as $key => $match ) {
					// replaces the strings.
					$content = str_replace( $match, '<h3>1.' . $matches_h2_1[1][ $key ] . '</h3>', $content );
				}
			}

			// only matches exactly match string "* <h2>" and end with "</h2>".
			$pattern = '/\* <h2>(.*?)<\/h2>/';
			preg_match_all( $pattern, $content, $matches_star_h2 );

			if ( is_array( $matches_star_h2[0] ) & is_array( $matches_star_h2[1] ) ) {
				foreach ( $matches_star_h2[0] as $key => $match ) {
					// replaces the strings.
					$content = str_replace( $match, '<h4>' . $matches_star_h2[1][ $key ] . '</h4>', $content );
				}
			}

			// only matches exactly match string "- <h2>" and end with "</h2>".
			$pattern = '/- <h2>(.*?)<\/h2>/';
			preg_match_all( $pattern, $content, $matches_dash_h2 );

			if ( is_array( $matches_dash_h2[0] ) & is_array( $matches_dash_h2[1] ) ) {
				foreach ( $matches_dash_h2[0] as $key => $match ) {
					// replaces the strings.
					$content = str_replace( $match, '<h5>' . $matches_dash_h2[1][ $key ] . '</h5>', $content );
				}
			}
		} elseif ( 'chatgpt' === $api_model ) {
			$api_secret_key = get_option( 'aicw_chatgpt_api_secret_key' );
			if ( empty( $api_secret_key ) ) {
				ai_content_writer()->flash_notice( esc_html__( 'Please configure the API settings. A valid ChatGPT API secret key is required to generate the content.', 'ai-content-writer' ), 'error' );
				wp_safe_redirect( $referer );
				exit();
			}

			// Generating prompt for ChatGPT OpenAI API model.
			$prompt = sprintf(
			/* translators: 1: Prompt Content, 2: System Tone, 3: Language, 4: Min Words */
				esc_html__(
					'%1$s with a professional tone. %2$s Ensure the content is engaging, easy to read, and formatted with proper headings (H2, H3), bullet points, and paragraphs.

Use %3$s as the language for this article. Keep the word count minimum of %4$s words for the best readability and SEO ranking.

The article should include:

- A catchy introduction that hooks the reader
- Informative body sections with subheadings
- A compelling conclusion with key takeaways

Avoid fluff, keep sentences concise, and ensure factual accuracy. Where applicable, use industry insights, statistics, and real-world examples. If necessary, cite reliable sources to back up claims. Ensure no AI or robotic tone—the content should feel human-written.',
					'ai-content-writer'
				),
				'"' . $prompt_content . '"',
				empty( $keywords ) ? esc_html__( 'The article should be optimized for SEO', 'ai-content-writer' ) : esc_html__( 'The article should be optimized for SEO, including relevant keywords: ', 'ai-content-writer' ) . '"' . $keywords . '".',
				$language,
				$min_words
			);

			// Generate content using the OpenAI ChatGPT API.
			$prompt_data = array(
				'secret_key'  => $api_secret_key,
				'prompt'      => $prompt,
				'system_tone' => $system_tone,
				'max_tokens'  => empty( $max_tokens ) ? 8000 : absint( $max_tokens ),
				'temperature' => empty( $temperature ) ? 0.7 : floatval( $temperature ),
			);

			$content = ai_content_writer()->generate_openai_content( $prompt_data );

			if ( is_wp_error( $content ) ) {
				ai_content_writer()->flash_notice( $content->get_error_message(), 'error' );
				wp_safe_redirect( $referer );
				exit();
			}

			// Convert OpenAI Markdown to HTML.
			$content = aicw_convert_openai_markdown_to_html( $content, $prompt_content );
			$content = isset( $content['content'] ) ? $content['content'] : '';
			$title   = isset( $content['title'] ) ? $content['title'] : $prompt_content;
		} else {
			ai_content_writer()->flash_notice( esc_html__( 'Invalid API model. Please configure the API settings.', 'ai-content-writer' ), 'error' );
			wp_safe_redirect( $referer );
			exit();
		}

		// Create a new post.
		$post_id = wp_insert_post(
			array(
				'post_title'   => wp_strip_all_tags( $title ),
				'post_content' => wp_kses_post( $content ),
				'post_status'  => $status,
				'post_type'    => $post_type,
			)
		);

		if ( is_wp_error( $post_id ) ) {
			ai_content_writer()->flash_notice( $post_id->get_error_message(), 'error' );
			wp_safe_redirect( $referer );
			exit();
		}

		// Add post meta for identification. _aicw_campaign_id is used to identify the campaign. But in this case, we are using the manual prompt to generate the content.
		update_post_meta( $post_id, '_aicw_campaign_id', 'manual' );

		if ( 'yes' === get_option( 'aicw_enable_img_generation', 'yes' ) ) {
			wp_safe_redirect(
				add_query_arg(
					array(
						'post_id' => $post_id,
					),
					admin_url( 'admin.php?page=aicw-generate-content&featured_image=1' )
				)
			);
			exit();
		}

		// Redirect to the post edit page.
		if ( 'yes' === get_option( 'aicw_enable_redirection', 'yes' ) ) {
			ai_content_writer()->flash_notice( esc_html__( 'Content generated successfully.', 'ai-content-writer' ), 'success' );
			wp_safe_redirect( admin_url( 'post.php?post=' . $post_id . '&action=edit' ) );
			exit();
		}

		ai_content_writer()->flash_notice( esc_html__( 'Content generated successfully.', 'ai-content-writer' ), 'success' );
		wp_safe_redirect( $referer );
		exit();
	}

	/**
	 * Set featured image.
	 *
	 * @since 1.0.0
	 * @return void
	 */
	public static function handle_set_featured_image() {
		check_admin_referer( 'aicw_set_featured_image' );
		$referer = wp_get_referer();

		if ( ! current_user_can( 'manage_options' ) ) {
			ai_content_writer()->flash_notice( esc_html__( 'You do not have permission to perform this action.', 'ai-content-writer' ), 'error' );
			wp_safe_redirect( $referer );
			exit();
		}

		$post_id  = isset( $_POST['post_id'] ) ? absint( wp_unslash( $_POST['post_id'] ) ) : 0;
		$media_id = isset( $_POST['featured_image'] ) ? absint( wp_unslash( $_POST['featured_image'] ) ) : 0;

		if ( empty( $post_id ) ) {
			ai_content_writer()->flash_notice( esc_html__( 'Invalid post. Please try again.', 'ai-content-writer' ), 'error' );
			wp_safe_redirect( $referer );
			exit();
		}

		if ( empty( $media_id ) ) {
			ai_content_writer()->flash_notice( esc_html__( 'Invalid image. Please select an image.', 'ai-content-writer' ), 'error' );
			wp_safe_redirect( $referer );
			exit();
		}

		// Get the dynamic hidden field value.
		$media_url = isset( $_POST[ $media_id ] ) ? sanitize_url( wp_unslash( $_POST[ $media_id ] ) ) : '';

		// Set the featured image.
		if ( empty( $media_url ) ) {
			ai_content_writer()->flash_notice( esc_html__( 'Invalid image URL. Please try again.', 'ai-content-writer' ), 'error' );
			wp_safe_redirect( $referer );
			exit();
		}

		$media_id = media_sideload_image( $media_url, $post_id, get_the_title( $post_id ), 'id' );
		set_post_thumbnail( $post_id, $media_id );

		// Redirect to the post edit page.
		if ( 'yes' === get_option( 'aicw_enable_redirection', 'yes' ) ) {
			wp_safe_redirect( admin_url( 'post.php?post=' . $post_id . '&action=edit' ) );
			exit();
		}

		ai_content_writer()->flash_notice( esc_html__( 'Content generated and featured image set successfully.', 'ai-content-writer' ), 'success' );
		// Remove featured_image & post_id from the referer URL.
		wp_safe_redirect( remove_query_arg( array( 'featured_image', 'post_id' ), $referer ) );
		exit();
	}

	/**
	 * Handle ajax request for deleting the campaigns temporarily post.
	 *
	 * @since 1.4.0
	 * @return void
	 */
	public static function handle_delete_temp_post() {
		check_ajax_referer( 'aicw_nonce', 'nonce' );

		if ( ! current_user_can( 'manage_options' ) ) {
			wp_send_json_error(
				array(
					'message' => esc_html__( 'You do not have permission to perform this action.', 'ai-content-writer' ),
				)
			);
		}

		$post_id = isset( $_POST['post_id'] ) ? absint( wp_unslash( $_POST['post_id'] ) ) : 0;

		if ( empty( $post_id ) ) {
			wp_send_json_error(
				array(
					'message' => esc_html__( 'Invalid post. Please try again.', 'ai-content-writer' ),
				)
			);
		}

		// Delete the post. This will permanently delete the post.
		if ( wp_delete_post( $post_id, true ) ) {
			wp_send_json_success(
				array(
					'message' => esc_html__( 'Post deleted successfully.', 'ai-content-writer' ),
				)
			);
		}

		wp_send_json_error(
			array(
				'message' => esc_html__( 'Failed to delete the post. Please try again.', 'ai-content-writer' ),
			)
		);
	}

	/**
	 * Handle ajax request for running the campaign instantly.
	 *
	 * @since 1.4.0
	 * @return void
	 */
	public static function handle_run_campaign() {
		check_ajax_referer( 'aicw_nonce', 'nonce' );

		if ( ! current_user_can( 'manage_options' ) ) {
			wp_send_json_error(
				array(
					'message' => esc_html__( 'You do not have permission to perform this action.', 'ai-content-writer' ),
				)
			);
		}

		$campaign_id = isset( $_POST['campaign_id'] ) ? absint( wp_unslash( $_POST['campaign_id'] ) ) : 0;
		if ( empty( $campaign_id ) ) {
			wp_send_json_error(
				array(
					'message' => esc_html__( 'Invalid campaign. Please try again.', 'ai-content-writer' ),
				)
			);
		}

		$campaign = get_post( $campaign_id );
		if ( ! $campaign || 'aicw_campaign' !== $campaign->post_type ) {
			wp_send_json_error(
				array(
					'message' => esc_html__( 'Campaign not found. Please try again.', 'ai-content-writer' ),
				)
			);
		}

		// Run the campaign instantly.
		Cron::generate_titles(
			array(
				'p'              => $campaign_id,
				'posts_per_page' => 1,
			)
		);

		Cron::generate_content(
			array(
				'meta_query' => array( // phpcs:ignore WordPress.DB.SlowDBQuery.slow_db_query_meta_query
					array(
						'key'   => '_aicw_campaign_id',
						'value' => $campaign_id,
					),
				),
			)
		);

		Cron::generate_thumbnails(
			array(
				'meta_query' => array( // phpcs:ignore WordPress.DB.SlowDBQuery.slow_db_query_meta_query
					array(
						'key'   => '_aicw_campaign_id',
						'value' => $campaign_id,
					),
				),
			)
		);

		Cron::publish_posts(
			array(
				'meta_query' => array( // phpcs:ignore WordPress.DB.SlowDBQuery.slow_db_query_meta_query
					array(
						'key'   => '_aicw_campaign_id',
						'value' => $campaign_id,
					),
				),
			)
		);

		wp_send_json_success(
			array(
				'message' => esc_html__( 'Campaign run successfully.', 'ai-content-writer' ),
			)
		);
	}
}
