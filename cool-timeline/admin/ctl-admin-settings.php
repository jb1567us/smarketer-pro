<?php
class CoolTimelineSettings {
    
    public function __construct() {
        add_action( 'admin_menu', array( $this, 'add_settings_page' ) );
    }
    
    public function add_settings_page() {
        add_options_page(
            'Cool Timeline Settings',
            'Cool Timeline',
            'manage_options',
            'cool_timeline_settings',
            array( $this, 'render_settings_page' )
        );
    }
    
    public function render_settings_page() {
        ?>
        <div class="wrap">
            <h1>Cool Timeline Settings</h1>
            <p>Configure your timeline settings here.</p>
        </div>
        <?php
    }
}

new CoolTimelineSettings();