<?php
class CTL_Helpers {
    
    public static function generate_timestamp( $date_string ) {
        return strtotime( $date_string );
    }
    
    public static function get_image_sizes() {
        return array(
            'thumbnail' => 'Thumbnail',
            'medium' => 'Medium',
            'large' => 'Large',
            'full' => 'Full Size',
        );
    }
}