<?php
/**
 * Single Book Chapter template
 */
get_header(); ?>

<div class="chapter-container">
    <div class="chapter-content">
        <article id="chapter-<?php the_ID(); ?>" <?php post_class('single-chapter'); ?>>
            <header class="chapter-header">
                <?php
                $arc_terms = get_the_terms(get_the_ID(), 'narrative_arc');
                $status = get_field('chapter_status');
                ?>
                
                <?php if ($arc_terms && !is_wp_error($arc_terms)): ?>
                <div class="chapter-arcs">
                    <?php foreach ($arc_terms as $term): ?>
                    <span class="arc-tag arc-<?php echo esc_attr(sanitize_title($term->name)); ?>">
                        <?php echo esc_html($term->name); ?>
                    </span>
                    <?php endforeach; ?>
                </div>
                <?php endif; ?>
                
                <h1 class="chapter-title"><?php the_title(); ?></h1>
                
                <div class="chapter-meta">
                    <div class="meta-left">
                        <span class="author">By <?php the_author(); ?></span>
                        <span class="date">Last updated: <?php echo get_the_modified_date(); ?></span>
                    </div>
                    <div class="meta-right">
                        <?php echo get_chapter_status_badge($status); ?>
                    </div>
                </div>
                
                <?php if (has_excerpt()): ?>
                <div class="chapter-description">
                    <?php the_excerpt(); ?>
                </div>
                <?php endif; ?>
            </header>
            
            <?php if (has_post_thumbnail()): ?>
            <div class="chapter-featured-image">
                <?php the_post_thumbnail('large'); ?>
            </div>
            <?php endif; ?>
            
            <div class="chapter-body">
                <?php the_content(); ?>
            </div>
            
            <?php
            $primary_source = get_field('primary_source');
            if ($primary_source):
            ?>
            <footer class="chapter-footer">
                <div class="source-citation">
                    <h4>Primary Source</h4>
                    <p><?php echo esc_html($primary_source); ?></p>
                </div>
            </footer>
            <?php endif; ?>
            
            <?php
            // If comments are open or we have at least one comment, load up the comment template.
            if (comments_open() || get_comments_number()):
                comments_template();
            endif;
            ?>
        </article>
    </div>
</div>

<?php get_footer(); ?>