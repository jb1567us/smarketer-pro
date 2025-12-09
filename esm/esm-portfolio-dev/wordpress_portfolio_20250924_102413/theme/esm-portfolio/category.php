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
                <div class="artwork-item">
                    <a href="<?php echo get_post_meta(get_the_ID(), 'saatchi_url', true); ?>" target="_blank" class="artwork-link">
                        <?php if (has_post_thumbnail()) : ?>
                            <?php the_post_thumbnail('large', array('class' => 'artwork-image')); ?>
                        <?php else : ?>
                            <img src="<?php echo get_template_directory_uri(); ?>/assets/placeholder.jpg" alt="<?php the_title(); ?>" class="artwork-image">
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
