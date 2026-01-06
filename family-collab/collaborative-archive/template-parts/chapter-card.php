<?php
/**
 * Template part for displaying chapter cards
 * 
 * @package Collaborative_Archive
 */

// Exit if accessed directly
if (!defined('ABSPATH')) {
    exit;
}

$status = get_field('chapter_status');
$primary_source = get_field('primary_source');
$arc_terms = get_the_terms(get_the_ID(), 'narrative_arc');
$modified_date = get_the_modified_time('U');
$current_time = current_time('timestamp');
$time_diff = human_time_diff($modified_date, $current_time);
?>

<article id="chapter-<?php the_ID(); ?>" <?php post_class('chapter-card'); ?>>
    
    <header class="chapter-card-header">
        <h3 class="chapter-card-title">
            <a href="<?php the_permalink(); ?>" rel="bookmark">
                <?php the_title(); ?>
            </a>
        </h3>
        
        <?php if ($arc_terms && !is_wp_error($arc_terms)): ?>
        <div class="chapter-card-arcs">
            <?php foreach ($arc_terms as $term): 
                $slug = sanitize_title($term->name);
            ?>
            <span class="arc-tag arc-<?php echo esc_attr($slug); ?>">
                <?php echo esc_html($term->name); ?>
            </span>
            <?php endforeach; ?>
        </div>
        <?php endif; ?>
    </header>
    
    <?php if (has_post_thumbnail()): ?>
    <div class="chapter-card-thumbnail">
        <a href="<?php the_permalink(); ?>">
            <?php the_post_thumbnail('medium', array(
                'alt' => get_the_title(),
                'loading' => 'lazy'
            )); ?>
        </a>
    </div>
    <?php endif; ?>
    
    <div class="chapter-card-content">
        <?php if (has_excerpt()): ?>
        <div class="chapter-card-excerpt">
            <?php the_excerpt(); ?>
        </div>
        <?php else: ?>
        <div class="chapter-card-excerpt">
            <p><?php echo wp_trim_words(get_the_content(), 25, '...'); ?></p>
        </div>
        <?php endif; ?>
        
        <?php if ($primary_source): ?>
        <div class="chapter-card-source">
            <strong>Source:</strong> <?php echo esc_html($primary_source); ?>
        </div>
        <?php endif; ?>
    </div>
    
    <footer class="chapter-card-footer">
        <div class="chapter-card-meta">
            <div class="meta-status">
                <?php echo ca_get_chapter_status_badge($status); ?>
            </div>
            
            <div class="meta-dates">
                <span class="modified-date" title="<?php echo get_the_modified_date(); ?>">
                    Updated: <?php echo $time_diff; ?> ago
                </span>
                <?php if ('published' === $status): ?>
                <span class="publish-date">
                    Published: <?php echo get_the_date(); ?>
                </span>
                <?php endif; ?>
            </div>
        </div>
        
        <div class="chapter-card-actions">
            <a href="<?php the_permalink(); ?>" class="read-chapter button button-small">
                Read Chapter
            </a>
            
            <?php if (is_user_logged_in() && get_current_user_id() == get_the_author_ID()): ?>
            <a href="<?php echo get_edit_post_link(); ?>" class="edit-chapter button button-small button-secondary">
                Edit
            </a>
            <?php endif; ?>
        </div>
    </footer>
    
    <?php 
    // Add progress indicator for drafts
    if ('draft' === $status || 'needs_review' === $status):
        $progress = ca_calculate_chapter_progress();
        if ($progress > 0):
    ?>
    <div class="chapter-progress">
        <div class="progress-bar">
            <div class="progress-fill" style="width: <?php echo $progress; ?>%;"></div>
        </div>
        <span class="progress-text"><?php echo $progress; ?>% complete</span>
    </div>
    <?php 
        endif;
    endif; 
    ?>
    
</article>

<?php
/**
 * Calculate chapter progress based on content and metadata
 */
function ca_calculate_chapter_progress() {
    $progress = 0;
    
    // Content length (40% weight)
    $content = get_the_content();
    if (str_word_count(strip_tags($content)) > 500) {
        $progress += 40;
    } elseif (str_word_count(strip_tags($content)) > 200) {
        $progress += 20;
    }
    
    // Excerpt (15% weight)
    if (has_excerpt()) {
        $progress += 15;
    }
    
    // Featured image (15% weight)
    if (has_post_thumbnail()) {
        $progress += 15;
    }
    
    // Primary source (15% weight)
    if (get_field('primary_source')) {
        $progress += 15;
    }
    
    // Narrative arcs (15% weight)
    $arcs = get_the_terms(get_the_ID(), 'narrative_arc');
    if ($arcs && !is_wp_error($arcs) && !empty($arcs)) {
        $progress += 15;
    }
    
    return min($progress, 100);
}