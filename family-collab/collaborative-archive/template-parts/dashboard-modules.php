<?php
/**
 * Template part for dashboard modules
 * 
 * @package Collaborative_Archive
 */

// Exit if accessed directly
if (!defined('ABSPATH')) {
    exit;
}

/**
 * Collaboration Hotspots Module
 */
function ca_collaboration_hotspots_module() {
    if (!is_user_logged_in()) {
        return;
    }
    ?>
    <section class="collaboration-module">
        <div class="welcome-back">
            <h2>Welcome Back, <?php echo esc_html(wp_get_current_user()->display_name); ?>!</h2>
            <p>Your Co-Author Status:</p>
        </div>
        
        <div class="todo-widgets">
            <?php ca_next_up_widget(); ?>
            <?php ca_pending_edits_widget(); ?>
        </div>
    </section>
    <?php
}

/**
 * Next Up Widget - Shows latest edited chapter
 */
function ca_next_up_widget() {
    $latest_chapter = new WP_Query(array(
        'post_type' => 'book_chapter',
        'author' => get_current_user_id(),
        'posts_per_page' => 1,
        'orderby' => 'modified'
    ));
    ?>
    <div class="next-up">
        <h3>Continue Editing:</h3>
        <?php if ($latest_chapter->have_posts()): 
            while ($latest_chapter->have_posts()): $latest_chapter->the_post(); 
                $edit_link = get_edit_post_link();
                $status = get_field('chapter_status');
            ?>
            <a href="<?php echo esc_url($edit_link); ?>" class="chapter-link">
                <?php the_title(); ?>
            </a>
            <?php echo ca_get_chapter_status_badge($status); ?>
            <p class="modified">Last edited: <?php echo human_time_diff(get_the_modified_time('U'), current_time('timestamp')); ?> ago</p>
            <?php endwhile; 
        else: ?>
            <p>No chapters yet. Start writing your family history!</p>
            <a href="<?php echo admin_url('post-new.php?post_type=book_chapter'); ?>" class="button">
                Create First Chapter
            </a>
        <?php endif; 
        wp_reset_postdata(); ?>
    </div>
    <?php
}

/**
 * Pending Edits Widget
 */
function ca_pending_edits_widget() {
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
    ?>
    <div class="pending-edits">
        <h3>Collaboration Tasks</h3>
        <?php if ($pending_chapters->have_posts()): ?>
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
    <?php
}

/**
 * Diplomatic Trail Map Module
 */
function ca_diplomatic_trail_module() {
    ?>
    <section class="diplomatic-trail">
        <h2>José Sancha Padrós: The Diplomatic Trail</h2>
        <div class="world-map-container">
            <div id="sancha-journey-map">
                <div class="map-placeholder">
                    <h3>The Journey of José Sancha Padrós</h3>
                    <p class="journey-path">Madrid → London → Paris → Moscow → Sofia → East Berlin → Madrid</p>
                    <div class="journey-timeline">
                        <?php ca_render_journey_timeline(); ?>
                    </div>
                    <p class="map-note">Interactive map coming soon</p>
                </div>
            </div>
        </div>
        
        <div class="family-snapshot">
            <h3>Family Overview</h3>
            <?php ca_family_snapshot(); ?>
        </div>
    </section>
    <?php
}

/**
 * Render Journey Timeline
 */
function ca_render_journey_timeline() {
    $journey_points = array(
        array('year' => '1908', 'location' => 'Madrid', 'event' => 'Born in San Lorenzo de El Escorial'),
        array('year' => '1912-1923', 'location' => 'London', 'event' => 'Childhood with family'),
        array('year' => '1931', 'location' => 'Paris', 'event' => 'Art scholarship'),
        array('year' => '1939', 'location' => 'Moscow', 'event' => 'Exile after Civil War'),
        array('year' => '1950s', 'location' => 'Sofia', 'event' => 'Theater work & illustrations'),
        array('year' => '1958', 'location' => 'East Berlin', 'event' => 'Film & teaching work'),
        array('year' => '1966', 'location' => 'Madrid', 'event' => 'Return to Spain'),
    );
    
    foreach ($journey_points as $point) {
        echo '<div class="journey-point">';
        echo '<span class="journey-year">' . esc_html($point['year']) . '</span>';
        echo '<span class="journey-location">' . esc_html($point['location']) . '</span>';
        echo '<span class="journey-event">' . esc_html($point['event']) . '</span>';
        echo '</div>';
    }
}

/**
 * Family Snapshot
 */
function ca_family_snapshot() {
    if (shortcode_exists('wp_genealogy')) {
        echo do_shortcode('[wp_genealogy family="sancha-padros" depth="2"]');
    } else {
        echo '<div class="family-placeholder">';
        echo '<h4>Sancha Padrós Family</h4>';
        echo '<ul>';
        echo '<li><strong>José María Sancha Padrós</strong> (1908-1994) - Artist</li>';
        echo '<li><strong>Francisco Sancha Lengo</strong> (Father) - Illustrator</li>';
        echo '<li><strong>Matilde Padrós</strong> (Mother)</li>';
        echo '<li><strong>Anelia Stoyanova</strong> (Wife)</li>';
        echo '<li><strong>Soledad Sancha</strong> (Sister) - Also exiled</li>';
        echo '</ul>';
        echo '<p>Install WP Genealogy plugin to display interactive family tree.</p>';
        echo '</div>';
    }
}

/**
 * Double Life Timeline Module
 */
function ca_double_life_timeline_module() {
    ?>
    <section class="double-life-timeline">
        <h2>Key Turning Points (1908–1994)</h2>
        <?php 
        if (shortcode_exists('cool-timeline')) {
            echo do_shortcode('[cool-timeline layout="horizontal" category="key-turning-points" designs="design-1" items="5"]');
        } else {
            ca_basic_timeline_fallback();
        }
        ?>
    </section>
    <?php
}

/**
 * Basic Timeline Fallback
 */
function ca_basic_timeline_fallback() {
    $key_events = array(
        '1908' => 'Born in San Lorenzo de El Escorial, Spain',
        '1912-1923' => 'Childhood in London with family',
        '1931' => 'Scholarship to study in Paris, connects with contemporary art',
        '1936-1939' => 'Spanish Civil War, fights for Republic',
        '1939' => 'Exile to Moscow after Civil War',
        '1940s' => 'VENONA Project codename "REMBRANDT" active',
        '1951' => 'Co-founds Aleko Konstantinov Satire Theater in Sofia',
        '1958' => 'Moves to East Berlin, works in film and education',
        '1966' => 'Returns permanently to Madrid',
        '1994' => 'Dies in Madrid'
    );
    
    echo '<div class="basic-timeline">';
    foreach ($key_events as $year => $event) {
        echo '<div class="timeline-event">';
        echo '<span class="timeline-year">' . esc_html($year) . '</span>';
        echo '<span class="timeline-description">' . esc_html($event) . '</span>';
        echo '</div>';
    }
    echo '</div>';
}

/**
 * Latest Chapters Module
 */
function ca_latest_chapters_module($posts_per_page = 6) {
    ?>
    <section class="latest-chapters">
        <h2>Latest Drafts & Research</h2>
        <div class="chapters-grid">
            <?php 
            $chapters = new WP_Query(array(
                'post_type' => 'book_chapter',
                'posts_per_page' => $posts_per_page,
                'orderby' => 'modified',
                'order' => 'DESC'
            ));
            
            if ($chapters->have_posts()): 
                while ($chapters->have_posts()): $chapters->the_post();
                    get_template_part('template-parts/chapter-card');
                endwhile; 
            else:
                ca_no_chapters_fallback();
            endif; 
            wp_reset_postdata(); 
            ?>
        </div>
        
        <?php if ($chapters->found_posts > $posts_per_page): ?>
        <div class="view-all-chapters">
            <a href="<?php echo get_post_type_archive_link('book_chapter'); ?>" class="button button-secondary">
                View All Chapters (<?php echo $chapters->found_posts; ?>)
            </a>
        </div>
        <?php endif; ?>
    </section>
    <?php
}

/**
 * No Chapters Fallback
 */
function ca_no_chapters_fallback() {
    ?>
    <div class="no-chapters">
        <h3>No Chapters Yet</h3>
        <p>Start building your family history book by creating the first chapter.</p>
        <?php if (is_user_logged_in()): ?>
        <a href="<?php echo admin_url('post-new.php?post_type=book_chapter'); ?>" class="button">
            Create First Chapter
        </a>
        <?php endif; ?>
    </div>
    <?php
}

/**
 * Enhanced Chapter Status Badge
 */
function ca_get_chapter_status_badge($status) {
    $statuses = array(
        'draft' => array(
            'label' => 'Draft', 
            'class' => 'status-draft',
            'icon' => '📝'
        ),
        'needs_review' => array(
            'label' => 'Needs Review', 
            'class' => 'status-needs_review',
            'icon' => '👀'
        ),
        'ready_to_publish' => array(
            'label' => 'Ready to Publish', 
            'class' => 'status-ready_to_publish',
            'icon' => '✅'
        ),
        'published' => array(
            'label' => 'Published', 
            'class' => 'status-published',
            'icon' => '📖'
        )
    );
    
    if (isset($statuses[$status])) {
        return '<span class="status ' . $statuses[$status]['class'] . '">' . 
               $statuses[$status]['icon'] . ' ' . $statuses[$status]['label'] . '</span>';
    }
    
    return '<span class="status status-draft">📝 Draft</span>';
}

/**
 * Render Narrative Arc Tags
 */
function ca_render_narrative_arcs($post_id = null) {
    if (!$post_id) {
        $post_id = get_the_ID();
    }
    
    $arc_terms = get_the_terms($post_id, 'narrative_arc');
    if ($arc_terms && !is_wp_error($arc_terms)) {
        echo '<div class="narrative-arcs">';
        foreach ($arc_terms as $term) {
            $slug = sanitize_title($term->name);
            echo '<span class="arc-tag arc-' . esc_attr($slug) . '">' . esc_html($term->name) . '</span>';
        }
        echo '</div>';
    }
}

/**
 * Dashboard Stats Module
 */
function ca_dashboard_stats_module() {
    if (!is_user_logged_in()) {
        return;
    }
    
    $chapter_count = wp_count_posts('book_chapter');
    $user_chapters = new WP_Query(array(
        'post_type' => 'book_chapter',
        'author' => get_current_user_id(),
        'posts_per_page' => -1,
        'fields' => 'ids'
    ));
    ?>
    <section class="dashboard-stats">
        <h3>Project Statistics</h3>
        <div class="stats-grid">
            <div class="stat-card">
                <span class="stat-number"><?php echo $chapter_count->publish; ?></span>
                <span class="stat-label">Published Chapters</span>
            </div>
            <div class="stat-card">
                <span class="stat-number"><?php echo $chapter_count->draft; ?></span>
                <span class="stat-label">Drafts</span>
            </div>
            <div class="stat-card">
                <span class="stat-number"><?php echo $user_chapters->found_posts; ?></span>
                <span class="stat-label">Your Chapters</span>
            </div>
            <div class="stat-card">
                <span class="stat-number"><?php echo ca_count_pending_reviews(); ?></span>
                <span class="stat-label">Pending Reviews</span>
            </div>
        </div>
    </section>
    <?php
    wp_reset_postdata();
}

/**
 * Count pending reviews
 */
function ca_count_pending_reviews() {
    $pending = new WP_Query(array(
        'post_type' => 'book_chapter',
        'meta_query' => array(
            array(
                'key' => 'chapter_status',
                'value' => 'needs_review',
                'compare' => '='
            )
        ),
        'posts_per_page' => -1,
        'fields' => 'ids'
    ));
    
    return $pending->found_posts;
}