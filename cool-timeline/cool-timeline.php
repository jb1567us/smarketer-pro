<?php
/*
  Plugin Name: Cool Timeline Lite
  Plugin URI: https://cooltimeline.com
  Description: Lightweight timeline plugin with media support - optimized for performance.
  Version: 3.1.1
  Author: Cool Plugins
  Author URI: https://coolplugins.net
  License: GPLv2 or later
  License URI: https://www.gnu.org/licenses/gpl-2.0.html
  Domain Path: /languages
  Text Domain: cool-timeline
*/

// Exit if accessed directly.
if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

// Configuration
if ( ! defined( 'CTL_V' ) ) {
	define( 'CTL_V', '3.1.1' );
}

define( 'CTL_PLUGIN_URL', plugin_dir_url( __FILE__ ) );
define( 'CTL_PLUGIN_DIR', plugin_dir_path( __FILE__ ) );

if ( ! class_exists( 'CoolTimelineLite' ) ) {
	final class CoolTimelineLite {

		private static $instance;
		private $cache_group = 'cool_timeline';
		private $cache_time = 3600; // 1 hour cache

		public static function get_instance() {
			if ( null === self::$instance ) {
				self::$instance = new self();
			}
			return self::$instance;
		}

		public static function registers() {
			$thisIns = self::$instance;
			
			register_activation_hook( __FILE__, array( $thisIns, 'ctl_activate' ) );
			register_deactivation_hook( __FILE__, array( $thisIns, 'ctl_deactivate' ) );

			add_action( 'plugins_loaded', array( $thisIns, 'ctl_include_files' ) );
			add_action( 'init', array( $thisIns, 'ctl_flush_rules' ) );
			add_action( 'init', array( $thisIns, 'ctl_load_plugin_textdomain' ) );
			
			if ( is_admin() ) {
				$pluginpath = plugin_basename( __FILE__ );
				add_filter( "plugin_action_links_$pluginpath", array( $thisIns, 'ctl_settings_link' ) );
				add_action( 'save_post', array( $thisIns, 'ctl_save_story_meta' ), 10, 3 );
			}

			// Optimized: Load assets only when needed
			add_action( 'wp_enqueue_scripts', array( $thisIns, 'ctl_conditional_assets' ) );
			
			// Gutenberg block
			if ( function_exists( 'register_block_type' ) ) {
				add_action( 'init', array( $thisIns, 'ctl_register_blocks' ) );
			}
		}

		public function __construct() {
			// Minimal constructor
		}

		public function ctl_include_files() {
			// Load only essential files
			require_once CTL_PLUGIN_DIR . 'admin/class.cool-timeline-posttype.php';
			require_once CTL_PLUGIN_DIR . 'includes/shortcodes/class-ctl-helpers.php';
			require_once CTL_PLUGIN_DIR . 'includes/shortcodes/class-ctl-shortcode.php';
			
			if ( is_admin() ) {
				require_once CTL_PLUGIN_DIR . 'admin/ctl-admin-settings.php';
				require_once CTL_PLUGIN_DIR . 'admin/ctl-meta-fields.php';
			}
		}

		// Optimized asset loading
		public function ctl_conditional_assets() {
			global $post;
			
			// Only load if timeline shortcode is present or we're on a timeline page
			if ( is_admin() || ( is_a( $post, 'WP_Post' ) && 
				( has_shortcode( $post->post_content, 'cool-timeline' ) || 
				  has_block( 'cool-timeline/timeline', $post ) ) ) ) {
				
				$this->ctl_load_assets();
			}
		}

		private function ctl_load_assets() {
			// Minimal CSS
			wp_enqueue_style( 
				'cool-timeline', 
				CTL_PLUGIN_URL . 'assets/css/timeline.min.css', 
				array(), 
				CTL_V 
			);
			
			// Load JS only if needed for interactive features
			if ( $this->ctl_needs_js() ) {
				wp_enqueue_script( 
					'cool-timeline', 
					CTL_PLUGIN_URL . 'assets/js/timeline.min.js', 
					array( 'jquery' ), 
					CTL_V, 
					true 
				);
			}
		}

		private function ctl_needs_js() {
			// Determine if JS is actually needed
			// Return true only for features that require JS
			return false; // Most timeline layouts don't need JS
		}

		public function ctl_register_blocks() {
			register_block_type( 'cool-timeline/timeline', array(
				'render_callback' => array( $this, 'ctl_render_timeline_block' ),
				'attributes'      => array(
					'layout' => array(
						'type'    => 'string',
						'default' => 'vertical',
					),
					'showMedia' => array(
						'type'    => 'boolean',
						'default' => true,
					),
					'postsPerPage' => array(
						'type'    => 'number',
						'default' => 10,
					),
				),
			) );
		}

		public function ctl_render_timeline_block( $attributes ) {
			// Use caching for block output
			$cache_key = 'timeline_block_' . md5( serialize( $attributes ) );
			$output = wp_cache_get( $cache_key, $this->cache_group );
			
			if ( false === $output ) {
				$output = $this->ctl_generate_timeline_output( $attributes );
				wp_cache_set( $cache_key, $output, $this->cache_group, $this->cache_time );
			}
			
			return $output;
		}

		private function ctl_generate_timeline_output( $args ) {
			$defaults = array(
				'layout'       => 'vertical',
				'show_media'   => true,
				'posts_per_page' => 10,
				'order'        => 'DESC',
			);
			
			$args = wp_parse_args( $args, $defaults );
			
			// Optimized query with caching
			$cache_key = 'timeline_posts_' . md5( serialize( $args ) );
			$timeline_posts = wp_cache_get( $cache_key, $this->cache_group );
			
			if ( false === $timeline_posts ) {
				$timeline_posts = $this->ctl_get_timeline_posts( $args );
				wp_cache_set( $cache_key, $timeline_posts, $this->cache_group, $this->cache_time / 2 ); // Shorter cache for posts
			}
			
			ob_start();
			$this->ctl_display_timeline( $timeline_posts, $args );
			return ob_get_clean();
		}

		private function ctl_get_timeline_posts( $args ) {
			$query_args = array(
				'post_type'      => 'cool_timeline',
				'posts_per_page' => intval( $args['posts_per_page'] ),
				'order'          => $args['order'],
				'orderby'        => 'meta_value_num',
				'meta_key'       => 'ctl_story_timestamp',
				'meta_query'     => array(
					array(
						'key'     => 'ctl_story_timestamp',
						'compare' => 'EXISTS',
					),
				),
				// Performance optimizations
				'no_found_rows'  => true, // Skip counting total rows
				'update_post_meta_cache' => false,
				'update_post_term_cache' => false,
			);
			
			return get_posts( $query_args );
		}

		private function ctl_display_timeline( $posts, $args ) {
			if ( empty( $posts ) ) {
				return;
			}
			
			$layout_class = 'ctl-layout-' . sanitize_html_class( $args['layout'] );
			?>
			<div class="cool-timeline <?php echo $layout_class; ?>">
				<?php foreach ( $posts as $post ) : 
					setup_postdata( $post );
					$this->ctl_display_timeline_item( $post, $args );
				endforeach; 
				wp_reset_postdata();
				?>
			</div>
			<?php
		}

		private function ctl_display_timeline_item( $post, $args ) {
			$story_date = get_post_meta( $post->ID, 'ctl_story_date', true );
			$media = $args['show_media'] ? $this->ctl_get_story_media( $post->ID ) : array();
			?>
			<div class="ctl-item" data-date="<?php echo esc_attr( $story_date ); ?>">
				<div class="ctl-item-content">
					<?php if ( ! empty( $media['featured_image'] ) ) : ?>
						<div class="ctl-media">
							<img src="<?php echo esc_url( $media['featured_image']['url'] ); ?>" 
								 alt="<?php echo esc_attr( $media['featured_image']['alt'] ); ?>" 
								 loading="lazy">
						</div>
					<?php endif; ?>
					
					<div class="ctl-date"><?php echo esc_html( $story_date ); ?></div>
					<h3 class="ctl-title"><?php echo esc_html( get_the_title( $post ) ); ?></h3>
					<div class="ctl-content">
						<?php echo wp_kses_post( get_the_content( null, false, $post ) ); ?>
					</div>
					
					<?php if ( ! empty( $media['gallery'] ) ) : ?>
						<div class="ctl-gallery">
							<?php foreach ( array_slice( $media['gallery'], 0, 5 ) as $image ) : // Limit to 5 images ?>
								<img src="<?php echo esc_url( $image['url'] ); ?>" 
									 alt="<?php echo esc_attr( $image['alt'] ); ?>" 
									 loading="lazy">
							<?php endforeach; ?>
						</div>
					<?php endif; ?>
				</div>
			</div>
			<?php
		}

		// Optimized media retrieval
		public function ctl_get_story_media( $post_id ) {
			$cache_key = 'story_media_' . $post_id;
			$media = wp_cache_get( $cache_key, $this->cache_group );
			
			if ( false !== $media ) {
				return $media;
			}
			
			$media = array();
			
			// Featured image - use built-in WordPress function
			if ( has_post_thumbnail( $post_id ) ) {
				$thumb_id = get_post_thumbnail_id( $post_id );
				$media['featured_image'] = array(
					'id'  => $thumb_id,
					'url' => wp_get_attachment_image_url( $thumb_id, 'medium' ), // Use smaller size
					'alt' => get_post_meta( $thumb_id, '_wp_attachment_image_alt', true )
				);
			}
			
			// Gallery images - limit to reasonable number
			$gallery_images = get_post_meta( $post_id, 'ctl_gallery_images', true );
			if ( ! empty( $gallery_images ) && is_array( $gallery_images ) ) {
				$media['gallery'] = array();
				foreach ( array_slice( $gallery_images, 0, 10 ) as $image_id ) { // Limit to 10 images
					$image_url = wp_get_attachment_image_url( $image_id, 'thumbnail' );
					if ( $image_url ) {
						$media['gallery'][] = array(
							'id'  => $image_id,
							'url' => $image_url,
							'alt' => get_post_meta( $image_id, '_wp_attachment_image_alt', true )
						);
					}
				}
			}
			
			wp_cache_set( $cache_key, $media, $this->cache_group, $this->cache_time );
			return $media;
		}

		public function ctl_save_story_meta( $post_id, $post, $update ) {
			if ( defined( 'DOING_AUTOSAVE' ) && DOING_AUTOSAVE ) {
				return;
			}
			
			if ( 'cool_timeline' !== $post->post_type ) {
				return;
			}
			
			// Clear cache when story is saved
			$this->ctl_clear_cache();

			if ( isset( $_POST['ctl_story_date'] ) ) {
				$story_date = sanitize_text_field( $_POST['ctl_story_date'] );
				$story_timestamp = $this->ctl_generate_timestamp( $story_date );
				update_post_meta( $post_id, 'ctl_story_timestamp', $story_timestamp );
				update_post_meta( $post_id, 'ctl_story_date', $story_date );
			}
		}

		private function ctl_generate_timestamp( $date_string ) {
			return strtotime( $date_string );
		}

		private function ctl_clear_cache() {
			// Clear our custom cache group
			wp_cache_delete( 'timeline_data', $this->cache_group );
			// You might want to implement more specific cache clearing
		}

		public function ctl_load_plugin_textdomain() {
			load_plugin_textdomain( 'cool-timeline', false, basename( dirname( __FILE__ ) ) . '/languages/' );
		}

		public function ctl_flush_rules() {
			if ( get_option( 'ctl_flush_rewrite_rules_flag' ) ) {
				flush_rewrite_rules();
				delete_option( 'ctl_flush_rewrite_rules_flag' );
			}
		}

		public function ctl_settings_link( $links ) {
			array_unshift( $links, '<a href="admin.php?page=cool_timeline_settings">Settings</a>' );
			return $links;
		}

		public function ctl_activate() {
			update_option( 'ctl_flush_rewrite_rules_flag', true );
			// Minimal activation
		}

		public function ctl_deactivate() {
			$this->ctl_clear_cache();
			// Clean deactivation
		}
	}
}

// Initialize the plugin
$cool_timeline = CoolTimelineLite::get_instance();
$cool_timeline->registers();