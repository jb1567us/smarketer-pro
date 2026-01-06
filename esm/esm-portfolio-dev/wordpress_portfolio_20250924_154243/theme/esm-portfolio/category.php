<?php
/**
 * The template for displaying category archive pages
 */
get_header();
?>

<div class="container">
    <header class="category-header">
        <h1 class="category-title"><?php single_cat_title(); ?></h1>
    </header>
    
    <div class="artwork-grid">
        <?php if (have_posts()) : ?>
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
                        </div>
                    </a>
                </div>
            <?php endwhile; ?>
        <?php else : ?>
            <p>No artworks found in this category.</p>
        <?php endif; ?>
    </div>
    
    <?php the_posts_navigation(); ?>
</div>

<?php get_footer(); ?>
