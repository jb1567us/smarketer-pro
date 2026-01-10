<?php
// fix_portfolio_display.php
// Use template_include to completely override the homepage template

require_once($_SERVER['DOCUMENT_ROOT'] . '/wp-load.php');
echo "<h1>🎨 Fixing Portfolio Display</h1>";

$mu_dir = $_SERVER['DOCUMENT_ROOT'] . '/wp-content/mu-plugins';

// Remove the old plugin that wasn't working
if (file_exists($mu_dir . '/esm-saatchi-portfolio.php')) {
    unlink($mu_dir . '/esm-saatchi-portfolio.php');
    echo "🧹 Removed non-working plugin<br>";
}

$plugin_code = <<<'PHP'
<?php
/* Plugin Name: ESM Saatchi Portfolio Direct */
/* Description: Directly renders Saatchi portfolio on homepage */

add_filter('template_include', function($template) {
    if (is_home() || is_front_page()) {
        // Get header
        get_header();
        
        // Custom portfolio content
        echo '<main style="max-width: 600px; margin: 2rem auto; padding: 0 1rem;">';
        
        $posts = get_posts([
            'post_type' => 'post',
            'posts_per_page' => -1,
            'post_status' => 'publish',
            'orderby' => 'date',
            'order' => 'DESC'
        ]);
        
        foreach ($posts as $post) {
            $thumbnail_id = get_post_thumbnail_id($post->ID);
            if (!$thumbnail_id) continue;
            
            $image_url = wp_get_attachment_image_url($thumbnail_id, 'large');
            $title = get_the_title($post->ID);
            
            // Create Saatchi URL
            $slug = sanitize_title($title);
            $slug = str_replace(['-painting', '-sculpture', '-collage', '-installation', '-print'], '', $slug);
            $saatchi_url = 'https://www.saatchiart.com/art/Painting-' . ucfirst($slug);
            
            echo '<div style="margin-bottom: 3rem; text-align: center;">';
            echo '<a href="' . esc_url($saatchi_url) . '" target="_blank" rel="noopener">';
            echo '<img src="' . esc_url($image_url) . '" alt="' . esc_attr($title) . '" style="width: 100%; height: auto; display: block;">';
            echo '</a>';
            echo '<div style="margin-top: 0.75rem; font-size: 1.1rem; color: #333;">' . esc_html($title) . '</div>';
            echo '</div>';
        }
        
        echo '</main>';
        
        // Get footer
        get_footer();
        
        return false; // Don't load default template
    }
    
    return $template;
}, 99);
PHP;

file_put_contents($mu_dir . '/esm-saatchi-direct.php', $plugin_code);
echo "✅ Installed esm-saatchi-direct.php<br>";

if (function_exists('opcache_reset'))
    opcache_reset();
if (function_exists('wp_cache_flush'))
    wp_cache_flush();

echo "<br><a href='/'>Check Fixed Portfolio</a>";
?>