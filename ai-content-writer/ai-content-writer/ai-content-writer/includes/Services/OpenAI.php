<?php

namespace AIContentWriter\Services;

defined( 'ABSPATH' ) || exit;

/**
 * OpenAI Service Class.
 *
 * Handles requests to the OpenAI API.
 *
 * @since 1.0.0
 * @package AIContentWriter\Services
 */
class OpenAI {

	/**
	 * OpenAI Base URL.
	 *
	 * @var string
	 */
	private string $api_url = 'https://api.openai.com/v1/';

	/**
	 * API Key.
	 *
	 * @var string
	 */
	private string $api_key;

	/**
	 * Constructor.
	 *
	 * @param string $api_key OpenAI API key.
	 */
	public function __construct( string $api_key ) {
		$this->api_key = $api_key;
	}

	/**
	 * Send a GET request to the OpenAI API.
	 *
	 * @param string $endpoint API endpoint.
	 * @return array Response array or error array.
	 */
	private function get_request( string $endpoint ): array {
		$url = esc_url_raw( $this->api_url . $endpoint );

		$response = wp_remote_get(
			$url,
			array(
				'timeout' => 30,
				'headers' => array(
					'Authorization' => 'Bearer ' . $this->api_key,
					'Content-Type'  => 'application/json',
				),
			)
		);

		if ( is_wp_error( $response ) ) {
			return array( 'error' => $response->get_error_message() );
		}

		$body = json_decode( wp_remote_retrieve_body( $response ), true );

		if ( json_last_error() !== JSON_ERROR_NONE ) {
			return array( 'error' => 'Invalid JSON response from OpenAI API.' );
		}

		return $body;
	}

	/**
	 * Send a POST request to OpenAI API.
	 *
	 * @param string $endpoint API endpoint.
	 * @param array  $data     Request payload.
	 * @return array Response array or error array.
	 */
	private function post_request( string $endpoint, array $data ): array {
		$url = esc_url_raw( $this->api_url . $endpoint );

		$response = wp_remote_post(
			$url,
			array(
				'timeout' => 30,
				'headers' => array(
					'Authorization' => 'Bearer ' . $this->api_key,
					'Content-Type'  => 'application/json',
				),
				'body'    => wp_json_encode( $data ),
			)
		);

		if ( is_wp_error( $response ) ) {
			return array( 'error' => $response->get_error_message() );
		}

		$body = json_decode( wp_remote_retrieve_body( $response ), true );

		if ( json_last_error() !== JSON_ERROR_NONE ) {
			return array( 'error' => 'Invalid JSON response from OpenAI API.' );
		}

		return $body;
	}

	/**
	 * Fetch available OpenAI models dynamically.
	 *
	 * @since 1.0.0
	 *
	 * @return array|\WP_Error List of models.
	 */
	public function get_models() {
		$cache_key = 'aicw_openai_models_' . md5( $this->api_key );
		$cached    = get_transient( $cache_key );

		if ( false !== $cached ) {
			return $cached;
		}

		$response = $this->get_request( 'models' );

		if ( isset( $response['error'] ) ) {
			return new \WP_Error(
				'aicw_openai_api_error',
				$response['error']['message'] ?? esc_html__( 'API key not valid. Please pass a valid API key.', 'ai-content-writer' )
			);
		}

		if ( empty( $response['data'] ) ) {
			return new \WP_Error(
				'aicw_openai_no_models',
				esc_html__( 'No models found or API key not valid. Please pass a valid API key.', 'ai-content-writer' )
			);
		}

		$models         = array();
		$allowed_models = array(
			'gpt-5.1',
			'gpt-5',
			'gpt-5-pro',
			'gpt-5-mini',
			'gpt-5-nano',
			'gpt-4.1',
			'gpt-4.1-mini',
			'gpt-4.1-nano',
			'gpt-4',
			'gpt-4o',
			'gpt-4-turbo',
			'gpt-3.5-turbo',
		);

		foreach ( $response['data'] as $model ) {
			if ( ! isset( $model['id'] ) ) {
				continue;
			}

			if ( ! in_array( $model['id'], $allowed_models, true ) ) {
				continue;
			}

			$model_id = sanitize_text_field( $model['id'] );

			// Display name is the same as ID unless you want formatting.
			$models[ $model_id ] = esc_html( $model_id );
		}

		// Cache for 24 hours.
		set_transient( $cache_key, $models, DAY_IN_SECONDS );

		return $models;
	}

	/**
	 * Generate text using OpenAI Chat Completion API.
	 *
	 * @since 1.0.0
	 *
	 * @param string $model  OpenAI model ID (e.g., gpt-4.1, gpt-5).
	 * @param string $prompt The user prompt.
	 * @return array|\WP_Error Response data.
	 */
	public function generate_text( string $model, string $prompt ) {
		if ( empty( $model ) ) {
			return new \WP_Error( 'aicw_openai_invalid_model', 'Model ID is required.' );
		}

		$data = array(
			'model'    => $model,
			'messages' => array(
				array(
					'role'    => 'user',
					'content' => $prompt,
				),
			),
		);

		$response = $this->post_request( 'chat/completions', $data );

		if ( isset( $response['error'] ) ) {
			return new \WP_Error( 'aicw_openai_generate_error', $response['error'] );
		}

		return $response;
	}
}
