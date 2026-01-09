<?php
// deploy_homepage_filter.php
// MU-Plugin to override homepage content with artwork grid

require_once($_SERVER['DOCUMENT_ROOT'] . '/wp-load.php');
echo "<h1>🎨 Deploying Homepage Content Filter</h1>";

$mu_dir = $_SERVER['DOCUMENT_ROOT'] . '/wp-content/mu-plugins';

$plugin_code = <<<'PHP'
<?php
/* Plugin Name: ESM Homepage Artwork Grid */
/* Description: Shows artwork portfolio grid on homepage */

add_action('template_redirect', function() {
    if (is_home() || is_front_page()) {
        // Remove the_content filter to prevent placeholder
        remove_all_filters('the_content');
        
        add_filter('the_content', function($content) {
            // Get all published posts
            $posts = get_posts([
                'post_type' => 'post',
                'posts_per_page' => 100,
                'post_status' => 'publish',
                'orderby' => 'date',
                'order' => 'DESC'
            ]);
            
            if (empty($posts)) {
                return '<p>No artwork found.</p>';
            }
            
            // Build grid HTML
            $html = '<div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 2rem; max-width: 1200px; margin: 2rem auto; padding: 0 1rem;">';
            
            foreach ($posts as $post) {
                $thumbnail = get_the_post_thumbnail($post->ID, 'medium', ['style' => 'width: 100%; height: auto; aspect-ratio: 1;']);
                $title = get_the_title($post->ID);
                $link = get_permalink($post->ID);
                
                $html .= '<div style="text-align: center;">';
                if ($thumbnail) {
                    $html .= '<a href="' . esc_url($link) . '">' . $thumbnail . '</a>';
                }
                $html .= '<h3 style="margin: 0.5rem 0;"><a href="' . esc_url($link) . '" style="text-decoration: none; color: inherit;">' . esc_html($title) . '</a></h3>';
                $html .= '</div>';
            }
            
            $html .= '</div>';
            
            return $html;
        }, 999);
    }
}, 1);
PHP;

file_put_contents($mu_dir . '/esm-homepage-grid.php', $plugin_code);
echo "✅ Installed esm-homepage-grid.php<br>";

if (function_exists('opcache_reset'))
    opcache_reset();
if (function_exists('wp_cache_flush'))
    wp_cache_flush();

echo "<br><a href='/'>Check Homepage Grid</a>";
?>