
        <?php get_header(); ?>
        
        <div class="artwork-grid">
            <?php if (have_posts()) : while (have_posts()) : the_post(); ?>
                <article class="artwork-item">
                    <a href="<?php the_permalink(); ?>">
                        <?php if (has_post_thumbnail()) : ?>
                            <?php the_post_thumbnail('artwork-thumbnail'); ?>
                        <?php endif; ?>
                        
                        <div class="artwork-info">
                            <h2 class="artwork-title"><?php the_title(); ?></h2>
                            <div class="artwork-price"><?php echo get_artwork_meta('artwork_price'); ?></div>
                            <div class="artwork-medium"><?php echo get_artwork_meta('artwork_medium'); ?></div>
                        </div>
                    </a>
                </article>
            <?php endwhile; endif; ?>
        </div>
        
        <?php get_footer(); ?>
        