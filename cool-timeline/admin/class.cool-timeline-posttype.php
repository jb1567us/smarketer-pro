<?php
class CoolTimelinePostType {
    
    public function __construct() {
        add_action( 'init', array( $this, 'register_timeline_post_type' ) );
    }
    
    public function register_timeline_post_type() {
        $labels = array(
            'name' => __( 'Timeline Stories', 'cool-timeline' ),
            'singular_name' => __( 'Timeline Story', 'cool-timeline' ),
        );
        
        $args = array(
            'labels' => $labels,
            'public' => true,
            'has_archive' => false,
            'menu_icon' => 'dashicons-clock',
            'supports' => array( 'title', 'editor', 'thumbnail' ),
            'show_in_rest' => true,
        );
        
        register_post_type( 'cool_timeline', $args );
    }
}

new CoolTimelinePostType();