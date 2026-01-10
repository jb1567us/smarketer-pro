<?php

namespace AIContentWriter\Services;

defined( 'ABSPATH' ) || exit; // Exit if accessed directly.

/**
 * Gemini Service Class.
 *
 * Handles requests to the Google Gemini API.
 *
 * @since 1.0.0
 * @package AIContentWriter\Services
 */
class Gemini {

	/**
	 * Gemini Base API Endpoint.
	 *
	 * @var string
	 */
	private string $api_url = 'https://generativelanguage.googleapis.com/v1beta/';

	/**
	 * API Key.
	 *
	 * @var string
	 */
	private string $api_key;

	/**
	 * Constructor.
	 *
	 * @param string $api_key Gemini API key.
	 */
	public function __construct( string $api_key ) {
		$this->api_key = $api_key;
	}

	/**
	 * Send a GET request to the Gemini API.
	 *
	 * @param string $endpoint The endpoint path (no leading slash).
	 *
	 * @since  1.0.0
	 * @return array Response array or WP_Error structured array.
	 */
	private function get_request( string $endpoint ): array {
		$url = esc_url_raw(
			$this->api_url . $endpoint . '?key=' . $this->api_key
		);

		$response = wp_remote_get(
			$url,
			array(
				'timeout' => 30,
				'headers' => array(
					'Content-Type' => 'application/json',
				),
			)
		);

		if ( is_wp_error( $response ) ) {
			return array( 'error' => $response->get_error_message() );
		}

		$body = json_decode( wp_remote_retrieve_body( $response ), true );

		if ( json_last_error() !== JSON_ERROR_NONE ) {
			return array( 'error' => 'Invalid JSON response from Gemini API.' );
		}

		return $body;
	}

	/**
	 * Send a POST request to the Gemini API.
	 *
	 * @param string $endpoint API endpoint.
	 * @param array  $data     Request body.
	 *
	 * @since  1.0.0
	 * @return array Response array or WP_Error structured array.
	 */
	private function post_request( string $endpoint, array $data ): array {
		$url = esc_url_raw(
			$this->api_url . $endpoint . '?key=' . $this->api_key
		);

		$response = wp_remote_post(
			$url,
			array(
				'timeout' => 30,
				'headers' => array(
					'Content-Type'   => 'application/json',
					'x-goog-api-key' => $this->api_key,
				),
				'body'    => wp_json_encode( $data ),
			)
		);

		if ( is_wp_error( $response ) ) {
			return array( 'error' => $response->get_error_message() );
		}

		$body = json_decode( wp_remote_retrieve_body( $response ), true );

		if ( json_last_error() !== JSON_ERROR_NONE ) {
			return array( 'error' => 'Invalid JSON response from Gemini API.' );
		}

		return $body;
	}

	/**
	 * Fetch available Gemini models dynamically.
	 *
	 * @since 1.0.0
	 * @return array|\WP_Error List of models.
	 */
	public function get_models() {
		$cache_key = 'aicw_gemini_models_' . md5( $this->api_key );
		$cached    = get_transient( $cache_key );

		if ( false !== $cached ) {
			return $cached;
		}

		$response = $this->get_request( 'models' );

		if ( isset( $response['error'] ) ) {
			return new \WP_Error(
				'aicw_gemini_api_error',
				$response['error']['message'] ?? esc_html__( 'API key not valid. Please pass a valid API key.', 'ai-content-writer' )
			);
		}

		if ( empty( $response['models'] ) ) {
			return new \WP_Error(
				'aicw_gemini_no_models',
				esc_html__( 'No models found or API key not valid. Please pass a valid API key.', 'ai-content-writer' )
			);
		}

		$models         = array();
		$allowed_models = array(
			'models/gemini-2.5-flash',
			'models/gemini-2.5-pro',
			'models/gemini-2.5-flash-lite',
			'models/gemini-2.0-flash',
			'models/gemini-2.0-flash-lite',
			'models/gemini-flash-latest',
			'models/gemini-flash-lite-latest',
			'models/gemini-pro-latest',
			'models/gemini-1.5-flash',
			'models/gemini-1.5-pro',
		);

		foreach ( $response['models'] as $model ) {
			if ( ! isset( $model['name'] ) ) {
				continue;
			}

			if ( ! in_array( $model['name'], $allowed_models, true ) ) {
				continue;
			}

			$model_id     = sanitize_text_field( $model['name'] );
			$display_name = $model['displayName'] ?? $model_id;

			$models[ $model_id ] = esc_html( $display_name );
		}

		// Cache for 24 hours.
		set_transient( $cache_key, $models, DAY_IN_SECONDS );

		return $models;
	}

	/**
	 * Generate text using a Gemini model.
	 *
	 * @since 1.0.0
	 *
	 * @param string $model  The model ID (e.g., models/gemini-2.5-flash).
	 * @param string $prompt The user prompt.
	 *
	 * @since  1.0.0
	 * @return array|\WP_Error Response or WP_Error.
	 */
	public function generate_text( string $model, string $prompt ) {
		if ( empty( $model ) ) {
			return new \WP_Error( 'aicw_gemini_invalid_model', 'Model ID is required.' );
		}

		$data = array(
			'contents' => array(
				array(
					'parts' => array(
						array( 'text' => $prompt ),
					),
				),
			),
		);

		$response = $this->post_request( $model . ':generateContent', $data );

		if ( isset( $response['error'] ) ) {
			return new \WP_Error( 'aicw_gemini_generate_error', $response['error'] );
		}

		return $response;
	}
}
