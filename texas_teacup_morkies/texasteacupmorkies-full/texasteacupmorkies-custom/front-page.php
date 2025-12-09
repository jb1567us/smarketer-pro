<?php
get_header();

$available_id = ttp_get_available_puppy_id();
$lead_mode = ttp_get_option( 'lead_mode', 'referral' );
$price_anchor = ttp_get_option( 'price_anchor', '$2,000+' );

$phone = ttp_get_option( 'phone', '' );
$call_href = $phone ? ttp_format_phone_href( $phone ) : '';
$text_href = $phone ? ttp_format_sms_href( $phone ) : '';

$apply_page = absint( ttp_get_option( 'apply_page_id', 0 ) );
$ref_page = absint( ttp_get_option( 'referral_page_id', 0 ) );

$waitlist_url = $apply_page ? get_permalink( $apply_page ) : (string) ttp_get_option( 'waitlist_form_url', '' );
$referral_url = $ref_page ? get_permalink( $ref_page ) : (string) ttp_get_option( 'referral_form_url', '' );

$google_reviews_url = (string) ttp_get_option( 'google_reviews_url', '' );

function ttp_home_trust_bar() {
	?>
	<div class="ttp-trustbar" role="list">
		<div class="ttp-trustbar__item" role="listitem">🏠 <strong>Raised in-home</strong> in Austin</div>
		<div class="ttp-trustbar__item" role="listitem">🤝 <strong>Socialized</strong> with people & pets</div>
		<div class="ttp-trustbar__item" role="listitem">🧼 <strong>House training</strong> in progress</div>
		<div class="ttp-trustbar__item" role="listitem">🩺 Vet care + references available</div>
	</div>
	<?php
}
?>

<section class="ttp-hero">
	<div class="ttp-container ttp-hero__inner">
		<div class="ttp-hero__copy">
			<?php if ( $available_id ) : ?>
				<h1 class="ttp-hero__title">Puppy Available Now <span class="ttp-muted">(Austin, TX)</span></h1>
				<p class="ttp-hero__sub">In-home raised • Socialized with people & pets • House training in progress</p>
				<p class="ttp-hero__price">Starting at <strong><?php echo esc_html( $price_anchor ); ?></strong></p>

				<div class="ttp-hero__cta">
					<a class="ttp-btn ttp-btn--lg" href="<?php echo esc_url( ttp_get_apply_url_for_puppy( $available_id ) ); ?>">Apply for the Available Puppy</a>
					<?php if ( $text_href ) : ?><a class="ttp-btn ttp-btn--ghost ttp-btn--lg" href="<?php echo esc_url( $text_href ); ?>">Text</a><?php endif; ?>
					<?php if ( $call_href ) : ?><a class="ttp-btn ttp-btn--ghost ttp-btn--lg" href="<?php echo esc_url( $call_href ); ?>">Call</a><?php endif; ?>
				</div>

				<?php ttp_home_trust_bar(); ?>

			<?php else : ?>
				<h1 class="ttp-hero__title"><?php bloginfo( 'name' ); ?></h1>
				<p class="ttp-hero__sub">Small, in-home Austin breeder raising well-socialized puppies with early training started.</p>
				<p class="ttp-hero__price">Puppies starting at <strong><?php echo esc_html( $price_anchor ); ?></strong> • Pickup in Austin</p>

				<div class="ttp-hero__cta">
					<?php if ( 'waitlist' === $lead_mode && $waitlist_url ) : ?>
						<a class="ttp-btn ttp-btn--lg" href="<?php echo esc_url( $waitlist_url ); ?>">Join the Waitlist</a>
					<?php else : ?>
						<a class="ttp-btn ttp-btn--lg" href="<?php echo esc_url( $referral_url ? $referral_url : home_url('/contact/') ); ?>">Request a Referral</a>
					<?php endif; ?>
					<?php if ( $text_href ) : ?><a class="ttp-btn ttp-btn--ghost ttp-btn--lg" href="<?php echo esc_url( $text_href ); ?>">Text</a><?php endif; ?>
					<?php if ( $call_href ) : ?><a class="ttp-btn ttp-btn--ghost ttp-btn--lg" href="<?php echo esc_url( $call_href ); ?>">Call</a><?php endif; ?>
				</div>

				<?php ttp_home_trust_bar(); ?>
			<?php endif; ?>
		</div>

		<?php if ( $available_id ) : $meta = ttp_get_puppy_meta( $available_id ); ?>
			<aside class="ttp-featuredcard">
				<a class="ttp-featuredcard__img" href="<?php echo esc_url( get_permalink( $available_id ) ); ?>">
					<?php echo get_the_post_thumbnail( $available_id, 'ttp_puppy_card', array( 'loading' => 'eager' ) ); ?>
				</a>
				<div class="ttp-featuredcard__body">
					<div class="ttp-badge ttp-badge--<?php echo esc_attr( $meta['status'] ?: 'status' ); ?>"><?php echo esc_html( ttp_badge_label( $meta['status'] ?? '' ) ); ?> (1)</div>
					<h2 class="ttp-featuredcard__title"><a href="<?php echo esc_url( get_permalink( $available_id ) ); ?>"><?php echo esc_html( get_the_title( $available_id ) ); ?></a></h2>
					<div class="ttp-featuredcard__meta">
						<span><?php echo esc_html( $meta['breed'] ?: '' ); ?></span>
						<?php if ( ! empty( $meta['price'] ) ) : ?><span>• <?php echo esc_html( $meta['price'] ); ?></span><?php endif; ?>
					</div>
					<div class="ttp-featuredcard__facts">
						<?php if ( ! empty( $meta['dob'] ) ) : ?><div><span class="ttp-muted">DOB</span><br><?php echo esc_html( $meta['dob'] ); ?></div><?php endif; ?>
						<?php if ( ! empty( $meta['ready_date'] ) ) : ?><div><span class="ttp-muted">Ready</span><br><?php echo esc_html( $meta['ready_date'] ); ?></div><?php endif; ?>
						<?php if ( ! empty( $meta['est_weight'] ) ) : ?><div><span class="ttp-muted">Est. Adult</span><br><?php echo esc_html( $meta['est_weight'] ); ?></div><?php endif; ?>
					</div>
					<div class="ttp-featuredcard__actions">
						<a class="ttp-btn" href="<?php echo esc_url( ttp_get_apply_url_for_puppy( $available_id ) ); ?>">Apply</a>
						<a class="ttp-btn ttp-btn--ghost" href="<?php echo esc_url( get_permalink( $available_id ) ); ?>">View details</a>
					</div>
					<?php if ( $google_reviews_url ) : ?><div class="ttp-featuredcard__reviews"><a href="<?php echo esc_url( $google_reviews_url ); ?>" target="_blank" rel="noopener">See our Google reviews</a></div><?php endif; ?>
				</div>
			</aside>
		<?php endif; ?>
	</div>
</section>

<section class="ttp-section">
	<div class="ttp-container">
		<div class="ttp-section__grid">
			<div class="ttp-card">
				<h2 class="ttp-h2">How it works</h2>
				<ol class="ttp-steps">
					<li><strong>Apply</strong> using our short form.</li>
					<li><strong>Quick approval</strong> by call/text to confirm fit and timing.</li>
					<li><strong>Pickup in Austin</strong> at our home, with go-home info.</li>
				</ol>
				<p class="ttp-muted">A deposit is not required to join the waitlist. After approval, you may place a refundable deposit to hold a specific puppy.</p>
			</div>
			<div class="ttp-card">
				<h2 class="ttp-h2">Reviews & Happy Homes</h2>
				<p>Small breeder. Real photos. Real reviews.</p>
				<div class="ttp-row">
					<?php if ( $google_reviews_url ) : ?><a class="ttp-btn ttp-btn--ghost" href="<?php echo esc_url( $google_reviews_url ); ?>" target="_blank" rel="noopener">Google Reviews</a><?php endif; ?>
				</div>
			</div>
		</div>
	</div>
</section>

<?php if ( ! $available_id ) : ?>
<section class="ttp-section ttp-section--alt">
	<div class="ttp-container">
		<div class="ttp-card ttp-card--wide">
			<?php if ( 'waitlist' === $lead_mode ) : ?>
				<h2 class="ttp-h2">Waitlist is open</h2>
				<p>Join the waitlist to be notified first.</p>
				<?php if ( $waitlist_url ) : ?><a class="ttp-btn" href="<?php echo esc_url( $waitlist_url ); ?>">Join Waitlist</a><?php endif; ?>
			<?php else : ?>
				<h2 class="ttp-h2">Need a puppy sooner?</h2>
				<p>If we don’t have puppies available, request a referral and we’ll review your needs privately.</p>
				<?php if ( $referral_url ) : ?><a class="ttp-btn" href="<?php echo esc_url( $referral_url ); ?>">Request a Referral</a><?php endif; ?>
			<?php endif; ?>
		</div>
	</div>
</section>
<?php endif; ?>

<?php get_footer(); ?>
