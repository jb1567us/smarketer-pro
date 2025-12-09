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
        <?php while (have_posts()) : the_post(); ?>
            <article id="post-<?php the_ID(); ?>" <?php post_class(); ?>>
                <div class="entry-content">
                    <?php the_content(); ?>
                </div>
            </article>
        <?php endwhile; ?>
    <?php else : ?>
        <div class="no-content">
            <h1>Nothing Found</h1>
            <p>Sorry, no content available.</p>
        </div>
    <?php endif; ?>
</div>

<?php get_footer(); ?>
