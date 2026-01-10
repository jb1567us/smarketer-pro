<?php
if ( ! defined( 'ABSPATH' ) ) { exit; }

function ttp_add_meta_boxes() {
	add_meta_box( 'ttp_puppy_details', __( 'Puppy Details', 'ttp' ), 'ttp_render_puppy_details_metabox', 'ttp_puppy', 'normal', 'high' );
	add_meta_box( 'ttp_happy_home_details', __( 'Happy Home Details', 'ttp' ), 'ttp_render_happy_home_details_metabox', 'ttp_happy_home', 'side', 'default' );
}
add_action( 'add_meta_boxes', 'ttp_add_meta_boxes' );

function ttp_render_puppy_details_metabox( $post ) {
	wp_nonce_field( 'ttp_save_puppy', 'ttp_puppy_nonce' );
	$status = get_post_meta( $post->ID, '_ttp_status', true );
	$price = get_post_meta( $post->ID, '_ttp_price', true );
	$dob = get_post_meta( $post->ID, '_ttp_dob', true );
	$ready = get_post_meta( $post->ID, '_ttp_ready_date', true );
	$weight = get_post_meta( $post->ID, '_ttp_est_weight', true );
	$gender = get_post_meta( $post->ID, '_ttp_gender', true );
	$color = get_post_meta( $post->ID, '_ttp_color_coat', true );
	$video = get_post_meta( $post->ID, '_ttp_video_url', true );
	$temperament = get_post_meta( $post->ID, '_ttp_temperament', true );
	$training = get_post_meta( $post->ID, '_ttp_training', true );
	?>
	<style>
		.ttp-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px}
		.ttp-grid label{display:block;font-weight:600;margin:0 0 4px}
		.ttp-grid input,.ttp-grid select,.ttp-grid textarea{width:100%}
		.ttp-help{color:#555;margin-top:6px}
		@media (max-width: 900px){.ttp-grid{grid-template-columns:1fr}}
	</style>

	<div class="ttp-grid">
		<div>
			<label for="ttp_status"><?php esc_html_e( 'Status', 'ttp' ); ?></label>
			<select id="ttp_status" name="ttp_status">
				<?php
				$opts = array('available' => 'Available', 'reserved' => 'Reserved', 'sold' => 'Sold');
				foreach ( $opts as $k => $label ) {
					printf('<option value="%s"%s>%s</option>', esc_attr($k), selected($status,$k,false), esc_html($label));
				}
				?>
			</select>
			<p class="ttp-help"><?php esc_html_e( 'Homepage will automatically feature a puppy marked Available.', 'ttp' ); ?></p>
		</div>

		<div>
			<label for="ttp_price"><?php esc_html_e( 'Price (e.g., 2500 or $2,500)', 'ttp' ); ?></label>
			<input id="ttp_price" name="ttp_price" type="text" value="<?php echo esc_attr( $price ); ?>" />
		</div>

		<div>
			<label for="ttp_dob"><?php esc_html_e( 'Date of Birth', 'ttp' ); ?></label>
			<input id="ttp_dob" name="ttp_dob" type="date" value="<?php echo esc_attr( $dob ); ?>" />
		</div>

		<div>
			<label for="ttp_ready_date"><?php esc_html_e( 'Ready / Go-Home Date', 'ttp' ); ?></label>
			<input id="ttp_ready_date" name="ttp_ready_date" type="date" value="<?php echo esc_attr( $ready ); ?>" />
		</div>

		<div>
			<label for="ttp_est_weight"><?php esc_html_e( 'Estimated Adult Weight (e.g., 6–8 lbs)', 'ttp' ); ?></label>
			<input id="ttp_est_weight" name="ttp_est_weight" type="text" value="<?php echo esc_attr( $weight ); ?>" />
		</div>

		<div>
			<label for="ttp_gender"><?php esc_html_e( 'Gender', 'ttp' ); ?></label>
			<input id="ttp_gender" name="ttp_gender" type="text" value="<?php echo esc_attr( $gender ); ?>" />
		</div>

		<div>
			<label for="ttp_color_coat"><?php esc_html_e( 'Color / Coat', 'ttp' ); ?></label>
			<input id="ttp_color_coat" name="ttp_color_coat" type="text" value="<?php echo esc_attr( $color ); ?>" />
		</div>

		<div>
			<label for="ttp_video_url"><?php esc_html_e( 'Video URL (optional)', 'ttp' ); ?></label>
			<input id="ttp_video_url" name="ttp_video_url" type="url" value="<?php echo esc_attr( $video ); ?>" placeholder="https://..." />
		</div>

		<div style="grid-column: 1 / -1;">
			<label for="ttp_temperament"><?php esc_html_e( 'Temperament (one bullet per line)', 'ttp' ); ?></label>
			<textarea id="ttp_temperament" name="ttp_temperament" rows="4"><?php echo esc_textarea( $temperament ); ?></textarea>
		</div>

		<div style="grid-column: 1 / -1;">
			<label for="ttp_training"><?php esc_html_e( 'Training & Socialization (one bullet per line)', 'ttp' ); ?></label>
			<textarea id="ttp_training" name="ttp_training" rows="4"><?php echo esc_textarea( $training ); ?></textarea>
		</div>
	</div>
	<?php
}

function ttp_render_happy_home_details_metabox( $post ) {
	wp_nonce_field( 'ttp_save_happy_home', 'ttp_happy_home_nonce' );
	$client = get_post_meta( $post->ID, '_ttp_client_name', true );
	$location = get_post_meta( $post->ID, '_ttp_client_location', true );
	$year = get_post_meta( $post->ID, '_ttp_year', true );
	?>
	<p>
		<label for="ttp_client_name" style="font-weight:600;display:block;margin-bottom:4px;"><?php esc_html_e( 'Client First Name (optional)', 'ttp' ); ?></label>
		<input id="ttp_client_name" name="ttp_client_name" type="text" value="<?php echo esc_attr( $client ); ?>" style="width:100%;" />
	</p>
	<p>
		<label for="ttp_client_location" style="font-weight:600;display:block;margin-bottom:4px;"><?php esc_html_e( 'City, State (optional)', 'ttp' ); ?></label>
		<input id="ttp_client_location" name="ttp_client_location" type="text" value="<?php echo esc_attr( $location ); ?>" style="width:100%;" />
	</p>
	<p>
		<label for="ttp_year" style="font-weight:600;display:block;margin-bottom:4px;"><?php esc_html_e( 'Year (optional)', 'ttp' ); ?></label>
		<input id="ttp_year" name="ttp_year" type="number" min="2000" max="2100" value="<?php echo esc_attr( $year ); ?>" style="width:100%;" />
	</p>
	<p style="color:#555;"><?php esc_html_e( 'Use the Featured Image for the photo. Use the editor content for a short caption (optional).', 'ttp' ); ?></p>
	<?php
}

function ttp_save_meta_boxes( $post_id ) {
	if ( defined( 'DOING_AUTOSAVE' ) && DOING_AUTOSAVE ) return;

	if ( 'ttp_puppy' === get_post_type( $post_id ) ) {
		if ( ! isset( $_POST['ttp_puppy_nonce'] ) || ! wp_verify_nonce( $_POST['ttp_puppy_nonce'], 'ttp_save_puppy' ) ) return;
		if ( ! current_user_can( 'edit_post', $post_id ) ) return;

		update_post_meta( $post_id, '_ttp_status', sanitize_text_field( $_POST['ttp_status'] ?? '' ) );
		update_post_meta( $post_id, '_ttp_price', sanitize_text_field( $_POST['ttp_price'] ?? '' ) );
		update_post_meta( $post_id, '_ttp_dob', sanitize_text_field( $_POST['ttp_dob'] ?? '' ) );
		update_post_meta( $post_id, '_ttp_ready_date', sanitize_text_field( $_POST['ttp_ready_date'] ?? '' ) );
		update_post_meta( $post_id, '_ttp_est_weight', sanitize_text_field( $_POST['ttp_est_weight'] ?? '' ) );
		update_post_meta( $post_id, '_ttp_gender', sanitize_text_field( $_POST['ttp_gender'] ?? '' ) );
		update_post_meta( $post_id, '_ttp_color_coat', sanitize_text_field( $_POST['ttp_color_coat'] ?? '' ) );
		update_post_meta( $post_id, '_ttp_video_url', esc_url_raw( $_POST['ttp_video_url'] ?? '' ) );
		update_post_meta( $post_id, '_ttp_temperament', sanitize_textarea_field( $_POST['ttp_temperament'] ?? '' ) );
		update_post_meta( $post_id, '_ttp_training', sanitize_textarea_field( $_POST['ttp_training'] ?? '' ) );
	}

	if ( 'ttp_happy_home' === get_post_type( $post_id ) ) {
		if ( ! isset( $_POST['ttp_happy_home_nonce'] ) || ! wp_verify_nonce( $_POST['ttp_happy_home_nonce'], 'ttp_save_happy_home' ) ) return;
		if ( ! current_user_can( 'edit_post', $post_id ) ) return;

		update_post_meta( $post_id, '_ttp_client_name', sanitize_text_field( $_POST['ttp_client_name'] ?? '' ) );
		update_post_meta( $post_id, '_ttp_client_location', sanitize_text_field( $_POST['ttp_client_location'] ?? '' ) );
		update_post_meta( $post_id, '_ttp_year', sanitize_text_field( $_POST['ttp_year'] ?? '' ) );
	}
}
add_action( 'save_post', 'ttp_save_meta_boxes' );
