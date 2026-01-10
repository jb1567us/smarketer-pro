
        <?php
        function esm_portfolio_setup() {
            add_theme_support('post-thumbnails');
            add_theme_support('title-tag');
            add_theme_support('html5', array('search-form', 'comment-form', 'comment-list', 'gallery', 'caption'));
            
            // Register navigation menus
            register_nav_menus(array(
                'primary' => __('Primary Menu', 'esm-portfolio'),
            ));
            
            // Custom image sizes
            add_image_size('artwork-thumbnail', 400, 300, true);
            add_image_size('artwork-large', 1200, 800, false);
        }
        add_action('after_setup_theme', 'esm_portfolio_setup');
        
        function esm_portfolio_scripts() {
            wp_enqueue_style('esm-portfolio-style', get_stylesheet_uri());
            
            // Google Fonts
            wp_enqueue_style('esm-google-fonts', 'https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap', array(), null);
        }
        add_action('wp_enqueue_scripts', 'esm_portfolio_scripts');
        
        // Add custom post meta for artwork details
        function get_artwork_meta($meta_key) {
            global $post;
            return get_post_meta($post->ID, $meta_key, true);
        }
        
        // Create custom menu walker for simple navigation
        class Simple_Menu_Walker extends Walker_Nav_Menu {
            function start_el(&$output, $item, $depth = 0, $args = array(), $id = 0) {
                $output .= '<li class="' . implode(' ', $item->classes) . '"><a href="' . $item->url . '">' . $item->title . '</a>';
            }
            
            function end_el(&$output, $item, $depth = 0, $args = array()) {
                $output .= '</li>';
            }
        }
        ?>
        