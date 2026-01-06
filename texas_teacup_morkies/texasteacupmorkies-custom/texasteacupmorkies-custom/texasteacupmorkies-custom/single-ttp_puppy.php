<?php
get_header();
the_post();
$meta = ttp_get_puppy_meta( get_the_ID() );
$price_anchor = ttp_get_option( 'price_anchor', '$2,000+' );
$phone = ttp_get_option( 'phone', '' );
$call_href = $phone ? ttp_format_phone_href( $phone ) : '';
$text_href = $phone ? ttp_format_sms_href( $phone ) : '';
?>
<section class="ttp-section">
	<div class="ttp-container">
		<div class="ttp-product">
			<div class="ttp-product__media">
				<?php if ( has_post_thumbnail() ) : ?><div class="ttp-product__image"><?php the_post_thumbnail( 'large' ); ?></div><?php endif; ?>
				<?php if ( ! empty( $meta['video_url'] ) ) : ?><div class="ttp-embed"><iframe title="Puppy video" src="<?php echo esc_url( $meta['video_url'] ); ?>" loading="lazy" allowfullscreen></iframe></div><?php endif; ?>
				<div class="ttp-prose"><?php the_content(); ?></div>
			</div>

			<div class="ttp-product__sidebar">
				<div class="ttp-badge ttp-badge--<?php echo esc_attr( $meta['status'] ?: 'status' ); ?>"><?php echo esc_html( ttp_badge_label( $meta['status'] ?? '' ) ); ?></div>
				<h1 class="ttp-h1"><?php the_title(); ?></h1>
				<p class="ttp-muted"><?php echo esc_html( $meta['breed'] ?: '' ); ?></p>
				<div class="ttp-product__price"><?php echo esc_html( $meta['price'] ?: ( 'Starting at ' . $price_anchor ) ); ?></div>

				<div class="ttp-facts">
					<?php if ( ! empty( $meta['dob'] ) ) : ?><div><span class="ttp-muted">DOB</span><br><?php echo esc_html( $meta['dob'] ); ?></div><?php endif; ?>
					<?php if ( ! empty( $meta['ready_date'] ) ) : ?><div><span class="ttp-muted">Ready</span><br><?php echo esc_html( $meta['ready_date'] ); ?></div><?php endif; ?>
					<?php if ( ! empty( $meta['est_weight'] ) ) : ?><div><span class="ttp-muted">Est. Adult</span><br><?php echo esc_html( $meta['est_weight'] ); ?></div><?php endif; ?>
					<?php if ( ! empty( $meta['gender'] ) ) : ?><div><span class="ttp-muted">Gender</span><br><?php echo esc_html( $meta['gender'] ); ?></div><?php endif; ?>
				</div>

				<div class="ttp-stack">
					<a class="ttp-btn ttp-btn--lg" href="<?php echo esc_url( ttp_get_apply_url_for_puppy( get_the_ID() ) ); ?>">Apply</a>
					<div class="ttp-row"><?php if ( $text_href ) : ?><a class="ttp-btn ttp-btn--ghost" href="<?php echo esc_url( $text_href ); ?>">Text</a><?php endif; ?><?php if ( $call_href ) : ?><a class="ttp-btn ttp-btn--ghost" href="<?php echo esc_url( $call_href ); ?>">Call</a><?php endif; ?></div>
				</div>

				<hr class="ttp-divider" />

				<h2 class="ttp-h3">Training & Socialization</h2>
				<ul class="ttp-bullets">
					<?php
					$training = ttp_escape_multiline_bullets( $meta['training'] ?? '' );
					if ( empty( $training ) ) $training = array('Raised in-home in Austin','Socialized with people & pets','House training in progress');
					foreach ( $training as $line ) echo '<li>' . esc_html( $line ) . '</li>';
					?>
				</ul>

				<?php $temps = ttp_escape_multiline_bullets( $meta['temperament'] ?? '' ); if ( ! empty( $temps ) ) : ?>
					<h2 class="ttp-h3">Temperament</h2>
					<ul class="ttp-bullets"><?php foreach ( $temps as $line ) echo '<li>' . esc_html( $line ) . '</li>'; ?></ul>
				<?php endif; ?>

				<h2 class="ttp-h3">How placement works</h2>
				<ol class="ttp-steps"><li><strong>Apply</strong> using our short form.</li><li><strong>Approve</strong> by call/text.</li><li><strong>Pickup</strong> at our home in Austin.</li></ol>
				<p class="ttp-muted">Deposit is not required to join the waitlist. After approval, you may place a refundable deposit to hold a specific puppy.</p>
			</div>
		</div>
	</div>
</section>
<?php get_footer(); ?>
