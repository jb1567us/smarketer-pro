<?php
/**
 * Plugin Name: Timeline Creator
 * Description: Create beautiful timelines with images, videos, and files
 * Version: 1.0.1
 * Author: Your Name
 */

// Prevent direct access
if (!defined('ABSPATH')) {
    exit;
}

// Define plugin constants
define('TIMELINE_CREATOR_VERSION', '1.0.1');
define('TIMELINE_CREATOR_PLUGIN_URL', plugin_dir_url(__FILE__));
define('TIMELINE_CREATOR_PLUGIN_PATH', plugin_dir_path(__FILE__));

class TimelineCreator {
    
    public function __construct() {
        add_action('init', array($this, 'init'));
        add_action('wp_enqueue_scripts', array($this, 'enqueue_scripts'));
        add_shortcode('timeline', array($this, 'timeline_shortcode'));
    }
    
    public function init() {
        $this->register_custom_post_type();
        $this->register_meta_fields();
        add_action('add_meta_boxes', array($this, 'add_meta_boxes'));
        add_action('save_post_timeline_event', array($this, 'save_timeline_meta'), 10, 2);
    }
    
    private function register_custom_post_type() {
        $labels = array(
            'name' => __('Timeline Events'),
            'singular_name' => __('Timeline Event'),
            'menu_name' => __('Timeline Events'),
            'name_admin_bar' => __('Timeline Event'),
            'add_new' => __('Add New'),
            'add_new_item' => __('Add New Timeline Event'),
            'new_item' => __('New Timeline Event'),
            'edit_item' => __('Edit Timeline Event'),
            'view_item' => __('View Timeline Event'),
            'all_items' => __('All Timeline Events'),
            'search_items' => __('Search Timeline Events'),
            'not_found' => __('No timeline events found.'),
            'not_found_in_trash' => __('No timeline events found in Trash.')
        );

        $args = array(
            'labels' => $labels,
            'public' => true,
            'publicly_queryable' => true,
            'show_ui' => true,
            'show_in_menu' => true,
            'query_var' => true,
            'rewrite' => array('slug' => 'timeline-event'),
            'capability_type' => 'post',
            'has_archive' => false,
            'hierarchical' => false,
            'menu_position' => null,
            'menu_icon' => 'dashicons-schedule',
            'supports' => array('title', 'editor', 'thumbnail'),
            'show_in_rest' => true,
        );

        register_post_type('timeline_event', $args);
    }
    
    private function register_meta_fields() {
        register_post_meta('timeline_event', '_timeline_date', array(
            'type' => 'string',
            'single' => true,
            'show_in_rest' => true,
            'sanitize_callback' => 'sanitize_text_field',
            'auth_callback' => function() {
                return current_user_can('edit_posts');
            }
        ));
        
        register_post_meta('timeline_event', '_timeline_media_type', array(
            'type' => 'string',
            'single' => true,
            'show_in_rest' => true,
            'sanitize_callback' => 'sanitize_text_field',
            'auth_callback' => function() {
                return current_user_can('edit_posts');
            }
        ));
        
        register_post_meta('timeline_event', '_timeline_video_url', array(
            'type' => 'string',
            'single' => true,
            'show_in_rest' => true,
            'sanitize_callback' => 'esc_url_raw',
            'auth_callback' => function() {
                return current_user_can('edit_posts');
            }
        ));
        
        register_post_meta('timeline_event', '_timeline_file_url', array(
            'type' => 'string',
            'single' => true,
            'show_in_rest' => true,
            'sanitize_callback' => 'esc_url_raw',
            'auth_callback' => function() {
                return current_user_can('edit_posts');
            }
        ));
    }
    
    public function add_meta_boxes() {
        add_meta_box(
            'timeline_details',
            'Timeline Event Details',
            array($this, 'render_meta_box'),
            'timeline_event',
            'normal',
            'high'
        );
    }
    
    public function render_meta_box($post) {
        wp_nonce_field('timeline_nonce_action', 'timeline_nonce');
        
        $date = get_post_meta($post->ID, '_timeline_date', true);
        $media_type = get_post_meta($post->ID, '_timeline_media_type', true) ?: 'none';
        $video_url = get_post_meta($post->ID, '_timeline_video_url', true);
        $file_url = get_post_meta($post->ID, '_timeline_file_url', true);
        
        ?>
        <div class="timeline-meta-fields">
            <p>
                <label for="timeline_date"><strong>Event Date:</strong></label>
                <input type="date" id="timeline_date" name="timeline_date" value="<?php echo esc_attr($date); ?>" style="width: 100%; max-width: 300px;">
                <br><small>Select the date for this timeline event</small>
            </p>
            
            <p>
                <label for="timeline_media_type"><strong>Media Type:</strong></label>
                <select id="timeline_media_type" name="timeline_media_type" style="width: 100%; max-width: 300px;">
                    <option value="none" <?php selected($media_type, 'none'); ?>>No Media</option>
                    <option value="image" <?php selected($media_type, 'image'); ?>>Featured Image</option>
                    <option value="video" <?php selected($media_type, 'video'); ?>>Video</option>
                    <option value="file" <?php selected($media_type, 'file'); ?>>File Attachment</option>
                </select>
            </p>
            
            <div id="video_field" style="display: <?php echo ($media_type == 'video') ? 'block' : 'none'; ?>; margin-top: 10px; padding: 10px; background: #f9f9f9;">
                <label for="timeline_video_url"><strong>Video URL:</strong></label>
                <input type="url" id="timeline_video_url" name="timeline_video_url" value="<?php echo esc_url($video_url); ?>" style="width: 100%; max-width: 500px;">
                <p class="description">Enter YouTube or Vimeo URL (e.g., https://www.youtube.com/watch?v=...)</p>
            </div>
            
            <div id="file_field" style="display: <?php echo ($media_type == 'file') ? 'block' : 'none'; ?>; margin-top: 10px; padding: 10px; background: #f9f9f9;">
                <label for="timeline_file_url"><strong>File Attachment:</strong></label>
                <div style="display: flex; align-items: center; gap: 10px;">
                    <input type="url" id="timeline_file_url" name="timeline_file_url" value="<?php echo esc_url($file_url); ?>" style="flex: 1; max-width: 500px;">
                    <button type="button" class="button" id="upload_file_btn">Upload File</button>
                </div>
                <p class="description">Upload PDF, DOC, or other files</p>
                <?php if (!empty($file_url)): ?>
                    <p class="description">Current file: <a href="<?php echo esc_url($file_url); ?>" target="_blank"><?php echo basename($file_url); ?></a></p>
                <?php endif; ?>
            </div>
        </div>
        
        <script>
        jQuery(document).ready(function($) {
            $('#timeline_media_type').change(function() {
                $('#video_field, #file_field').hide();
                if ($(this).val() === 'video') {
                    $('#video_field').show();
                } else if ($(this).val() === 'file') {
                    $('#file_field').show();
                }
            });
            
            // File upload functionality
            $('#upload_file_btn').click(function(e) {
                e.preventDefault();
                var fileFrame = wp.media({
                    title: 'Select File',
                    button: { text: 'Use File' },
                    multiple: false
                });
                
                fileFrame.on('select', function() {
                    var attachment = fileFrame.state().get('selection').first().toJSON();
                    $('#timeline_file_url').val(attachment.url);
                });
                
                fileFrame.open();
            });
        });
        </script>
        <?php
    }
    
    public function save_timeline_meta($post_id, $post) {
        // Check if nonce is set and valid
        if (!isset($_POST['timeline_nonce']) || !wp_verify_nonce($_POST['timeline_nonce'], 'timeline_nonce_action')) {
            return;
        }
        
        // Check if user has permissions
        if (!current_user_can('edit_post', $post_id)) {
            return;
        }
        
        // Check if not an autosave
        if (defined('DOING_AUTOSAVE') && DOING_AUTOSAVE) {
            return;
        }
        
        // Check post type
        if ($post->post_type != 'timeline_event') {
            return;
        }
        
        // Save fields
        $fields = array(
            'timeline_date' => '_timeline_date',
            'timeline_media_type' => '_timeline_media_type',
            'timeline_video_url' => '_timeline_video_url',
            'timeline_file_url' => '_timeline_file_url'
        );
        
        foreach ($fields as $field => $meta_key) {
            if (isset($_POST[$field])) {
                $value = $_POST[$field];
                
                // Sanitize based on field type
                switch ($field) {
                    case 'timeline_video_url':
                    case 'timeline_file_url':
                        $value = esc_url_raw($value);
                        break;
                    default:
                        $value = sanitize_text_field($value);
                        break;
                }
                
                update_post_meta($post_id, $meta_key, $value);
            } else {
                // Delete meta if field is not set
                delete_post_meta($post_id, $meta_key);
            }
        }
    }
    
    public function enqueue_scripts() {
        wp_enqueue_style(
            'timeline-creator-style',
            TIMELINE_CREATOR_PLUGIN_URL . 'assets/timeline-style.css',
            array(),
            TIMELINE_CREATOR_VERSION
        );
        
        wp_enqueue_script(
            'timeline-creator-script',
            TIMELINE_CREATOR_PLUGIN_URL . 'assets/timeline-script.js',
            array('jquery'),
            TIMELINE_CREATOR_VERSION,
            true
        );
        
        // Only enqueue media scripts on admin for timeline events
        if (is_admin()) {
            $screen = get_current_screen();
            if ($screen && $screen->post_type === 'timeline_event') {
                wp_enqueue_media();
                wp_enqueue_script('jquery');
            }
        }
    }
    
    public function timeline_shortcode($atts) {
        $atts = shortcode_atts(array(
            'category' => '',
            'limit' => -1,
            'order' => 'ASC',
            'show_dates' => 'yes'
        ), $atts);
        
        $args = array(
            'post_type' => 'timeline_event',
            'posts_per_page' => intval($atts['limit']),
            'order' => $atts['order'],
            'meta_key' => '_timeline_date',
            'orderby' => 'meta_value',
            'meta_type' => 'DATE',
        );
        
        if (!empty($atts['category'])) {
            $args['tax_query'] = array(
                array(
                    'taxonomy' => 'category',
                    'field' => 'slug',
                    'terms' => sanitize_text_field($atts['category'])
                )
            );
        }
        
        $timeline_events = new WP_Query($args);
        
        ob_start();
        
        if ($timeline_events->have_posts()) {
            echo '<div class="timeline-container">';
            
            $counter = 0;
            while ($timeline_events->have_posts()) {
                $timeline_events->the_post();
                $this->render_timeline_event($counter, $atts['show_dates']);
                $counter++;
            }
            
            echo '</div>';
        } else {
            echo '<p>No timeline events found.</p>';
        }
        
        wp_reset_postdata();
        return ob_get_clean();
    }
    
    private function render_timeline_event($counter, $show_dates = 'yes') {
        $post_id = get_the_ID();
        $date = get_post_meta($post_id, '_timeline_date', true);
        $media_type = get_post_meta($post_id, '_timeline_media_type', true);
        $video_url = get_post_meta($post_id, '_timeline_video_url', true);
        $file_url = get_post_meta($post_id, '_timeline_file_url', true);
        
        $date_display = '';
        if ($show_dates === 'yes' && !empty($date)) {
            $date_display = '<div class="timeline-date">' . date('F j, Y', strtotime($date)) . '</div>';
        }
        
        ?>
        <div class="timeline-event <?php echo ($counter % 2 == 0) ? 'left' : 'right'; ?>">
            <?php echo $date_display; ?>
            
            <div class="timeline-content">
                <h3 class="timeline-title"><?php the_title(); ?></h3>
                
                <div class="timeline-media">
                    <?php $this->render_media($media_type, $video_url, $file_url); ?>
                </div>
                
                <div class="timeline-description">
                    <?php the_content(); ?>
                </div>
                
                <?php if ($media_type === 'file' && !empty($file_url)): 
                    $file_name = basename($file_url);
                    $file_extension = pathinfo($file_name, PATHINFO_EXTENSION);
                ?>
                <div class="timeline-file">
                    <a href="<?php echo esc_url($file_url); ?>" class="file-download" target="_blank" download>
                        <span class="file-icon">📎</span>
                        Download <?php echo strtoupper($file_extension); ?> File
                    </a>
                </div>
                <?php endif; ?>
            </div>
        </div>
        <?php
    }
    
    private function render_media($media_type, $video_url, $file_url) {
        switch ($media_type) {
            case 'image':
                if (has_post_thumbnail()) {
                    echo '<div class="timeline-image">';
                    the_post_thumbnail('medium', array('class' => 'timeline-featured-image'));
                    echo '</div>';
                }
                break;
                
            case 'video':
                if (!empty($video_url)) {
                    echo '<div class="timeline-video">';
                    $embed_code = wp_oembed_get($video_url);
                    if ($embed_code) {
                        echo $embed_code;
                    } else {
                        echo '<p><a href="' . esc_url($video_url) . '" target="_blank">Watch Video</a></p>';
                    }
                    echo '</div>';
                }
                break;
                
            case 'file':
                // File preview is handled in the main event display
                break;
                
            default:
                // No media
                break;
        }
    }
}

// Initialize the plugin
function initialize_timeline_creator() {
    new TimelineCreator();
}
add_action('plugins_loaded', 'initialize_timeline_creator');

// Activation hook
register_activation_hook(__FILE__, 'timeline_creator_activate');
function timeline_creator_activate() {
    flush_rewrite_rules();
}

// Deactivation hook
register_deactivation_hook(__FILE__, 'timeline_creator_deactivate');
function timeline_creator_deactivate() {
    flush_rewrite_rules();
}