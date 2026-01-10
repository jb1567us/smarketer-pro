<?php
class CoolTimelineMetaFields {
    
    public function __construct() {
        add_action( 'add_meta_boxes', array( $this, 'add_meta_boxes' ) );
        add_action( 'save_post', array( $this, 'save_meta_fields' ) );
    }
    
    public function add_meta_boxes() {
        add_meta_box(
            'ctl_story_meta',
            'Timeline Story Details',
            array( $this, 'render_meta_fields' ),
            'cool_timeline',
            'normal',
            'high'
        );
    }
    
    public function render_meta_fields( $post ) {
        wp_nonce_field( 'ctl_save_meta', 'ctl_meta_nonce' );
        
        $story_date = get_post_meta( $post->ID, 'ctl_story_date', true );
        ?>
        <div class="ctl-meta-field">
            <label for="ctl_story_date">Story Date:</label>
            <input type="date" id="ctl_story_date" name="ctl_story_date" value="<?php echo esc_attr( $story_date ); ?>" />
            <p class="description">The date for this timeline story</p>
        </div>
        <?php
    }
    
    public function save_meta_fields( $post_id ) {
        if ( ! isset( $_POST['ctl_meta_nonce'] ) || ! wp_verify_nonce( $_POST['ctl_meta_nonce'], 'ctl_save_meta' ) ) {
            return;
        }
        
        if ( defined( 'DOING_AUTOSAVE' ) && DOING_AUTOSAVE ) {
            return;
        }
        
        if ( 'cool_timeline' !== get_post_type( $post_id ) ) {
            return;
        }
        
        if ( isset( $_POST['ctl_story_date'] ) ) {
            update_post_meta( $post_id, 'ctl_story_date', sanitize_text_field( $_POST['ctl_story_date'] ) );
        }
    }
}

new CoolTimelineMetaFields();