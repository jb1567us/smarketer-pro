<?php
/**
 * Caviar Premium functions and definitions
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit; // Exit if accessed directly
}

function caviar_setup() {
    // Add default posts and comments RSS feed links to head.
    add_theme_support( 'automatic-feed-links' );

    // Let WordPress manage the document title.
    add_theme_support( 'title-tag' );

    // Enable support for Post Thumbnails on posts and pages.
    add_theme_support( 'post-thumbnails' );

    // Switch default core markup for search form, comment form, and comments to output valid HTML5.
    add_theme_support( 'html5', array(
        'search-form',
        'comment-form',
        'comment-list',
        'gallery',
        'caption',
    ) );

    // Register navigation menu
    register_nav_menus( array(
        'primary' => esc_html__( 'Primary Menu', 'caviar-premium' ),
    ) );
    
    // Check if pages have tags support, if not, add it.
    register_taxonomy_for_object_type('post_tag', 'page');
}
add_action( 'after_setup_theme', 'caviar_setup' );

/**
 * Enqueue scripts and styles.
 */
function caviar_scripts() {
    // Enqueue main stylesheet
    wp_enqueue_style( 'caviar-style', get_stylesheet_uri(), array(), '1.0.0' );

    // Enqueue script for navigation toggle (inline for simplicity or separate file)
    // We'll output a small inline script in footer for the hamburger toggle to avoid extra requests
}
add_action( 'wp_enqueue_scripts', 'caviar_scripts' );

/**
 * Make sure Pages show up in main loop if we want default archives to include them? 
 * Actually, for front-page.php custom query, we don't need this.
 */

/**
 * Helper to display tags as a clean list
 */
function caviar_get_tags_list($id) {
    $tags = get_the_tags($id);
    if ($tags) {
        $names = array();
        foreach ($tags as $tag) {
            $names[] = $tag->name;
        }
        return implode(', ', $names);
    }
    return '';
}

// Disable WordPress Native Lazy Loading to prevent placeholder issues
add_filter( 'wp_lazy_loading_enabled', '__return_false' );

// Force load ESM Collection Template (Deployment Fix)
$esm_template = WP_CONTENT_DIR . '/mu-plugins/esm-collection-template.php';
if (file_exists($esm_template)) {
    require_once $esm_template;
} else {
    $esm_template_fallback = ABSPATH . 'wp-content/mu-plugins/esm-collection-template.php';
    if (file_exists($esm_template_fallback)) {
        require_once $esm_template_fallback;
    }
}
?>
