<?php
/**
 * The main template file
 *
 * This is the most generic template file in a WordPress theme
 * and one of the two required files for a theme (the other being style.css).
 * It is used to display a page when nothing more specific matches a query.
 */

get_header();
?>

<div class="artwork-archive">
    <div class="artwork-list">
        <?php
        if (have_posts()) :
            while (have_posts()) : the_post();
                $image_url = get_post_meta(get_the_ID(), 'artwork_image_url', true);
                $saatchi_url = get_post_meta(get_the_ID(), 'saatchi_url', true);
                ?>
                
                <div class="artwork-item">
                    <a href="<?php echo esc_url($saatchi_url); ?>" target="_blank" class="artwork-link">
                        <?php if ($image_url) : ?>
                            <div class="artwork-image-container">
                                <img src="<?php echo esc_url($image_url); ?>" alt="<?php the_title(); ?>" class="artwork-image">
                            </div>
                        <?php else : ?>
                            <div class="artwork-image-placeholder">No Image Available</div>
                        <?php endif; ?>
                        <div class="artwork-info">
                            <h2 class="artwork-title"><?php the_title(); ?></h2>
                        </div>
                    </a>
                </div>
                
            <?php endwhile;
            
            // Pagination
            the_posts_pagination(array(
                'mid_size' => 2,
                'prev_text' => __('&larr; Previous', 'esm-portfolio'),
                'next_text' => __('Next &rarr;', 'esm-portfolio'),
            ));
            
        else : ?>
            <div class="no-artworks">
                <p><?php esc_html_e('No artworks found.', 'esm-portfolio'); ?></p>
            </div>
        <?php endif; ?>
    </div>
</div>

<?php get_footer(); ?>