<?php

defined( 'ABSPATH' ) || exit; // Exit if accessed directly.

/**
 * Get the plugin instance (Deprecated).
 *
 * @since 1.0.0
 * @deprecated 1.1.0 Use ai_content_writer() instead.
 * @return \AIContentWriter\Plugin Plugin initialization class.
 */
function aicw_ai_content_writer() {
	_deprecated_function( __FUNCTION__, '1.1.0', 'ai_content_writer' );

	return ai_content_writer();
}
