<?php

defined( 'ABSPATH' ) || exit; // Exit if accessed directly.

/**
 * Render an external image.
 *
 * @param string $image_url The image URL.
 * @param string $alt The alt text.
 * @param string $class_name The class name.
 *
 * @since 1.0.0
 * @package AIContentWriter
 * @return string The image HTML.
 */
function aicw_render_external_image( $image_url, $alt = '', $class_name = '' ) {
	if ( empty( $image_url ) ) {
		return ''; // Return early if no image URL.
	}

	// Sanitize the URL, alt text, and class.
	$image_url  = esc_url( $image_url );
	$alt        = esc_attr( $alt );
	$class_name = esc_attr( $class_name );

	// Prepare the attributes.
	$attributes = sprintf(
		'src="%s" alt="%s" class="%s"',
		$image_url,
		$alt,
		$class_name
	);

	if ( empty( $attributes ) ) {
		return ''; // Return early if no attributes.
	}

	// Allow only the <img> tag with specific attributes.
	$allowed_html = array(
		'img' => array(
			'src'   => array(),
			'alt'   => array(),
			'class' => array(),
		),
	);

	// Construct the <img> tag.
	$img_tag = '<img ' . $attributes . '>';

	// Return sanitized HTML.
	return wp_kses( $img_tag, $allowed_html );
}

/**
 * Convert OpenAI Markdown to HTML.
 *
 * @param string $content The OpenAI Markdown content.
 * @param string $title The title of the content.
 *
 * @since 1.0.0
 * @package AIContentWriter
 * @return array The HTML content and title.
 */
function aicw_convert_openai_markdown_to_html( $content, $title = '' ) {
	// Replace headers.
	$content = preg_replace( '/###### (.+)/', '<h6>$1</h6>', $content );
	$content = preg_replace( '/##### (.+)/', '<h5>$1</h5>', $content );
	$content = preg_replace( '/#### (.+)/', '<h4>$1</h4>', $content );
	$content = preg_replace( '/### (.+)/', '<h3>$1</h3>', $content );
	$content = preg_replace( '/## (.+)/', '<h2>$1</h2>', $content );

	// Replace bold text.
	$content = preg_replace( '/\*\*(.+?)\*\*/', '<strong>$1</strong>', $content );

	// Extract title if present.
	preg_match( '/^# (.+)/m', $content, $matches );
	$title = $matches[1] ?? $title;
	// Remove title from content.
	$content = preg_replace( '/^# .+\n*/', '', $content );

	return array(
		'title'   => $title,
		'content' => $content,
	);
}

/**
 * Get campaign.
 *
 * @param mixed $data The data.
 *
 * @since 1.4.0
 * @return WP_Post|false The campaign object, or false if not found.
 */
function aicw_get_campaign( $data ) {

	if ( is_numeric( $data ) ) {
		$data = get_post( $data );
	}

	if ( $data instanceof WP_Post && 'aicw_campaign' === $data->post_type ) {
		return $data;
	}

	return false;
}

/**
 * Get campaigns.
 *
 * @param array $args The args.
 * @param bool  $count Whether to return a count.
 *
 * @since 1.4.0
 * @return array|int The campaigns.
 */
function aicw_get_campaigns( $args = array(), $count = false ) {
	$defaults = array(
		'post_type'      => 'aicw_campaign',
		'posts_per_page' => - 1,
		'orderby'        => 'date',
		'order'          => 'ASC',
	);

	$args  = wp_parse_args( $args, $defaults );
	$query = new WP_Query( $args );

	if ( $count ) {
		return $query->found_posts;
	}

	return array_map( 'aicw_get_campaign', $query->posts );
}

/**
 * Get campaign titles.
 * This will generate the titles for the campaign using OpenAI or any other AI service.
 *
 * @param string $type The type of the campaign.
 * @param string $keywords The campaign keywords.
 * @param int    $needed_count The number of titles to generate.
 *
 * @since 1.4.0
 * @return array The generated titles.
 */
function aicw_generate_titles( $type, $keywords, $needed_count = 20 ) {
	if ( empty( $type ) || empty( $keywords ) ) {
		return array();
	}

	// Initialize titles needed count.
	$needed_count = empty( $needed_count ) ? 20 : ( absint( $needed_count ) + 20 );

	if ( 'gemini' === $type ) {
		$api_key = get_option( 'aicw_gemini_api_key' );
		if ( empty( $api_key ) ) {
			return array();
		}

		// Define the API URL.
		$model_name = 'gemini-1.5-pro';
		$url        = 'https://generativelanguage.googleapis.com/v1/models/' . $model_name . ':generateContent';

		// The data payload to send to the Gemini API.
		$data = array(
			'contents' => array(
				array(
					'role'  => 'user',
					'parts' => array(
						array(
							'text' => 'You are experienced in writing about ' . $keywords . '. Please generate ' . $needed_count . ' SEO friendly titles for these keywords.',
						),
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
			return array();
		}

		// Get the response body.
		$body = wp_remote_retrieve_body( $response );

		// Decode the JSON response.
		$result = json_decode( $body, true );

		// Handle the response data.
		if ( ! isset( $result['candidates'][0]['content']['parts'][0]['text'] ) ) {
			return array();
		}

		$titles = explode( "\n", trim( $result['candidates'][0]['content']['parts'][0]['text'] ) );
	} elseif ( 'chatgpt' === $type ) {
		$api_key = get_option( 'aicw_chatgpt_api_secret_key' );
		if ( empty( $api_key ) ) {
			return array();
		}

		// Call OpenAI API to generate titles.
		$chatgpt_ai_model = get_option( 'aicw_chatgpt_ai_model', 'gpt-5' );
		$api_url          = 'https://api.openai.com/v1/chat/completions';

		// The data payload to send to the OpenAI API.
		$data = array(
			'model'             => $chatgpt_ai_model,
			'messages'          => array(
				array(
					'role'    => 'system',
					'content' => 'You are experienced in writing about ' . $keywords . '. Please generate some titles for these keywords.',
				),
				array(
					'role'    => 'user',
					'content' => 'Generate ' . $needed_count . ' titles for these keywords: ' . $keywords,
				),
			),
			'max_tokens'        => 1000,
			'temperature'       => 0.7,
			'top_p'             => 1,
			'frequency_penalty' => 0,
			'presence_penalty'  => 0,
		);

		// Adjust parameter for specific OpenAI models like GPT-5 series.
		if ( in_array( $chatgpt_ai_model, array( 'gpt-5', 'gpt-5-mini', 'gpt-5-nano' ), true ) ) {
			unset( $data['max_tokens'], $data['temperature'], $data['top_p'], $data['frequency_penalty'], $data['presence_penalty'] );
		}

		// Set up the arguments for the request.
		$args = array(
			'headers' => array(
				'Content-Type'  => 'application/json',
				'Authorization' => 'Bearer ' . $api_key,
			),
			'body'    => wp_json_encode( $data ),
			'timeout' => 300,
		);

		// Make the request.
		$response = wp_remote_post( $api_url, $args );

		// Check if the request returned an error.
		if ( is_wp_error( $response ) ) {
			// Handle the error appropriately.
			return array();
		}

		// Get the response body.
		$body = wp_remote_retrieve_body( $response );

		// Decode the JSON response.
		$result = json_decode( $body, true );

		// Check if the response contains the expected data.
		if ( ! isset( $result['choices'][0]['message']['content'] ) ) {
			return array();
		}

		$titles = explode( "\n", trim( $result['choices'][0]['message']['content'] ) );
	}

	return $titles;
}

/**
 * Generate content for the campaign.
 * This will generate the content for the campaign using OpenAI or any other AI service.
 *
 * @param int    $post_id The ID of the post for which content is being generated.
 * @param string $title The title of the content.
 * @param string $keywords The campaign keywords.
 *
 * @since 1.4.0
 * @return string|mixed The generated content or null.
 */
function aicw_generate_content( $post_id, $title, $keywords = '' ) {
	if ( empty( $post_id ) || empty( $title ) ) {
		return '';
	}

	// Get the associated campaign ID.
	$campaign_id   = get_post_meta( $post_id, '_aicw_campaign_id', true );
	$campaign_type = get_post_meta( $campaign_id, '_aicw_campaign_type', true );
	$api_model     = empty( $campaign_type ) ? get_option( 'aicw_api_model' ) : $campaign_type; // TODO: We will remove this option in the future. It's already remove from the settings page.

	if ( empty( $api_model ) ) {
		return null;
	}

	if ( 'gemini' === $api_model ) {
		$language = 'English'; // TODO: Add language support.

		$api_key = get_option( 'aicw_gemini_api_key' );
		if ( empty( $api_key ) ) {
			return null;
		}

		// Generating prompt for the Gemini API model.
		$prompt = 'Write a well-structured article on the title: ' . $title . ', in ' . $language . ',';
		if ( ! empty( $keywords ) ) {
			$prompt = $prompt . ' with keywords: ' . $keywords . ',';
		}

		// Generate content using the Google Gemini Open AI API.
		$prompt_data = array(
			'text' => $prompt,
		);

		$content = ai_content_writer()->generate_content( $prompt_data );

		if ( is_wp_error( $content ) ) {
			return null;
		}

		// Get all the matches from the generated content string starting form "**" and end with "**" as array.
		$pattern = '/\*\*(.*?)\*\*/';
		preg_match_all( $pattern, $content, $matches );

		// Get the title.
		// $title = $matches[1][0];
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
				$content = str_replace( $match, '<h5>' . $matches_dash_h2[1][ $key ] . '</h5>', $content );
			}
		}

		return $content;
	} elseif ( 'chatgpt' === $api_model ) {
		$language       = 'English'; // TODO: Add language support.
		$api_secret_key = get_option( 'aicw_chatgpt_api_secret_key' );
		if ( empty( $api_secret_key ) ) {
			return null;
		}

		// For ChatGPT OpenAI API model.
		$system_tone = '';
		if ( empty( $system_tone ) ) {
			$system_tone = esc_html__( 'You are an expert SEO content writer. Generate factually accurate, engaging, and well-structured articles optimized for readability and search engines.', 'ai-content-writer' );
		}

		$max_tokens  = 5000;
		$temperature = 0.7;

		// Generating prompt for ChatGPT OpenAI API model.
		$prompt = sprintf(
		/* translators: 1: Prompt Content, 2: System Tone, 3: Language */
			esc_html__(
				'Write a well-structured article on %1$s with a professional tone. %2$s Ensure the content is engaging, easy to read, and formatted with proper headings (H2, H3), bullet points, and paragraphs.

Use %3$s as the language for this article.

The article should include:

- A catchy introduction that hooks the reader
- Informative body sections with subheadings
- A compelling conclusion with key takeaways

Avoid fluff, keep sentences concise, and ensure factual accuracy. Where applicable, use industry insights, statistics, and real-world examples. If necessary, cite reliable sources to back up claims. Ensure no AI or robotic tone—the content should feel human-written.',
				'ai-content-writer'
			),
			'"' . $title . '"',
			empty( $keywords ) ? esc_html__( 'The article should be optimized for SEO', 'ai-content-writer' ) : esc_html__( 'The article should be optimized for SEO, including relevant keywords: ', 'ai-content-writer' ) . '"' . $keywords . '".',
			$language
		);

		// Generate content using the OpenAI ChatGPT API.
		$prompt_data = array(
			'secret_key'  => $api_secret_key,
			'prompt'      => $prompt,
			'system_tone' => $system_tone,
			'max_tokens'  => empty( $max_tokens ) ? 5000 : absint( $max_tokens ),
			'temperature' => empty( $temperature ) ? 0.7 : floatval( $temperature ),
		);

		$content = ai_content_writer()->generate_openai_content( $prompt_data );

		if ( is_wp_error( $content ) ) {
			return null;
		}

		// Convert OpenAI Markdown to HTML.
		$content = aicw_convert_openai_markdown_to_html( $content, $title );

		return isset( $content['content'] ) ? $content['content'] : null;
	}

	return null;
}

/**
 * Get the post ID by exact title using direct $wpdb query.
 *
 * @param string $post_title The post title.
 *
 * @since 1.4.0
 * @return int|null The post ID if found, otherwise null.
 */
function aicw_get_post_by_title( $post_title ) {
	global $wpdb;

	$post_title = wp_unslash( $post_title ); // Just in case, unescape slashes.

	// phpcs:ignore WordPress.DB.DirectDatabaseQuery.DirectQuery, WordPress.DB.DirectDatabaseQuery.NoCaching
	$query = $wpdb->get_var(
		$wpdb->prepare(
			"SELECT ID FROM {$wpdb->posts}
		 WHERE post_title = %s
		 AND post_type != 'revision'
		 AND post_status IN ('publish', 'pending', 'draft', 'future', 'private')
		 LIMIT 1",
			$post_title
		)
	);

	return $query ? (int) $query : null;
}

/**
 * Get all post IDs by exact title using direct $wpdb query.
 *
 * @param string $post_title The post title.
 *
 * @since 1.4.0
 * @return int[] Array of post IDs if found, otherwise an empty array.
 */
function aicw_get_posts_by_title( $post_title ) {
	global $wpdb;

	$post_title = wp_unslash( $post_title ); // Ensure slashes are removed.

	// phpcs:ignore WordPress.DB.DirectDatabaseQuery.DirectQuery, WordPress.DB.DirectDatabaseQuery.NoCaching
	$query = $wpdb->get_col(
		$wpdb->prepare(
			"SELECT ID FROM {$wpdb->posts}
			WHERE post_title = %s
			AND post_type != 'revision'
			AND post_status IN ('publish', 'pending', 'draft', 'future', 'private')",
			$post_title
		)
	);

	return array_map( 'intval', $query );
}



/**
 * Campaign needs to update.
 * This function checks if the campaign needs to be updated.
 *
 * @param int $campaign_id The campaign ID.
 *
 * @since 1.4.0
 * @return array The array of needed elements.
 */
function aicw_campaign_needs_update( $campaign_id ) {
	// Check if the campaign is not found.
	if ( empty( $campaign_id ) ) {
		return array(
			'needs_update' => false,
			'error'        => __( 'The campaign is not found.', 'ai-content-writer' ),
		);
	}

	// Check is the campaign target is reached.
	$target = absint( get_post_meta( $campaign_id, '_aicw_campaign_target', true ) );

	// Get total found posts for this campaign.
	$total_posts = aicw_get_campaigns(
		array(
			'post_type'      => 'aicw_post',
			'posts_per_page' => -1,
			'meta_query'     => array( // phpcs:ignore WordPress.DB.SlowDBQuery.slow_db_query_meta_query
				array(
					'key'   => '_aicw_campaign_id',
					'value' => $campaign_id,
				),
			),
			'post_status'    => 'any',
		),
		true
	);

	// Get total found posts for this campaign that already published.
	$total_posts_published = aicw_get_campaigns(
		array(
			'post_type'      => get_post_meta( $campaign_id, '_aicw_post_type', true ) ?? 'post',
			'posts_per_page' => -1,
			'meta_query'     => array( // phpcs:ignore WordPress.DB.SlowDBQuery.slow_db_query_meta_query
				array(
					'key'   => '_aicw_campaign_id',
					'value' => $campaign_id,
				),
			),
			'post_status'    => 'any',
		),
		true
	);

	// Merge the total posts and total published posts.
	if ( $total_posts_published > 0 ) {
		$total_posts = $total_posts + $total_posts_published;
	}

	// Check if the target is reached.
	if ( $total_posts >= $target ) {
		return array(
			'needs_update' => false,
			'error'        => __( 'The campaign target is reached.', 'ai-content-writer' ),
		);
	}

	// Check how many posts are needed to reach the target.
	$posts_needed = absint( $target - $total_posts );

	return array(
		'needs_update' => true,
		'posts_needed' => $posts_needed,
		'error'        => '',
	);
}

/**
 * Campaigns temporary post needs update.
 * This function checks if the campaign temporary post needs to be updated.
 *
 * @param \WP_Post $post The temporary post.
 * @param int      $campaign_id The campaign ID.
 *
 * @since 1.4.0
 * @return array The array of needed elements.
 */
function aicw_temp_post_needs_update( $post, $campaign_id ) {
	// Check if the temporary post and campaign are empty or not found.
	if ( empty( $post ) || empty( $campaign_id ) ) {
		return array();
	}

	$needs_update = array();

	// Check if the temporary post title is empty or not found.
	if ( empty( $post->post_title ) ) {
		$needs_update['title'] = true;
	}

	// Check if the temporary post content is empty or not found.
	if ( empty( $post->post_content ) ) {
		$needs_update['content'] = true;
	}

	// Check if the campaign needs to generate a thumbnail.
	$generate_thumb = get_post_meta( $campaign_id, '_aicw_generate_thumbnail', true );

	// Check if the temporary post thumbnail is empty or not found.
	if ( empty( get_post_thumbnail_id( $post->ID ) ) && $generate_thumb ) {
		$needs_update['thumbnail'] = true;
	}

	return $needs_update;
}

/**
 * Update last run time.
 * This function updates the last run time for the campaigns or temporary posts.
 *
 * @param int $post_id The post ID.
 *
 * @since 1.4.0
 * @return void
 */
function aicw_update_last_run_time( $post_id ) {
	// Update the post and indicate that the post has been updated.
	wp_update_post(
		array(
			'ID'                => $post_id,
			'post_modified'     => current_time( 'mysql' ),
			'post_modified_gmt' => current_time( 'mysql', 1 ),
		)
	);
}

/**
 * Get the camping target max limit.
 * This function gets the campaign target maximum limit.
 *
 * @since 1.4.0
 * @return int The campaign target limit.
 */
function aicw_get_campaign_target_max_limit() {
	$target_limit = apply_filters( 'aicw_campaign_target_max_limit', 20 );

	return absint( $target_limit );
}

/**
 * Get user agents.
 * This function gets the user agents for the campaigns.
 *
 * @since 1.7.0
 * @return array The user agents.
 */
function aicw_user_agents(): array {
	return array(
		'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
		'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
		'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
		'Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1',
		'Mozilla/5.0 (iPad; CPU OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1',
	);
}

/**
 * Render search and replace fields.
 *
 * @param array $field Field arguments.
 *
 * @since 2.0.2
 */
function aicw_search_replace_fields( $field ) {
	$key = wp_rand( 1, 100000 );
	?>
	<tr>
		<td class="search">
			<input type="text" name="search_replaces[<?php echo esc_attr( $key ); ?>][search]" value="<?php echo esc_attr( $field['search'] ); ?>" placeholder="<?php esc_attr_e( 'Keyword', 'ai-content-writer' ); ?>">
		</td>
		<td class="replace">
			<input type="text" name="search_replaces[<?php echo esc_attr( $key ); ?>][replace]" value="<?php echo esc_attr( $field['replace'] ); ?>" placeholder="<?php esc_attr_e( 'Keyword 2', 'ai-content-writer' ); ?>">
		</td>
		<td class="actions" width="1%">
			<a href="#" class="delete"><?php esc_html_e( 'Delete', 'ai-content-writer' ); ?></a>
		</td>
	</tr>
	<?php
}

/**
 * Decode Bing URL.
 * This function decodes a Bing URL to extract the original URL.
 *
 * @param string $href The Bing URL.
 *
 * @since 2.0.5
 * @return string|false The decoded URL or false if not found or invalid.
 */
function aicw_decode_bing_url( $href ) {
	$query = wp_parse_url( $href, PHP_URL_QUERY );
	if ( empty( $query ) ) {
		return false;
	}

	parse_str( $query, $params );

	if ( ! empty( $params['u'] ) ) {
		$u = rawurldecode( $params['u'] );

		// Find position of "aHR0" (start of actual Base64 for https).
		$pos = strpos( $u, 'aHR0' );
		if ( false !== $pos ) {
			$u = substr( $u, $pos );
		}

		// Convert URL-safe Base64 to standard Base64.
		$u = strtr( $u, '-_', '+/' );

		// Add padding.
		$padding = strlen( $u ) % 4;
		if ( $padding > 0 ) { $u .= str_repeat( '=', 4 - $padding );
		}

		// Decode the Base64 string. The base64_decode function is safe here as we are validating the input.
		$decoded_url = base64_decode( $u, true ); // phpcs:ignore WordPress.PHP.DiscouragedPHPFunctions.obfuscation_base64_decode
		if ( false !== $decoded_url ) {
			return esc_url_raw( $decoded_url );
		}
	}

	return false;
}
