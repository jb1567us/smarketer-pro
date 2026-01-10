<?php
/**
 * Archive template for Book Chapters
 */
get_header(); ?>

<div class="archive-container">
    <div class="archive-header">
        <h1 class="archive-title">Book Chapters</h1>
        <div class="archive-description">
            <p>Explore all chapters of the José Sancha Padrós family history book.</p>
        </div>
        
        <?php
        $arc_terms = get_terms(array(
            'taxonomy' => 'narrative_arc',
            'hide_empty' => true,
        ));
        
        if ($arc_terms && !is_wp_error($arc_terms)):
        ?>
        <div class="archive-filters">
            <span>Filter by Narrative Arc:</span>
            <div class="filter-buttons">
                <a href="<?php echo get_post_type_archive_link('book_chapter'); ?>" class="filter-button active">All</a>
                <?php foreach ($arc_terms as $term): ?>
                <a href="<?php echo get_term_link($term); ?>" class="filter-button">
                    <?php echo esc_html($term->name); ?>
                </a>
                <?php endforeach; ?>
            </div>
        </div>
        <?php endif; ?>
    </div>
    
    <div class="chapters-archive-grid">
        <?php if (have_posts()): ?>
            <?php while (have_posts()): the_post(); 
                $status = get_field('chapter_status');
                $arc_terms = get_the_terms(get_the_ID(), 'narrative_arc');
            ?>
            <article class="chapter-archive-card">
                <header class="chapter-archive-header">
                    <h2 class="chapter-archive-title">
                        <a href="<?php the_permalink(); ?>"><?php the_title(); ?></a>
                    </h2>
                    
                    <?php if ($arc_terms && !is_wp_error($arc_terms)): ?>
                    <div class="chapter-archive-arcs">
                        <?php foreach ($arc_terms as $term): ?>
                        <span class="arc-tag arc-<?php echo esc_attr(sanitize_title($term->name)); ?>">
                            <?php echo esc_html($term->name); ?>
                        </span>
                        <?php endforeach; ?>
                    </div>
                    <?php endif; ?>
                </header>
                
                <?php if (has_excerpt()): ?>
                <div class="chapter-archive-excerpt">
                    <?php the_excerpt(); ?>
                </div>
                <?php endif; ?>
                
                <footer class="chapter-archive-footer">
                    <div class="chapter-archive-meta">
                        <?php echo get_chapter_status_badge($status); ?>
                        <span class="modified-date">
                            Updated: <?php echo human_time_diff(get_the_modified_time('U'), current_time('timestamp')); ?> ago
                        </span>
                    </div>
                    <a href="<?php the_permalink(); ?>" class="read-chapter">
                        Read Chapter
                    </a>
                </footer>
            </article>
            <?php endwhile; ?>
        <?php else: ?>
            <div class="no-chapters-found">
                <h3>No Chapters Found</h3>
                <p>No book chapters have been published yet.</p>
            </div>
        <?php endif; ?>
    </div>
    
    <?php
    the_posts_pagination(array(
        'prev_text' => __('Previous', 'collaborative-archive'),
        'next_text' => __('Next', 'collaborative-archive'),
    ));
    ?>
</div>

<?php get_footer(); ?>