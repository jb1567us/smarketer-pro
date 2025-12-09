<?php
/**
 * The main template file
 */
get_header(); ?>

<div class="content-container">
    <div class="content-wrapper">
        <?php if (have_posts()): ?>
            <header class="page-header">
                <h1 class="page-title">
                    <?php
                    if (is_home() && !is_front_page()) {
                        single_post_title();
                    } elseif (is_archive()) {
                        the_archive_title();
                    } elseif (is_search()) {
                        printf(__('Search Results for: %s', 'collaborative-archive'), get_search_query());
                    } else {
                        bloginfo('name');
                    }
                    ?>
                </h1>
            </header>
            
            <div class="posts-grid">
                <?php while (have_posts()): the_post(); ?>
                    <article <?php post_class('post-card'); ?>>
                        <header class="entry-header">
                            <h2 class="entry-title">
                                <a href="<?php the_permalink(); ?>"><?php the_title(); ?></a>
                            </h2>
                            <div class="entry-meta">
                                <span class="posted-on">
                                    <?php echo get_the_date(); ?>
                                </span>
                                <?php if ('post' === get_post_type()): ?>
                                <span class="byline">
                                    by <?php the_author(); ?>
                                </span>
                                <?php endif; ?>
                            </div>
                        </header>
                        
                        <?php if (has_post_thumbnail()): ?>
                        <div class="post-thumbnail">
                            <a href="<?php the_permalink(); ?>">
                                <?php the_post_thumbnail('medium'); ?>
                            </a>
                        </div>
                        <?php endif; ?>
                        
                        <div class="entry-content">
                            <?php the_excerpt(); ?>
                        </div>
                        
                        <footer class="entry-footer">
                            <a href="<?php the_permalink(); ?>" class="read-more">
                                Read More
                            </a>
                        </footer>
                    </article>
                <?php endwhile; ?>
            </div>
            
            <?php
            the_posts_pagination(array(
                'prev_text' => __('Previous', 'collaborative-archive'),
                'next_text' => __('Next', 'collaborative-archive'),
            ));
            ?>
            
        <?php else: ?>
            <div class="no-content">
                <h2><?php _e('Nothing Found', 'collaborative-archive'); ?></h2>
                <p><?php _e('Sorry, no content found.', 'collaborative-archive'); ?></p>
            </div>
        <?php endif; ?>
    </div>
</div>

<?php get_footer(); ?>