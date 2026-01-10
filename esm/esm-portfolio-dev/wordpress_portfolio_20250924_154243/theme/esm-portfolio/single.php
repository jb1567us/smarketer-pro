<?php
/**
 * The template for displaying single posts
 * Note: This template redirects to Saatchi Art, but is here as a fallback
 */
get_header();
?>

<div class="container">
    <article id="post-<?php the_ID(); ?>" <?php post_class(); ?>>
        <header class="entry-header">
            <h1 class="entry-title"><?php the_title(); ?></h1>
        </header>
        
        <div class="entry-content">
            <?php the_content(); ?>
            <p><a href="<?php echo get_post_meta(get_the_ID(), 'saatchi_url', true); ?>" target="_blank">View on Saatchi Art</a></p>
        </div>
    </article>
</div>

<?php get_footer(); ?>
