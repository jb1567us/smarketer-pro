<?php
class CTL_Shortcode {
    
    public function __construct() {
        add_shortcode( 'cool-timeline', array( $this, 'render_shortcode' ) );
    }
    
    public function render_shortcode( $atts ) {
        $atts = shortcode_atts( array(
            'layout' => 'vertical',
            'show_media' => 'true',
            'posts_per_page' => '10',
            'order' => 'DESC',
        ), $atts );
        
        $cool_timeline = CoolTimelineLite::get_instance();
        return $cool_timeline->ctl_render_timeline_block( $atts );
    }
}

new CTL_Shortcode();