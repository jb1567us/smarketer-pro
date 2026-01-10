<?php
/**
 * Plugin Name:       AI Content Writer
 * Plugin URI:        https://beautifulplugins.com/ai-content-writer/
 * Description:       AI Content Writer helps you automatically generate high-quality, SEO-optimized content for your blog or website in minutes using advanced AI technologies like ChatGPT, OpenAI, Google Gemini, and more.
 * Version:           2.1.0
 * Requires at least: 5.0
 * Requires PHP:      7.4
 * Author:            BeautifulPlugins
 * Author URI:        https://beautifulplugins.com/
 * License:           GPLv2 or later
 * License URI:       https://www.gnu.org/licenses/gpl-2.0.html
 * Text Domain:       ai-content-writer
 * Domain Path:       /languages
 * Tested up to:      6.8
 *
 * @package AIContentWriter
 *
 * AI Content Writer is a plugin that helps you generate content for your website using the power of AI.
 *
 * AI Content Writer is a free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 2 of the License, or
 * any later version.
 *
 * AI Content Writer is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with AI Content Writer. If not, see https://www.gnu.org/licenses/gpl-2.0.html
 */

use AIContentWriter\Plugin;

defined( 'ABSPATH' ) || exit; // Exit if accessed directly.

// Include the optimized autoloader.
require_once __DIR__ . '/vendor/autoload.php';

/**
 * Get the plugin instance.
 *
 * @since 1.0.0
 * @return Plugin plugin initialize class.
 */
function ai_content_writer() {
	return Plugin::create( __FILE__, '2.1.0' );
}

// Initialize the plugin.
ai_content_writer();
