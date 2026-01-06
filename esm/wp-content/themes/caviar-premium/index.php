<?php
/**
 * The main template file
 *
 * This is the most generic template file in a WordPress theme
 * and one of the two required files for a theme (the other being style.css).
 */

get_header();
?>

<main id="primary" class="site-main">
    <div class="central-block" style="padding: 2rem;">
        <?php
        if ( have_posts() ) :
            while ( have_posts() ) :
                the_post();
                ?>
                <article id="post-<?php the_ID(); ?>" <?php post_class(); ?> style="margin-bottom: 3rem;">
                    <header class="entry-header" style="text-align:center; margin-bottom:1.5rem;">
                        <?php the_title( '<h2 class="entry-title"><a href="' . esc_url( get_permalink() ) . '" rel="bookmark">', '</a></h2>' ); ?>
                    </header>

                    <div class="entry-content">
                        <?php
                        // If it's a search result or archive, show excerpt
                        if ( is_search() || is_archive() ) {
                            the_excerpt();
                        } else {
                            the_content();
                        }
                        ?>
                    </div>
                </article>
                <?php
            endwhile;

            // Navigation
            the_posts_navigation();

        else :
            ?>
            <section class="no-results not-found" style="text-align:center;">
                <header class="page-header">
                    <h1 class="page-title"><?php esc_html_e( 'Nothing Found', 'caviar-premium' ); ?></h1>
                </header>
                <div class="page-content">
                    <p><?php esc_html_e( 'It seems we can&rsquo;t find what you&rsquo;re looking for.', 'caviar-premium' ); ?></p>
                </div>
            </section>
            <?php
        endif;
        ?>
    </div>
</main>

<?php
get_footer();
