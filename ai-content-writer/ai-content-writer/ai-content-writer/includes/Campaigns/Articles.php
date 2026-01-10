<?php

namespace AIContentWriter\Campaigns;

use simplehtmldom\HtmlWeb;

defined( 'ABSPATH' ) || exit; // Exit if accessed directly.

/**
 * Class Articles
 *
 * @since 1.7.0
 * @package AIContentWriter/Campaigns
 */
class Articles {

	/**
	 * Generate titles.
	 * This function is responsible for generating titles based on the provided keywords.
	 *
	 * @param int    $campaign_id The ID of the campaign for which titles are being generated.
	 * @param string $keywords An array of keywords that will be used to generate the titles and source links.
	 * @param int    $posts_needed The number of posts needed.
	 *
	 * @since 1.7.0
	 * @return bool Whether the titles and source links were generated successfully or not.
	 */
	public static function generate_titles( $campaign_id, $keywords, $posts_needed ) {
		if ( empty( $campaign_id ) || empty( $keywords ) || empty( $posts_needed ) ) {
			return false;
		}

		$host = get_post_meta( $campaign_id, '_aicw_campaign_host', true );
		if ( empty( $host ) ) {
			$host = get_option( 'aicw_default_host' );
		}

		// Check if the host is allowed Otherwise return false.
		$allowed_hosts = get_option( 'aicw_allowed_hosts' );

		// Take the only domain from the host.
		$host_domain = wp_parse_url( $host, PHP_URL_HOST );
		// Remove www. from the host domain.
		$host_domain = str_replace( 'www.', '', $host_domain );

		// Check if the host is allowed Otherwise return false.
		if ( ! empty( $allowed_hosts ) && str_contains( $allowed_hosts, $host_domain ) === false ) {
			return false;
		}

		// Explode keywords by comma.
		$keywords = explode( ',', $keywords );

		// Take a random keyword from the array.
		if ( is_array( $keywords ) ) {
			$keyword = $keywords[ array_rand( $keywords ) ];
		} else {
			$keyword = $keywords;
		}

		if ( empty( $keyword ) ) {
			return false;
		}

		// Check if keyword is a string and trim it.
		if ( is_string( $keyword ) ) {
			$keyword = trim( $keyword );
		}

		// Generate host URL for Bing search with keywords.
		$keyword = rawurlencode( $keyword );
		$url     = trailingslashit( $host ) . "search?q=$keyword&count=20&setlang=en&first=10";

		// Initialize HTML dom.
		$dom = new HtmlWeb();
		// Load the HTML from the URL.
		$html = $dom->load( $url );

		if ( ! $html ) {
			return false;
		}

		// Check if the $host contain 'bing.com/news' then use the news card selector.
		if ( str_contains( $host, 'bing.com/news' ) ) {
			$results = $html->find( 'div[class="news-card newsitem cardcommon"] a.title' );
		} else {
			$results = $html->find( 'li.b_algo h2 a' );
		}

		// Check if the results are empty then return false.
		if ( empty( (array) $results ) ) {
			return false;
		}

		$count = 0;
		foreach ( $results as $a ) {
			$title = wp_strip_all_tags( $a->plaintext );
			$link  = $a->href;

			// Decode the Bing URL if it contains 'bing.com/ck/'.
			if ( str_contains( $link, 'bing.com/ck/' ) ) {
				$link = aicw_decode_bing_url( $link );
			} else {
				$link = esc_url( $link );
			}

			if ( empty( $title ) || empty( $link ) ) {
				continue;
			}

			// Check if the title already exists.
			$post_exists = aicw_get_post_by_title( $title );
			if ( $post_exists && ( get_post_meta( $post_exists, '_aicw_content_source_link', true ) === $link ) ) {
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
			update_post_meta( $post_id, '_aicw_content_source_link', $link );

			// Update the counter.
			++$count;

			// If the counter is greater than or equal to the target then break the loop.
			if ( $count >= $posts_needed ) {
				ai_content_writer()->create_log( sprintf( /* translators: 1: Number of posts generated. */ __( '%d posts titles and source links generated successfully.', 'ai-content-writer' ), $count ), 'success', $campaign_id );
				break;
			}
		}

		// If the loop executed successfully, return true.
		return $count > 0;
	}

	/**
	 * Generate content.
	 * This function is responsible for generating content based on the source link.
	 *
	 * @param int    $post_id The ID of the post for which content is being generated.
	 * @param string $title The title of the post.
	 * @param string $keyword The keyword that will be used to generate the content.
	 *
	 * @since 1.7.0
	 * @return bool Whether the content was generated successfully or not.
	 */
	public static function generate_content( $post_id, $title = '', $keyword = '' ) {
		if ( empty( $post_id ) ) {
			return false;
		}

		// Get the source link from the post meta.
		$source_link = get_post_meta( $post_id, '_aicw_content_source_link', true );

		if ( empty( $source_link ) ) {
			return false;
		}

		// Get the content from the source link.
		$dom  = new HtmlWeb();
		$html = $dom->load( trailingslashit( $source_link ) );

		if ( ! $html ) {
			return false;
		}

		// SEO Metadata schema.
		$seo_data = array(
			'description' => '',
			'keywords'    => $keyword,
		);

		$meta_desc = $html->find( 'meta[name=description]', 0 );
		if ( ! empty( $meta_desc ) ) {
			$seo_data['description'] = trim( $meta_desc->content );
		}

		$meta_keywords = $html->find( 'meta[name=keywords]', 0 );
		if ( ! empty( $meta_keywords ) ) {
			$seo_data['keywords'] = trim( $meta_keywords->content );
		}

		// Get the post title, content and error.
		$result = array(
			'title'   => '',
			'content' => '',
		);

		// Extract title - try different common title selectors.
		$possible_title_selectors = array(
			'h1.entry-title',
			'h1.post-title',
			'h1.article-title',
			'article h1',
			'.article-header h1',
			'.post-header h1',
			'header h1',
			'h1',
			'.headline',
			'.title',
			'#title',
		);

		// Try to find the title using the possible selectors.
		foreach ( $possible_title_selectors as $selector ) {
			$title_element = $html->find( $selector, 0 );
			if ( $title_element ) {
				$result['title'] = trim( $title_element->plaintext );
				break;
			}
		}

		// If title still not found, use the page title.
		if ( empty( $result['title'] ) ) {
			$title_element = $html->find( 'title', 0 );
			if ( $title_element ) {
				$result['title'] = trim( $title_element->plaintext );
			}
		}

		// Extract content - try different common content containers.
		$content_elements           = null;
		$possible_content_selectors = array(
			'article',
			'.post-content',
			'.entry-content',
			'.article-content',
			'.content',
			'#content',
			'.post-body',
			'.article-body',
			'.story-content',
			'.main-content',
			'main',
			'.post',
			'#main-content',
			'.story',
			'.entry',
			'.blog-post',
			'.post-entry',
		);

		// Try to identify the main content container.
		foreach ( $possible_content_selectors as $selector ) {
			$element = $html->find( $selector, 0 );
			if ( $element ) {
				$content_elements = $element;
				break;
			}
		}

		// If no content found with selector approach, use paragraph fallback.
		if ( empty( (array) $content_elements ) ) {
			// Find all paragraphs and analyze which ones likely belong to the main content.
			$all_paragraphs = $html->find( 'p' );

			// Filter out small paragraphs that likely aren't article content and paragraphs in common non-content areas like headers, footers, sidebars.
			$content_paragraphs = array();
			foreach ( $all_paragraphs as $p ) {
				$text   = trim( $p->plaintext );
				$length = strlen( $text );

				// Skip empty paragraphs.
				if ( $length < 10 ) { continue;
				}

				// Skip paragraphs in common non-content areas.
				$parent       = $p->parent();
				$parent_tag   = $parent ? strtolower( $parent->tag ) : '';
				$parent_class = $parent ? strtolower( $parent->class ) : '';
				$parent_id    = $parent ? strtolower( $parent->id ) : '';

				$skip_keywords = array( 'footer', 'header', 'sidebar', 'comment', 'menu', 'nav', 'widget' );
				$should_skip   = false;
				foreach ( $skip_keywords as $skip_keyword ) {
					if ( strpos( $parent_class, $skip_keyword ) !== false || strpos( $parent_id, $skip_keyword ) !== false || strpos( $parent_tag, $skip_keyword ) !== false ) {
						$should_skip = true;
						break;
					}
				}

				if ( ! $should_skip ) {
					$content_paragraphs[] = $text;
				}
			}

			// Join all valid paragraphs.
			$result['content'] = implode( "\n\n", $content_paragraphs );
		} else {
			// Clean up the content - Remove common non-content elements.
			foreach ( $content_elements->find( 'aside, .sidebar, .widget, nav, .navigation, .menu, .comment, .comments, .post-meta, .related-posts, .social-share, .share-buttons, .sharing, .author-bio, script, style, iframe, form, .advertisement, .ads, .ad-container' ) as $remove ) {
				$remove->outertext = '';
				$remove->clear();
			}

			/**
			 * Allow cleanup HTML elements from the content.
			 * This will allow users to clean up specific elements using HTML tags, classes, or IDs.
			 *
			 * @param object $content_elements The content elements.
			 * @param int    $post_id The post ID.
			 *
			 * @since 2.0.2
			 * @return object The modified content elements.
			 */
			$content_elements = apply_filters( 'aicw_cleanup_content_elements', $content_elements, $post_id );

			// Define allowed HTML tags.
			$allowed_html = array( 'p', 'h2', 'h3', 'h4', 'h5', 'h6', 'ol', 'ul', 'blockquote' );

			// Extract content with HTML structure preserved.
			$paragraphs = array();
			foreach ( $content_elements->find( 'p, h2, h3, h4, h5, h6, ol, ul, blockquote' ) as $node ) {
				// Get the tag name.
				$tag_name = strtolower( $node->tag );

				// Check if this tag is in our allowed tags list.
				if ( in_array( $tag_name, $allowed_html, true ) ) {
					// For list elements, need to preserve structure.
					if ( 'ol' === $tag_name || 'ul' === $tag_name ) {
						$list_items = array();
						foreach ( $node->find( 'li' ) as $li ) {
							$li_text = trim( $li->plaintext );
							if ( ! empty( $li_text ) ) {
								$list_items[] = "<li>{$li_text}</li>";
							}
						}
						if ( ! empty( $list_items ) ) {
							$list_html    = "<{$tag_name}>" . implode( '', $list_items ) . "</{$tag_name}>";
							$paragraphs[] = $list_html;
						}
					} else {
						// For other tags like p, h2, etc., just get inner text.
						$text = trim( $node->plaintext );
						if ( ! empty( $text ) ) {
							$paragraphs[] = "<{$tag_name}>{$text}</{$tag_name}>";
						}
					}
				}
			}

			// Join all elements with proper spacing.
			$result['content'] = implode( "\n", $paragraphs );

			// If no paragraphs found, use the plain text of the content element.
			if ( empty( $result['content'] ) ) {
				$result['content'] = trim( $content_elements->plaintext );
			}
		}

		// Clean the content.
		$result['content'] = preg_replace( '/\s+/', ' ', $result['content'] ); // Normalize whitespace.
		$result['content'] = preg_replace( '/\n\s*\n/', "\n\n", $result['content'] ); // Remove extra line breaks.
		$result['content'] = trim( $result['content'] );

		// Clean the title.
		$result['title'] = preg_replace( '/\s+/', ' ', $result['title'] ); // Normalize whitespace.
		$result['title'] = trim( $result['title'] );

		// Release memory.
		$html->clear();
		unset( $html );

		// Check if the content is empty.
		if ( isset( $result['content'] ) && empty( $result['content'] ) ) {
			return false;
		}

		// Update the post content.
		$updated = wp_update_post(
			array(
				'ID'           => $post_id,
				'post_title'   => wp_strip_all_tags( isset( $result['title'] ) ? $result['title'] : $title ),
				'post_content' => wp_kses_post( $result['content'] ),
			)
		);

		if ( is_wp_error( $updated ) ) {
			return false;
		}

		return true;
	}
}
