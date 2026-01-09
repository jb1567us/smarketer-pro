<?php
/**
 * The homepage template
 */
get_header();
?>

<div class="homepage-container">
    <div class="artwork-grid">
        <?php
        // Query to get all artwork posts
        $artworks_query = new WP_Query(array(
            'post_type' => 'post',
            'posts_per_page' => -1,
            'meta_query' => array(
                array(
                    'key' => 'artwork_image_url',
                    'compare' => 'EXISTS'
                )
            )
        ));
        
        if ($artworks_query->have_posts()) :
            while ($artworks_query->have_posts()) : $artworks_query->the_post();
                $image_url = get_post_meta(get_the_ID(), 'artwork_image_url', true);
                $saatchi_url = get_post_meta(get_the_ID(), 'saatchi_url', true);
                $categories = get_the_category();
                $category_name = !empty($categories) ? $categories[0]->name : 'Artwork';
                ?>
                
                <div class="artwork-card">
                    <a href="<?php echo esc_url($saatchi_url); ?>" target="_blank" class="artwork-link">
                        <?php if ($image_url) : ?>
                            <div class="artwork-image-container">
                                <img src="<?php echo esc_url($image_url); ?>" alt="<?php the_title(); ?>" class="artwork-image">
                            </div>
                        <?php else : ?>
                            <div class="artwork-image-placeholder">No Image Available</div>
                        <?php endif; ?>
                        <div class="artwork-info">
                            <h3 class="artwork-title"><?php the_title(); ?></h3>
                            <span class="artwork-category"><?php echo esc_html($category_name); ?></span>
                        </div>
                    </a>
                </div>
                
            <?php endwhile;
            wp_reset_postdata();
        else : ?>
            <p>No artworks found.</p>
        <?php endif; ?>
    </div>
</div>

<?php get_footer(); ?>
