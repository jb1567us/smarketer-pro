<?php
/**
 * The front page template for the Collaborative Archive dashboard
 */
get_header(); ?>

<div class="dashboard-container">
    
    <!-- Module A: Collaboration Hotspots -->
    <?php if (is_user_logged_in()): ?>
    <section class="collaboration-module">
        <div class="welcome-back">
            <h2>Welcome Back, <?php echo esc_html(wp_get_current_user()->display_name); ?>!</h2>
            <p>Your Co-Author Status:</p>
        </div>
        
        <div class="todo-widgets">
            <!-- Next Up: Latest Edited Chapter -->
            <?php 
            $latest_chapter = new WP_Query(array(
                'post_type' => 'book_chapter',
                'author' => get_current_user_id(),
                'posts_per_page' => 1,
                'orderby' => 'modified'
            ));
            
            if ($latest_chapter->have_posts()): 
                while ($latest_chapter->have_posts()): $latest_chapter->the_post(); 
                $edit_link = get_edit_post_link();
                ?>
                <div class="next-up">
                    <h3>Continue Editing:</h3>
                    <a href="<?php echo esc_url($edit_link); ?>" class="chapter-link">
                        <?php the_title(); ?>
                    </a>
                    <?php echo get_chapter_status_badge(get_field('chapter_status')); ?>
                    <p class="modified">Last edited: <?php echo human_time_diff(get_the_modified_time('U'), current_time('timestamp')); ?> ago</p>
                </div>
                <?php endwhile; 
            else: ?>
                <div class="next-up">
                    <h3>Get Started</h3>
                    <p>No chapters yet. Start writing your family history!</p>
                    <a href="<?php echo admin_url('post-new.php?post_type=book_chapter'); ?>" class="button">
                        Create First Chapter
                    </a>
                </div>
            <?php endif; 
            wp_reset_postdata(); ?>
            
            <!-- Pending Edits -->
            <div class="pending-edits">
                <h3>Collaboration Tasks</h3>
                <?php 
                $pending_chapters = new WP_Query(array(
                    'post_type' => 'book_chapter',
                    'meta_query' => array(
                        array(
                            'key' => 'chapter_status',
                            'value' => 'needs_review',
                            'compare' => '='
                        )
                    ),
                    'posts_per_page' => 3
                ));
                
                if ($pending_chapters->have_posts()): ?>
                    <ul class="pending-list">
                    <?php while ($pending_chapters->have_posts()): $pending_chapters->the_post(); ?>
                        <li>
                            <a href="<?php the_permalink(); ?>"><?php the_title(); ?></a>
                            <span class="needs-review-badge">Needs Review</span>
                        </li>
                    <?php endwhile; ?>
                    </ul>
                <?php else: ?>
                    <p>No chapters currently need review.</p>
                <?php endif; 
                wp_reset_postdata(); ?>
                
                <div class="quick-actions">
                    <a href="<?php echo admin_url('edit.php?post_type=book_chapter'); ?>" class="button button-secondary">
                        View All Chapters
                    </a>
                    <a href="<?php echo admin_url('post-new.php?post_type=book_chapter'); ?>" class="button">
                        Add New Chapter
                    </a>
                </div>
            </div>
        </div>
    </section>
    <?php endif; ?>
    
    <!-- Module B: The Diplomatic Trail Map -->
    <section class="diplomatic-trail">
        <h2>José Sancha Padrós: The Diplomatic Trail</h2>
        <div class="world-map-container">
            <div id="sancha-journey-map">
                <!-- This would be replaced with an interactive map or detailed image -->
                <div style="background: #e9ecef; padding: 4rem; border-radius: 8px; text-align: center;">
                    <h3 style="color: var(--navy); margin-bottom: 1rem;">The Journey of José Sancha Padrós</h3>
                    <p style="color: var(--medium-gray);">Madrid → London → Paris → Moscow → Sofia → East Berlin → Madrid</p>
                    <p style="margin-top: 1rem; font-style: italic;">Interactive map coming soon</p>
                </div>
            </div>
        </div>
        
        <div class="family-snapshot">
            <h3>Family Overview</h3>
            <?php 
            // This would integrate with WP Genealogy plugin
            if (shortcode_exists('wp_genealogy')) {
                echo do_shortcode('[wp_genealogy family="sancha-padros" depth="2"]');
            } else {
                echo '<p>Family tree plugin not active. Install WP Genealogy to display family data.</p>';
            }
            ?>
        </div>
    </section>
    
    <!-- Module C: The Double Life Timeline -->
    <section class="double-life-timeline">
        <h2>Key Turning Points (1908–1994)</h2>
        <?php 
        // This would integrate with Cool Timeline plugin
        if (shortcode_exists('cool-timeline')) {
            echo do_shortcode('[cool-timeline layout="horizontal" category="key-turning-points" designs="design-1" items="5"]');
        } else {
            echo '<p>Timeline plugin not active. Install Cool Timeline to visualize key events.</p>';
            
            // Fallback basic timeline
            echo '<div class="basic-timeline">';
            $key_events = array(
                '1908' => 'Born in San Lorenzo de El Escorial, Spain',
                '1912-1923' => 'Childhood in London with family',
                '1931' => 'Scholarship to study in Paris',
                '1939' => 'Exile to Moscow after Spanish Civil War',
                '1940s' => 'VENONA Project codename "REMBRANDT"',
                '1951' => 'Co-founds Satire Theater in Sofia',
                '1966' => 'Returns permanently to Madrid',
                '1994' => 'Dies in Madrid'
            );
            
            foreach ($key_events as $year => $event) {
                echo '<div class="timeline-event">';
                echo '<span class="timeline-year">' . esc_html($year) . '</span>';
                echo '<span class="timeline-description">' . esc_html($event) . '</span>';
                echo '</div>';
            }
            echo '</div>';
        }
        ?>
    </section>
    
    <!-- Module D: Latest Chapters & Narrative Arcs -->
    <section class="latest-chapters">
        <h2>Latest Drafts & Research</h2>
        <div class="chapters-grid">
            <?php 
            $chapters = new WP_Query(array(
                'post_type' => 'book_chapter',
                'posts_per_page' => 6,
                'orderby' => 'modified',
                'order' => 'DESC'
            ));
            
            if ($chapters->have_posts()): 
                while ($chapters->have_posts()): $chapters->the_post();
                    $status = get_field('chapter_status');
                    $arc_terms = get_the_terms(get_the_ID(), 'narrative_arc');
                    $primary_source = get_field('primary_source');
                ?>
                <article class="chapter-card">
                    <h3><a href="<?php the_permalink(); ?>"><?php the_title(); ?></a></h3>
                    
                    <?php if ($arc_terms && !is_wp_error($arc_terms)): ?>
                    <div class="narrative-arcs">
                        <?php foreach ($arc_terms as $term): ?>
                        <span class="arc-tag arc-<?php echo esc_attr(sanitize_title($term->name)); ?>">
                            <?php echo esc_html($term->name); ?>
                        </span>
                        <?php endforeach; ?>
                    </div>
                    <?php endif; ?>
                    
                    <?php if (has_excerpt()): ?>
                    <div class="chapter-excerpt">
                        <?php the_excerpt(); ?>
                    </div>
                    <?php endif; ?>
                    
                    <div class="chapter-meta">
                        <?php echo get_chapter_status_badge($status); ?>
                        <span class="modified">Modified: <?php echo human_time_diff(get_the_modified_time('U'), current_time('timestamp')); ?> ago</span>
                    </div>
                    
                    <?php if ($primary_source): ?>
                    <div class="primary-source">
                        Source: <?php echo esc_html($primary_source); ?>
                    </div>
                    <?php endif; ?>
                </article>
                <?php endwhile; 
            else: ?>
                <div class="no-chapters">
                    <h3>No Chapters Yet</h3>
                    <p>Start building your family history book by creating the first chapter.</p>
                    <?php if (is_user_logged_in()): ?>
                    <a href="<?php echo admin_url('post-new.php?post_type=book_chapter'); ?>" class="button">
                        Create First Chapter
                    </a>
                    <?php endif; ?>
                </div>
            <?php endif; 
            wp_reset_postdata(); ?>
        </div>
        
        <?php if ($chapters->found_posts > 6): ?>
        <div class="view-all-chapters" style="text-align: center; margin-top: 2rem;">
            <a href="<?php echo get_post_type_archive_link('book_chapter'); ?>" class="button button-secondary">
                View All Chapters (<?php echo $chapters->found_posts; ?>)
            </a>
        </div>
        <?php endif; ?>
    </section>
</div>

<?php get_footer(); ?>