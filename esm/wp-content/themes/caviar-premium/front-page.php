<?php
/**
 * The template for displaying the front page (Portfolio Grid)
 */

get_header();
?>

<main id="primary" class="site-main">

    <div class="portfolio-grid">
        <?php
        $args = array(
            'post_type'      => 'page',
            'posts_per_page' => -1,
            'post_status'    => 'publish',
            'orderby'        => 'menu_order date',
            'order'          => 'DESC',
            'meta_key'       => '_thumbnail_id', // Only show pages with featured images
        );

        // Exclude specific utility pages if necessary (e.g., this page itself if set as static)
        $front_page_id = get_option('page_on_front');
        if ($front_page_id) {
            $args['post__not_in'] = array($front_page_id);
        }

        $query = new WP_Query($args);

        if ($query->have_posts()) :
            while ($query->have_posts()) : $query->the_post();
                // Skip if it's clearly not an artwork (simple exclusions by slug if needed)
                if (is_page(array('about', 'contact', 'home'))) continue;
                ?>
                <?php
                // Prioritize the 'saatchi_url' meta field which contains the correct verified linking
                $meta_url = get_post_meta(get_the_ID(), 'saatchi_url', true);
                
                if (!empty($meta_url)) {
                    $saatchi_url = $meta_url;
                } else {
                    // Fallback to hardcoded overrides if meta is missing
                    $custom_urls = array(
                        2153 => 'https://www.saatchiart.com/art/Printmaking-Right-Way-Limited-Edition-of-1/1295487/6444853/view',
                        2152 => 'https://www.saatchiart.com/art/Printmaking-Start-Sign-Limited-Edition-of-1/1295487/6444891/view',
                        2150 => 'https://elliotspencermorgan.com/no-public-shrooms-limited-edition-of-1/',
                        2107 => 'https://www.saatchiart.com/art/Painting-Mushroom-Exclamation/1295487/6492441/view',
                        2106 => 'https://www.saatchiart.com/art/Painting-Excited-Bird/1295487/6492447/view'
                    );
                    
                    $current_id = get_the_ID();
                    
                    if (array_key_exists($current_id, $custom_urls)) {
                        $saatchi_url = $custom_urls[$current_id];
                    } else {
                        // Default Logic (often broken/incomplete, but kept as last resort)
                        $title = get_the_title();
                        $slug = sanitize_title($title);
                        $slug = str_replace(array('-painting', '-sculpture', '-collage', '-installation', '-print'), '', $slug);
                        $saatchi_url = 'https://www.saatchiart.com/art/Painting-' . ucfirst($slug);
                    }
                }
                ?>
                <div class="artwork-card">
                    <a href="<?php echo esc_url($saatchi_url); ?>" target="_blank" rel="noopener">
                        <?php 
                        // Use full size image for all artworks to avoid missing thumbnail issues
                        if (has_post_thumbnail()) {
                            the_post_thumbnail('full');
                        }
                        ?>
                    </a>
                    <div class="artwork-card-title"><?php the_title(); ?></div>
                </div>
                <?php
            endwhile;
            wp_reset_postdata();
        else :
            echo '<p style="text-align:center">No artworks found.</p>';
        endif;
        ?>
    </div>

</main>

<?php
get_footer();
