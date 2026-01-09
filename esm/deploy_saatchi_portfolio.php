<?php
// deploy_saatchi_portfolio.php
// Create mobile-first single-column portfolio linking to Saatchi

require_once($_SERVER['DOCUMENT_ROOT'] . '/wp-load.php');
echo "<h1>🎨 Deploying Saatchi Portfolio Homepage</h1>";

$mu_dir = $_SERVER['DOCUMENT_ROOT'] . '/wp-content/mu-plugins';

// Delete the old homepage filter if it exists
if (file_exists($mu_dir . '/esm-homepage-grid.php')) {
    unlink($mu_dir . '/esm-homepage-grid.php');
    echo "🧹 Removed old homepage grid<br>";
}

$plugin_code = <<<'PHP'
<?php
/* Plugin Name: ESM Saatchi Portfolio Homepage */
/* Description: Mobile-first single-column gallery linking to Saatchi Art */

add_action('template_redirect', function() {
    if (is_home() || is_front_page()) {
        add_action('wp_head', function() {
            echo '<style>
                /* Hide default content */
                .wp-block-post-template,
                .wp-block-query,
                main > .wp-block-group > *:not(.saatchi-portfolio) {
                    display: none !important;
                }
                
                /* Portfolio styles */
                .saatchi-portfolio {
                    max-width: 600px;
                    margin: 2rem auto;
                    padding: 0 1rem;
                }
                
                .artwork-item {
                    margin-bottom: 3rem;
                    text-align: center;
                }
                
                .artwork-item img {
                    width: 100%;
                    height: auto;
                    display: block;
                    transition: opacity 0.3s ease;
                }
                
                .artwork-item a:hover img {
                    opacity: 0.85;
                }
                
                .artwork-title {
                    margin-top: 0.75rem;
                    font-size: 1.1rem;
                    color: #333;
                }
                
                @media (max-width: 768px) {
                    .saatchi-portfolio {
                        max-width: 100%;
                    }
                }
            </style>';
        }, 999);
        
        add_filter('the_content', function($content) {
            global $wp_query;
            
            // Only on main query
            if (!$wp_query->is_main_query()) {
                return $content;
            }
            
            // Get all published posts
            $posts = get_posts([
                'post_type' => 'post',
                'posts_per_page' => -1,
                'post_status' => 'publish',
                'orderby' => 'date',
                'order' => 'DESC'
            ]);
            
            if (empty($posts)) {
                return '<p>No artwork found.</p>';
            }
            
            // Build single-column portfolio
            $html = '<div class="saatchi-portfolio">';
            
            foreach ($posts as $post) {
                $thumbnail_id = get_post_thumbnail_id($post->ID);
                if (!$thumbnail_id) continue;
                
                $image_url = wp_get_attachment_image_url($thumbnail_id, 'large');
                $title = get_the_title($post->ID);
                
                // Create Saatchi URL from title
                // Format: https://www.saatchiart.com/art/Painting-[title-slug]
                $slug = sanitize_title($title);
                $slug = str_replace('-painting', '', $slug);
                $slug = str_replace('-sculpture', '', $slug);
                $slug = str_replace('-collage', '', $slug);
                $slug = str_replace('-installation', '', $slug);
                $slug = str_replace('-print', '', $slug);
                
                // Construct Saatchi URL
                $saatchi_url = 'https://www.saatchiart.com/art/Painting-' . ucfirst($slug);
                
                $html .= '<div class="artwork-item">';
                $html .= '<a href="' . esc_url($saatchi_url) . '" target="_blank" rel="noopener">';
                $html .= '<img src="' . esc_url($image_url) . '" alt="' . esc_attr($title) . '" loading="lazy">';
                $html .= '</a>';
                $html .= '<div class="artwork-title">' . esc_html($title) . '</div>';
                $html .= '</div>';
            }
            
            $html .= '</div>';
            
            return $html;
        }, 999);
    }
});
PHP;

file_put_contents($mu_dir . '/esm-saatchi-portfolio.php', $plugin_code);
echo "✅ Installed esm-saatchi-portfolio.php<br>";

if (function_exists('opcache_reset'))
    opcache_reset();
if (function_exists('wp_cache_flush'))
    wp_cache_flush();

echo "<br><a href='/'>Check Saatchi Portfolio Homepage</a>";
?>