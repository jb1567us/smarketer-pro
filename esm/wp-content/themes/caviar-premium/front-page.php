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
                <div class="artwork-card">
                    <a href="<?php the_permalink(); ?>">
                        <?php 
                        if (has_post_thumbnail()) {
                            the_post_thumbnail('large');
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
