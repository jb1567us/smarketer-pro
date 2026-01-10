<?php
/**
 * The main template file
 *
 * @package ESM Portfolio
 */

get_header();
?>

<div class="container">
    <?php if (have_posts()) : ?>
        <?php if (is_category()) : ?>
            <header class="category-header">
                <h1 class="category-title"><?php single_cat_title(); ?></h1>
            </header>
        <?php endif; ?>
        
        <div class="artwork-grid">
            <?php while (have_posts()) : the_post(); ?>
                <div class="artwork-card">
                    <a href="<?php echo get_post_meta(get_the_ID(), 'saatchi_url', true); ?>" target="_blank" class="artwork-link">
                        <?php 
                        $image_url = get_post_meta(get_the_ID(), 'artwork_image_url', true);
                        if ($image_url) : ?>
                            <div class="artwork-image-container">
                                <img src="<?php echo esc_url($image_url); ?>" alt="<?php the_title(); ?>" class="artwork-image">
                            </div>
                        <?php else : ?>
                            <div class="artwork-image-placeholder">No Image Available</div>
                        <?php endif; ?>
                        <div class="artwork-info">
                            <h3 class="artwork-title"><?php the_title(); ?></h3>
                            <?php 
                            $categories = get_the_category();
                            if (!empty($categories)) {
                                echo '<span class="artwork-category">' . esc_html($categories[0]->name) . '</span>';
                            }
                            ?>
                        </div>
                    </a>
                </div>
            <?php endwhile; ?>
        </div>
        
        <?php the_posts_navigation(); ?>
    <?php else : ?>
        <div class="no-content">
            <h1>Nothing Found</h1>
            <p>Sorry, no content available.</p>
        </div>
    <?php endif; ?>
</div>

<?php get_footer(); ?>
