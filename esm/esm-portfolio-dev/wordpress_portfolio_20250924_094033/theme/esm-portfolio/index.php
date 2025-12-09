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
                <div class="category-description"><?php the_archive_description(); ?></div>
            </header>
        <?php endif; ?>
        
        <div class="artwork-grid">
            <?php while (have_posts()) : the_post(); ?>
                <div class="artwork-item">
                    <a href="<?php echo get_post_meta(get_the_ID(), 'saatchi_url', true); ?>" target="_blank" class="artwork-link">
                        <?php if (has_post_thumbnail()) : ?>
                            <?php the_post_thumbnail('large', array('class' => 'artwork-image')); ?>
                        <?php else : ?>
                            <img src="<?php echo get_template_directory_uri(); ?>/assets/placeholder.jpg" alt="<?php the_title(); ?>" class="artwork-image">
                        <?php endif; ?>
                        <div class="artwork-overlay">
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
