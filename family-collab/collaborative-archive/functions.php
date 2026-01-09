<?php
/**
 * Collaborative Archive Theme functions and definitions
 */

if (!defined('ABSPATH')) {
    exit; // Exit if accessed directly
}

// Theme setup
function collaborative_archive_setup() {
    add_theme_support('title-tag');
    add_theme_support('post-thumbnails');
    add_theme_support('custom-logo');
    add_theme_support('html5', array(
        'search-form',
        'comment-form',
        'comment-list',
        'gallery',
        'caption',
    ));
    
    // Add support for editor styles
    add_theme_support('editor-styles');
    add_editor_style('assets/css/editor-style.css');
    
    // Register navigation menus
    register_nav_menus(array(
        'primary' => __('Primary Menu', 'collaborative-archive'),
        'footer' => __('Footer Menu', 'collaborative-archive'),
    ));
    
    // Set content width
    if (!isset($content_width)) {
        $content_width = 1200;
    }
    
    // Add custom image sizes
    add_image_size('chapter-thumbnail', 400, 250, true);
    add_image_size('chapter-featured', 800, 400, true);
    add_image_size('timeline-image', 300, 200, true);
}
add_action('after_setup_theme', 'collaborative_archive_setup');

// Enqueue scripts and styles
function collaborative_archive_scripts() {
    // Google Fonts
    wp_enqueue_style('google-fonts', 'https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Playfair+Display:wght@400;500;600;700&display=swap', array(), null);
    
    // Main stylesheet
    wp_enqueue_style('collaborative-archive-style', get_stylesheet_uri(), array(), '1.0.0');
    
    // Custom CSS
    wp_enqueue_style('collaborative-archive-custom', get_template_directory_uri() . '/assets/css/custom.css', array(), '1.0.0');
    
    // JavaScript
    wp_enqueue_script('collaborative-archive-script', get_template_directory_uri() . '/assets/js/custom.js', array('jquery'), '1.0.0', true);
    
    // Localize script for AJAX
    wp_localize_script('collaborative-archive-script', 'ca_ajax', array(
        'ajax_url' => admin_url('admin-ajax.php'),
        'nonce' => wp_create_nonce('ca_nonce')
    ));
}
add_action('wp_enqueue_scripts', 'collaborative_archive_scripts');

// Include template parts
require get_template_directory() . '/template-parts/dashboard-modules.php';
require get_template_directory() . '/template-parts/chapter-card.php';

// Register Custom Post Type: Book Chapters
function create_book_chapter_cpt() {
    $labels = array(
        'name' => _x('Chapters', 'Post Type General Name', 'collaborative-archive'),
        'singular_name' => _x('Chapter', 'Post Type Singular Name', 'collaborative-archive'),
        'menu_name' => __('Book Chapters', 'collaborative-archive'),
        'name_admin_bar' => __('Chapter', 'collaborative-archive'),
        'archives' => __('Chapter Archives', 'collaborative-archive'),
        'attributes' => __('Chapter Attributes', 'collaborative-archive'),
        'parent_item_colon' => __('Parent Chapter:', 'collaborative-archive'),
        'all_items' => __('All Chapters', 'collaborative-archive'),
        'add_new_item' => __('Add New Chapter', 'collaborative-archive'),
        'add_new' => __('Add New', 'collaborative-archive'),
        'new_item' => __('New Chapter', 'collaborative-archive'),
        'edit_item' => __('Edit Chapter', 'collaborative-archive'),
        'update_item' => __('Update Chapter', 'collaborative-archive'),
        'view_item' => __('View Chapter', 'collaborative-archive'),
        'view_items' => __('View Chapters', 'collaborative-archive'),
        'search_items' => __('Search Chapter', 'collaborative-archive'),
        'not_found' => __('Not found', 'collaborative-archive'),
        'not_found_in_trash' => __('Not found in Trash', 'collaborative-archive'),
        'featured_image' => __('Featured Image', 'collaborative-archive'),
        'set_featured_image' => __('Set featured image', 'collaborative-archive'),
        'remove_featured_image' => __('Remove featured image', 'collaborative-archive'),
        'use_featured_image' => __('Use as featured image', 'collaborative-archive'),
        'insert_into_item' => __('Insert into chapter', 'collaborative-archive'),
        'uploaded_to_this_item' => __('Uploaded to this chapter', 'collaborative-archive'),
        'items_list' => __('Chapters list', 'collaborative-archive'),
        'items_list_navigation' => __('Chapters list navigation', 'collaborative-archive'),
        'filter_items_list' => __('Filter chapters list', 'collaborative-archive'),
    );
    
    $args = array(
        'label' => __('Chapter', 'collaborative-archive'),
        'description' => __('Book chapters for the family history project', 'collaborative-archive'),
        'labels' => $labels,
        'supports' => array('title', 'editor', 'author', 'thumbnail', 'excerpt', 'comments', 'custom-fields', 'revisions'),
        'taxonomies' => array('narrative_arc'),
        'hierarchical' => false,
        'public' => true,
        'show_ui' => true,
        'show_in_menu' => true,
        'menu_position' => 5,
        'menu_icon' => 'dashicons-book-alt',
        'show_in_admin_bar' => true,
        'show_in_nav_menus' => true,
        'can_export' => true,
        'has_archive' => true,
        'exclude_from_search' => false,
        'publicly_queryable' => true,
        'capability_type' => 'post',
        'show_in_rest' => true,
        'rewrite' => array('slug' => 'chapters'),
    );
    register_post_type('book_chapter', $args);
}
add_action('init', 'create_book_chapter_cpt', 0);

// Register Narrative Arc Taxonomy
function create_narrative_arc_taxonomy() {
    $labels = array(
        'name' => _x('Narrative Arcs', 'Taxonomy General Name', 'collaborative-archive'),
        'singular_name' => _x('Narrative Arc', 'Taxonomy Singular Name', 'collaborative-archive'),
        'menu_name' => __('Narrative Arcs', 'collaborative-archive'),
        'all_items' => __('All Narrative Arcs', 'collaborative-archive'),
        'parent_item' => __('Parent Narrative Arc', 'collaborative-archive'),
        'parent_item_colon' => __('Parent Narrative Arc:', 'collaborative-archive'),
        'new_item_name' => __('New Narrative Arc Name', 'collaborative-archive'),
        'add_new_item' => __('Add New Narrative Arc', 'collaborative-archive'),
        'edit_item' => __('Edit Narrative Arc', 'collaborative-archive'),
        'update_item' => __('Update Narrative Arc', 'collaborative-archive'),
        'view_item' => __('View Narrative Arc', 'collaborative-archive'),
        'separate_items_with_commas' => __('Separate narrative arcs with commas', 'collaborative-archive'),
        'add_or_remove_items' => __('Add or remove narrative arcs', 'collaborative-archive'),
        'choose_from_most_used' => __('Choose from the most used', 'collaborative-archive'),
        'popular_items' => __('Popular Narrative Arcs', 'collaborative-archive'),
        'search_items' => __('Search Narrative Arcs', 'collaborative-archive'),
        'not_found' => __('Not Found', 'collaborative-archive'),
        'no_terms' => __('No narrative arcs', 'collaborative-archive'),
        'items_list' => __('Narrative arcs list', 'collaborative-archive'),
        'items_list_navigation' => __('Narrative arcs list navigation', 'collaborative-archive'),
    );
    
    $args = array(
        'labels' => $labels,
        'hierarchical' => true,
        'public' => true,
        'show_ui' => true,
        'show_admin_column' => true,
        'show_in_nav_menus' => true,
        'show_tagcloud' => true,
        'show_in_rest' => true,
        'rewrite' => array('slug' => 'narrative-arc'),
    );
    register_taxonomy('narrative_arc', array('book_chapter'), $args);
}
add_action('init', 'create_narrative_arc_taxonomy', 0);

// Add default narrative arcs
function add_default_narrative_arcs() {
    $arcs = array('Art & Culture', 'The Political Life', 'The Intelligence File');
    
    foreach ($arcs as $arc) {
        if (!term_exists($arc, 'narrative_arc')) {
            wp_insert_term($arc, 'narrative_arc');
        }
    }
}
add_action('init', 'add_default_narrative_arcs');

// Custom dashboard functionality
function get_pending_collaboration_tasks() {
    if (!is_user_logged_in()) {
        return array();
    }
    
    $current_user = wp_get_current_user();
    $tasks = array();
    
    // Get chapters that need review
    $chapters_needing_review = new WP_Query(array(
        'post_type' => 'book_chapter',
        'meta_query' => array(
            array(
                'key' => 'chapter_status',
                'value' => 'needs_review',
                'compare' => '='
            )
        ),
        'posts_per_page' => 5
    ));
    
    if ($chapters_needing_review->have_posts()) {
        while ($chapters_needing_review->have_posts()) {
            $chapters_needing_review->the_post();
            $tasks[] = array(
                'type' => 'review',
                'title' => get_the_title(),
                'link' => get_edit_post_link(),
                'author' => get_the_author()
            );
        }
    }
    wp_reset_postdata();
    
    return $tasks;
}

// AJAX handler for dashboard updates
function update_dashboard_modules() {
    check_ajax_referer('ca_nonce', 'nonce');
    
    $module = sanitize_text_field($_POST['module']);
    $data = array();
    
    switch ($module) {
        case 'collaboration_tasks':
            $data = get_pending_collaboration_tasks();
            break;
        case 'recent_chapters':
            $chapters = new WP_Query(array(
                'post_type' => 'book_chapter',
                'posts_per_page' => 5,
                'orderby' => 'modified',
                'order' => 'DESC'
            ));
            
            if ($chapters->have_posts()) {
                while ($chapters->have_posts()) {
                    $chapters->the_post();
                    $data[] = array(
                        'title' => get_the_title(),
                        'link' => get_permalink(),
                        'modified' => human_time_diff(get_the_modified_time('U'), current_time('timestamp')),
                        'status' => get_field('chapter_status'),
                        'arcs' => wp_get_post_terms(get_the_ID(), 'narrative_arc', array('fields' => 'names'))
                    );
                }
            }
            wp_reset_postdata();
            break;
    }
    
    wp_send_json_success($data);
}
add_action('wp_ajax_update_dashboard_modules', 'update_dashboard_modules');
add_action('wp_ajax_nopriv_update_dashboard_modules', 'update_dashboard_modules');

// Add custom body class for dashboard
function add_dashboard_body_class($classes) {
    if (is_front_page()) {
        $classes[] = 'dashboard-page';
    }
    return $classes;
}
add_filter('body_class', 'add_dashboard_body_class');

// Helper function to get chapter status badge
function get_chapter_status_badge($status) {
    $statuses = array(
        'draft' => array('label' => 'Draft', 'class' => 'status-draft'),
        'needs_review' => array('label' => 'Needs Review', 'class' => 'status-needs_review'),
        'ready_to_publish' => array('label' => 'Ready to Publish', 'class' => 'status-ready_to_publish'),
        'published' => array('label' => 'Published', 'class' => 'status-published')
    );
    
    if (isset($statuses[$status])) {
        return '<span class="status ' . $statuses[$status]['class'] . '">' . $statuses[$status]['label'] . '</span>';
    }
    
    return '<span class="status status-draft">Draft</span>';
}

// Add body classes for different template types
function ca_body_classes($classes) {
    if (is_singular('book_chapter')) {
        $classes[] = 'single-chapter';
        
        $status = get_field('chapter_status');
        if ($status) {
            $classes[] = 'chapter-status-' . $status;
        }
    }
    
    if (is_post_type_archive('book_chapter')) {
        $classes[] = 'chapter-archive';
    }
    
    if (is_front_page()) {
        $classes[] = 'front-dashboard';
    }
    
    return $classes;
}
add_filter('body_class', 'ca_body_classes');

// Customizer settings for the theme
function ca_customize_register($wp_customize) {
    // Add theme options section
    $wp_customize->add_section('ca_theme_options', array(
        'title' => __('Theme Options', 'collaborative-archive'),
        'priority' => 30,
    ));
    
    // Dashboard welcome message
    $wp_customize->add_setting('ca_welcome_message', array(
        'default' => 'Welcome to the Collaborative Archive',
        'sanitize_callback' => 'sanitize_text_field',
    ));
    
    $wp_customize->add_control('ca_welcome_message', array(
        'label' => __('Dashboard Welcome Message', 'collaborative-archive'),
        'section' => 'ca_theme_options',
        'type' => 'text',
    ));
    
    // Project description
    $wp_customize->add_setting('ca_project_description', array(
        'default' => 'A collaborative family history project',
        'sanitize_callback' => 'sanitize_textarea_field',
    ));
    
    $wp_customize->add_control('ca_project_description', array(
        'label' => __('Project Description', 'collaborative-archive'),
        'section' => 'ca_theme_options',
        'type' => 'textarea',
    ));
    
    // Primary color
    $wp_customize->add_setting('ca_primary_color', array(
        'default' => '#1a237e',
        'sanitize_callback' => 'sanitize_hex_color',
    ));
    
    $wp_customize->add_control(new WP_Customize_Color_Control($wp_customize, 'ca_primary_color', array(
        'label' => __('Primary Color', 'collaborative-archive'),
        'section' => 'ca_theme_options',
    )));
    
    // Secondary color
    $wp_customize->add_setting('ca_secondary_color', array(
        'default' => '#d4af37',
        'sanitize_callback' => 'sanitize_hex_color',
    ));
    
    $wp_customize->add_control(new WP_Customize_Color_Control($wp_customize, 'ca_secondary_color', array(
        'label' => __('Secondary Color', 'collaborative-archive'),
        'section' => 'ca_theme_options',
    )));
}
add_action('customize_register', 'ca_customize_register');

// Add custom CSS from theme options
function ca_custom_colors_css() {
    $primary_color = get_theme_mod('ca_primary_color', '#1a237e');
    $secondary_color = get_theme_mod('ca_secondary_color', '#d4af37');
    ?>
    <style type="text/css">
        :root {
            --navy: <?php echo $primary_color; ?>;
            --gold: <?php echo $secondary_color; ?>;
        }
    </style>
    <?php
}
add_action('wp_head', 'ca_custom_colors_css');

// Add dashboard widgets for authors
function ca_add_dashboard_widgets() {
    if (current_user_can('edit_posts')) {
        wp_add_dashboard_widget(
            'ca_recent_chapters_widget',
            __('Your Recent Chapters', 'collaborative-archive'),
            'ca_recent_chapters_dashboard_widget'
        );
        
        wp_add_dashboard_widget(
            'ca_project_stats_widget',
            __('Project Statistics', 'collaborative-archive'),
            'ca_project_stats_dashboard_widget'
        );
    }
}
add_action('wp_dashboard_setup', 'ca_add_dashboard_widgets');

// Recent chapters dashboard widget
function ca_recent_chapters_dashboard_widget() {
    $chapters = new WP_Query(array(
        'post_type' => 'book_chapter',
        'author' => get_current_user_id(),
        'posts_per_page' => 5,
        'orderby' => 'modified',
        'order' => 'DESC'
    ));
    
    if ($chapters->have_posts()) {
        echo '<ul>';
        while ($chapters->have_posts()) {
            $chapters->the_post();
            $status = get_field('chapter_status');
            echo '<li>';
            echo '<a href="' . get_edit_post_link() . '">' . get_the_title() . '</a>';
            echo ' <span class="status status-' . $status . '">' . $status . '</span>';
            echo '</li>';
        }
        echo '</ul>';
    } else {
        echo '<p>No chapters yet. <a href="' . admin_url('post-new.php?post_type=book_chapter') . '">Create your first chapter</a>.</p>';
    }
    wp_reset_postdata();
}

// Project stats dashboard widget
function ca_project_stats_dashboard_widget() {
    $chapter_count = wp_count_posts('book_chapter');
    $total_chapters = $chapter_count->publish + $chapter_count->draft + $chapter_count->pending;
    
    echo '<div class="dashboard-stats">';
    echo '<p><strong>Total Chapters:</strong> ' . $total_chapters . '</p>';
    echo '<p><strong>Published:</strong> ' . $chapter_count->publish . '</p>';
    echo '<p><strong>Drafts:</strong> ' . $chapter_count->draft . '</p>';
    echo '<p><strong>Pending Review:</strong> ' . $chapter_count->pending . '</p>';
    echo '</div>';
}

// Shortcode for displaying recent chapters
function ca_recent_chapters_shortcode($atts) {
    $atts = shortcode_atts(array(
        'count' => 5,
        'status' => 'published',
        'arc' => ''
    ), $atts);
    
    $args = array(
        'post_type' => 'book_chapter',
        'posts_per_page' => intval($atts['count']),
        'orderby' => 'date',
        'order' => 'DESC'
    );
    
    if ($atts['status'] !== 'all') {
        $args['meta_query'] = array(
            array(
                'key' => 'chapter_status',
                'value' => $atts['status'],
                'compare' => '='
            )
        );
    }
    
    if (!empty($atts['arc'])) {
        $args['tax_query'] = array(
            array(
                'taxonomy' => 'narrative_arc',
                'field' => 'slug',
                'terms' => $atts['arc']
            )
        );
    }
    
    $chapters = new WP_Query($args);
    $output = '';
    
    if ($chapters->have_posts()) {
        $output .= '<div class="recent-chapters-shortcode">';
        while ($chapters->have_posts()) {
            $chapters->the_post();
            $output .= '<div class="chapter-item">';
            $output .= '<h4><a href="' . get_permalink() . '">' . get_the_title() . '</a></h4>';
            $output .= '<p>' . get_the_excerpt() . '</p>';
            $output .= '</div>';
        }
        $output .= '</div>';
    } else {
        $output .= '<p>No chapters found.</p>';
    }
    
    wp_reset_postdata();
    return $output;
}
add_shortcode('recent_chapters', 'ca_recent_chapters_shortcode');

// Add custom columns to chapter admin
function ca_add_chapter_admin_columns($columns) {
    $new_columns = array();
    
    foreach ($columns as $key => $value) {
        $new_columns[$key] = $value;
        if ($key === 'title') {
            $new_columns['chapter_status'] = __('Status', 'collaborative-archive');
            $new_columns['narrative_arc'] = __('Narrative Arc', 'collaborative-archive');
        }
    }
    
    return $new_columns;
}
add_filter('manage_book_chapter_posts_columns', 'ca_add_chapter_admin_columns');

// Populate custom admin columns
function ca_populate_chapter_admin_columns($column, $post_id) {
    switch ($column) {
        case 'chapter_status':
            $status = get_field('chapter_status', $post_id);
            if ($status) {
                echo '<span class="status status-' . $status . '">' . ucfirst($status) . '</span>';
            }
            break;
            
        case 'narrative_arc':
            $terms = get_the_terms($post_id, 'narrative_arc');
            if ($terms && !is_wp_error($terms)) {
                $term_links = array();
                foreach ($terms as $term) {
                    $term_links[] = $term->name;
                }
                echo implode(', ', $term_links);
            }
            break;
    }
}
add_action('manage_book_chapter_posts_custom_column', 'ca_populate_chapter_admin_columns', 10, 2);

// Make custom columns sortable
function ca_make_chapter_columns_sortable($columns) {
    $columns['chapter_status'] = 'chapter_status';
    $columns['narrative_arc'] = 'narrative_arc';
    return $columns;
}
add_filter('manage_edit-book_chapter_sortable_columns', 'ca_make_chapter_columns_sortable');

// Modify main query for chapter archives
function ca_modify_chapter_archive_query($query) {
    if (!is_admin() && $query->is_main_query() && is_post_type_archive('book_chapter')) {
        $query->set('posts_per_page', 12);
        $query->set('orderby', 'modified');
        $query->set('order', 'DESC');
    }
}
add_action('pre_get_posts', 'ca_modify_chapter_archive_query');

// Add chapter navigation to single chapter pages
function ca_chapter_navigation() {
    if (!is_singular('book_chapter')) {
        return;
    }
    
    $previous = get_previous_post();
    $next = get_next_post();
    
    if ($previous || $next) {
        echo '<nav class="chapter-navigation">';
        echo '<div class="nav-links">';
        
        if ($previous) {
            echo '<div class="nav-previous">';
            echo '<span>Previous Chapter</span>';
            echo '<a href="' . get_permalink($previous->ID) . '">' . get_the_title($previous->ID) . '</a>';
            echo '</div>';
        }
        
        if ($next) {
            echo '<div class="nav-next">';
            echo '<span>Next Chapter</span>';
            echo '<a href="' . get_permalink($next->ID) . '">' . get_the_title($next->ID) . '</a>';
            echo '</div>';
        }
        
        echo '</div>';
        echo '</nav>';
    }
}