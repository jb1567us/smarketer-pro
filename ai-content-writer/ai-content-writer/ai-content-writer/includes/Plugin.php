<?php

namespace AIContentWriter;

defined( 'ABSPATH' ) || exit; // Exit if accessed directly.

/**
 * The main plugin class.
 *
 * @since 1.0.0
 * @package AI Content Writer
 */
class Plugin {

	/**
	 * Plugin file path.
	 *
	 * @var string
	 */
	protected $file;

	/**
	 * Plugin version.
	 *
	 * @var string
	 */
	protected $version = '1.0.0';

	/**
	 * The single instance of the class.
	 *
	 * @since 1.0.0
	 * @var self
	 */
	public static $instance;

	/**
	 * Gets the single instance of the class.
	 * This method is used to create a new instance of the class.
	 *
	 * @param string $file The plugin file path.
	 * @param string $version The plugin version.
	 *
	 * @since 1.0.0
	 * @return static
	 */
	final public static function create( $file, $version = '1.0.0' ) {
		if ( null === self::$instance ) {
			self::$instance = new static( $file, $version );
		}

		return self::$instance;
	}

	/**
	 * Constructor.
	 *
	 * @param string $file The plugin file path.
	 * @param string $version The plugin version.
	 *
	 * @since 1.0.0
	 */
	public function __construct( $file, $version ) {
		$this->file    = $file;
		$this->version = $version;
		$this->define_constants();
		$this->includes();
		$this->init_hooks();
	}

	/**
	 * Define the plugin constants.
	 *
	 * @since 1.0.0
	 * @return void
	 */
	private function define_constants() {
		define( 'AICW_VERSION', $this->version );
		define( 'AICW_FILE', $this->file );
		define( 'AICW_PATH', plugin_dir_path( $this->file ) );
		define( 'AICW_URL', plugin_dir_url( $this->file ) );
		define( 'AICW_ASSETS_URL', AICW_URL . 'assets/' );
	}

	/**
	 * Include the required files.
	 *
	 * @since 1.0.0
	 * @return void
	 */
	private function includes() {
		require_once __DIR__ . '/functions.php';
		// Require the deprecated functions file.
		require_once __DIR__ . '/deprecated.php';
	}

	/**
	 * Initialize the plugin hooks.
	 *
	 * @since 1.0.0
	 * @return void
	 */
	private function init_hooks() {
		register_activation_hook( AICW_FILE, array( $this, 'activate' ) );
		add_filter( 'plugin_action_links_' . plugin_basename( AICW_FILE ), array( $this, 'action_links' ) );
		add_action( 'admin_notices', array( $this, 'display_flash_notices' ), 12 );
		add_action( 'init', array( $this, 'init' ), 0 );
	}

	/**
	 * Add action links to the plugin.
	 *
	 * @param array $links The plugin action links.
	 *
	 * @since 1.0.0
	 * @return array The modified plugin action links.
	 */
	public function action_links( $links ) {
		$action_links = array(
			'settings' => sprintf(
				/* translators: %1$s: Settings URL, %2$s: Settings text */
				'<a href="%1$s">%2$s</a>',
				esc_url( admin_url( 'admin.php?page=aicw-settings' ) ),
				esc_html__( 'Settings', 'ai-content-writer' )
			),
		);

		$action_links = array_merge( $action_links, $links );

		if ( ! defined( 'AICW_PRO_VERSION' ) ) {
			$action_links['go_pro'] = '<a href="https://beautifulplugins.com/plugins/ai-content-writer-pro/?utm_source=plugin&utm_medium=pro-badge&utm_campaign=plugin-action" target="_blank" style="color: #39b54a; font-weight: bold;">' . esc_html__( 'Go Pro', 'ai-content-writer' ) . '</a>';
		}

		return $action_links;
	}

	/**
	 * Activate the plugin.
	 *
	 * @since 1.0.0
	 * @return void
	 */
	public function activate() {
		update_option( 'aicw_version', AICW_VERSION );

		// Check if the deprecated option exists then delete it.
		if ( get_option( 'aicw_is_enabled' ) ) {
			delete_option( 'aicw_is_enabled' );
		}
	}

	/**
	 * Add a flash notice.
	 *
	 * @param string  $notice Notice message.
	 * @param string  $type This can be "info", "warning", "error" or "success", "success" as default.
	 * @param boolean $dismissible Whether the notice is-dismissible or not.
	 *
	 * @since 1.0.0
	 * @return void
	 */
	public function flash_notice( $notice = '', $type = 'success', $dismissible = true ) {
		$notices          = get_option( 'aicw_flash_notices', array() );
		$dismissible_text = ( $dismissible ) ? 'is-dismissible' : '';

		// Add new notice.
		array_push(
			$notices,
			array(
				'notice'      => $notice,
				'type'        => $type,
				'dismissible' => $dismissible_text,
			)
		);

		// Update the notices array.
		update_option( 'aicw_flash_notices', $notices );
	}

	/**
	 * Display flash notices after that, remove the option to prevent notices being displayed forever.
	 *
	 * @since 1.0.0
	 * @return void
	 */
	public function display_flash_notices() {
		$notices = get_option( 'aicw_flash_notices', array() );

		foreach ( $notices as $notice ) {
			printf(
				'<div class="notice notice-%1$s %2$s"><p>%3$s</p></div>',
				esc_attr( $notice['type'] ),
				esc_attr( $notice['dismissible'] ),
				esc_html( $notice['notice'] ),
			);
		}

		// Reset options to prevent notices being displayed forever.
		if ( ! empty( $notices ) ) {
			delete_option( 'aicw_flash_notices', array() );
		}
	}

	/**
	 * Initialize the plugin.
	 *
	 * @since 1.0.0
	 * @return void
	 */
	public function init() {
		// Load common classes.
		new PostTypes();
		new Cron();

		// Load admin classes.
		if ( is_admin() ) {
			new Admin\Admin();
			new Admin\Dashboard();
			new Admin\Actions();
			new Admin\Settings();
			new Admin\Notices();
		}
	}

	/**
	 * Generate content with the help of Open AI API.
	 * This method is used to generate content based on the user input configurations and settings.
	 *
	 * @param array $prompt_data The prompt data to generate content.
	 *
	 * @since 1.0.0
	 * @return string|\WP_Error The generated content.
	 */
	public function generate_content( $prompt_data ) {
		// Retrieve API key from settings.
		$api_key = get_option( 'aicw_gemini_api_key' );
		if ( empty( $api_key ) ) {
			return new \WP_Error( 'aicw_api_key_not_set', esc_html__( 'Please configure the API settings. A valid Gemini API key is required to generate the content.', 'ai-content-writer' ) );
		}

		// Define the API URL.
		// phpcs:disable
		// https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent.
		// https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateContent
		// phpcs:enable

		$model_name = get_option( 'aicw_gemini_ai_model', 'models/gemini-2.5-flash' );
		$url        = 'https://generativelanguage.googleapis.com/v1/' . $model_name . ':generateContent';

		// The data payload to send to the Gemini API.
		$data = array(
			'contents' => array(
				array(
					'role'  => 'user',
					'parts' => array(
						$prompt_data,
					),
				),
			),
		);

		// Set up the arguments for the request.
		$args = array(
			'body'        => wp_json_encode( $data ),
			'headers'     => array(
				'Content-Type'   => 'application/json',
				'x-goog-api-key' => $api_key,
			),
			'method'      => 'POST',
			'data_format' => 'body',
			'timeout'     => 300,
		);

		// Make the request.
		$response = wp_remote_post( $url, $args );

		// Check if the request returned an error.
		if ( is_wp_error( $response ) ) {
			// Handle the error appropriately.
			$error_msg = $response->get_error_message();
			return new \WP_Error( 'api_error', $error_msg );
		}

		// Get the response body.
		$body = wp_remote_retrieve_body( $response );

		// Decode the JSON response.
		$result = json_decode( $body, true );

		// Handle the response data.
		if ( isset( $result['candidates'][0]['content']['parts'][0]['text'] ) ) {
			$generated_text = $result['candidates'][0]['content']['parts'][0]['text'];
			return $generated_text;
		} else {
			$error_msg = isset( $result['error']['message'] ) ? $result['error']['message'] : esc_html__( 'An unexpected error occurred while generating the content.', 'ai-content-writer' );
			// Handle the case where the response does not contain the expected data.
			return new \WP_Error( 'unexpected_api_response', $error_msg );
		}
	}

	/**
	 * Generate content with the help of ChatGPT Open AI API.
	 * This method is used to generate content based on the user input configurations and settings.
	 *
	 * @param array $prompt_data The prompt data to generate openAI content.
	 *
	 * @since 1.0.0
	 * @return string|\WP_Error The generated content.
	 */
	public function generate_openai_content( $prompt_data ) {
		$api_secret_key = isset( $prompt_data['secret_key'] ) ? $prompt_data['secret_key'] : '';

		// Bail if the API Secret key is not set.
		if ( empty( $api_secret_key ) ) {
			return new \WP_Error( 'aicw_api_secret_key_not_set', esc_html__( 'Please configure the API settings. A valid ChatGPT OpenAI API key is required to generate the content.', 'ai-content-writer' ) );
		}

		$prompt = isset( $prompt_data['prompt'] ) ? $prompt_data['prompt'] : '';

		if ( empty( $prompt ) ) {
			return new \WP_Error( 'aicw_prompt_not_set', esc_html__( 'Please provide a prompt to generate the content.', 'ai-content-writer' ) );
		}

		$system_tone      = isset( $prompt_data['system_tone'] ) ? $prompt_data['system_tone'] : esc_html__( 'You are an expert SEO content writer. Generate factually accurate, engaging, and well-structured articles optimized for readability and search engines.', 'ai-content-writer' );
		$max_tokens       = isset( $prompt_data['max_tokens'] ) ? $prompt_data['max_tokens'] : 8000;
		$temperature      = isset( $prompt_data['temperature'] ) ? $prompt_data['temperature'] : 0.7;
		$chatgpt_ai_model = get_option( 'aicw_chatgpt_ai_model', 'gpt-5' );

		// Allow long-running requests (e.g., GPT-5 article generation).
		if ( function_exists( 'set_time_limit' ) ) {
			set_time_limit( 300 ); // phpcs:ignore Squiz.PHP.DiscouragedFunctions.Discouraged --Allowing long-running requests. It's necessary for generating long content. And safe to use here because this is called in background during cron job or AJAX request.

			// phpcs:disable
			// TODO: Need to handle potential error logs when using set_time_limit in PHP 8+.
			// try {
			// set_time_limit( 300 ); // 5 minutes
			// } catch ( \Throwable $e ) {
			// error_log( 'Failed to set execution time: ' . $e->getMessage() );
			// }
			// phpcs:enable
		}

		// Define the API URL.
		$api_url = 'https://api.openai.com/v1/chat/completions';

		// The data payload to send to the OpenAI API.
		$data = array(
			'model'             => $chatgpt_ai_model,
			'messages'          => array(
				array(
					'role'    => 'system',
					'content' => $system_tone,
				),
				array(
					'role'    => 'user',
					'content' => $prompt,
				),
			),
			'max_tokens'        => $max_tokens,
			'temperature'       => $temperature,
			'top_p'             => 1,
			'frequency_penalty' => 0,
			'presence_penalty'  => 0,
		);

		// Adjust parameter for specific OpenAI models like GPT-5 series.
		if ( in_array( $chatgpt_ai_model, array( 'gpt-5', 'gpt-5-mini', 'gpt-5-nano' ), true ) ) {
			unset( $data['max_tokens'], $data['temperature'], $data['top_p'], $data['frequency_penalty'], $data['presence_penalty'] );

			// Add correct token limit for GPT-5.
			$data['max_completion_tokens'] = $max_tokens;
		}

		// Set up the arguments for the request.
		$args = array(
			'headers' => array(
				'Content-Type'  => 'application/json',
				'Authorization' => 'Bearer ' . $api_secret_key,
			),
			'body'    => wp_json_encode( $data ),
			'timeout' => 300,
		);

		// Make the request.
		$response = wp_remote_post( $api_url, $args );

		// Check if the request returned an error.
		if ( is_wp_error( $response ) ) {
			$error_msg = $response->get_error_message();
			return new \WP_Error( 'api_error', $error_msg );
		}

		// Get the response body.
		$body = wp_remote_retrieve_body( $response );

		// Decode the JSON response.
		$result = json_decode( $body, true );

		// Check if the response contains the expected data.
		if ( ! isset( $result['choices'][0]['message']['content'] ) ) {
			return new \WP_Error( 'unexpected_api_response', esc_html__( 'An unexpected error occurred while generating the content.', 'ai-content-writer' ) );
		}

		// Return the generated content.
		return $result['choices'][0]['message']['content'];
	}

	/**
	 * Generate image with the help of Pexels API.
	 *
	 * @param string $query The query to search images.
	 * @param int    $per_page The number of images to fetch.
	 *
	 * @since 1.0.0
	 * @return array|\WP_Error The images array.
	 */
	public function generate_images( $query, $per_page = 20 ) {
		// Retrieve the Pexels API key.
		$api_key = get_option( 'aicw_pexels_api_key' );

		if ( empty( $api_key ) ) {
			return new \WP_Error( 'aicw_api_key_not_set', esc_html__( 'Please configure the API settings. A valid Pexels API key is required to generate the images.', 'ai-content-writer' ) );
		}

		// Define the API URL.
		$url = 'https://api.pexels.com/v1/search?query=' . rawurlencode( $query ) . '&per_page=' . absint( $per_page );

		// Set up the arguments for the request.
		$args = array(
			'headers' => array(
				'Authorization' => $api_key,
			),
		);

		// Make the request.
		$response = wp_remote_get( $url, $args );

		// Check if the request returned an error.
		if ( is_wp_error( $response ) ) {
			// Handle the error appropriately.
			return new \WP_Error( 'api_error', $response->get_error_message() );
		}

		// Get the response body.
		$body = wp_remote_retrieve_body( $response );

		// Decode the JSON response.
		$data = json_decode( $body, true );

		// Handle the response data.
		if ( isset( $data['photos'] ) && ! empty( $data['photos'] ) ) {
			return $data['photos'];
		} else {
			// Handle the case where the response does not contain the expected data.
			return new \WP_Error( 'unexpected_api_response', esc_html__( 'An unexpected error occurred while generating the images.', 'ai-content-writer' ) );
		}
	}

	/**
	 * Create a log entry
	 *
	 * @param string $message The log message.
	 * @param string $type    The log type (e.g., 'success', 'info', 'error', 'warning').
	 * @param int    $campaign_id Optional. The campaign ID associated with the log. Default is empty.
	 *
	 * @since 2.0.6
	 * @return int|\WP_Error The ID of the created log post or WP_Error on failure.
	 */
	public function create_log( $message, $type = 'info', $campaign_id = '' ) {
		if ( empty( $message ) ) {
			return new \WP_Error( 'aicw_log_message_empty', esc_html__( 'Log message cannot be empty.', 'ai-content-writer' ) );
		}

		$log_data = array(
			'post_title'   => sanitize_title( $type ),
			'post_content' => wp_kses_post( $message ),
			'post_status'  => 'publish',
			'post_type'    => 'aicw_log',
		);

		// If campaign ID is provided, add it as post meta.
		if ( ! empty( $campaign_id ) ) {
			$log_data['meta_input']['_aicw_related_campaign'] = absint( $campaign_id );
		}

		return wp_insert_post( $log_data );
	}
}
