<?php
get_header();
$featured_id = ttp_get_available_puppy_id();
$price_anchor = (string) ttp_get_option('price_anchor', '$2,000+');
?>
<section class="ttp-hero">
	<div class="ttp-container ttp-hero__inner">
		<div>
			<h1 class="ttp-hero__title">Boutique, family-raised puppies in Austin, TX</h1>
			<p class="ttp-hero__sub">We’re a small, warm, in-home breeder. Our focus is simple: healthy routines, calm socialization, and honest communication—so you know exactly what you’re getting.</p>

			<div class="ttp-trustbar" aria-label="Trust signals">
				<div class="ttp-trustbar__item">Raised in-home in Austin</div>
				<div class="ttp-trustbar__item">Socialized with people &amp; pets</div>
				<div class="ttp-trustbar__item">House training in progress</div>
				<div class="ttp-trustbar__item">Vet references available</div>
			</div>

			<div class="ttp-hero__cta">
				<?php echo do_shortcode('[ttp_lead_cta]'); ?>
				<a class="ttp-btn ttp-btn--ghost" href="<?php echo esc_url( get_post_type_archive_link('ttp_puppy') ); ?>">See all puppies</a>
			</div>

			<p class="ttp-muted" style="margin-top:12px;">Pricing is upfront (typically <strong><?php echo esc_html($price_anchor); ?></strong>) so we can focus on great fits.</p>
		</div>

		<div>
			<?php if ( $featured_id ) : ?>
				<?php
				$status = ttp_get_puppy_status( $featured_id );
				$price  = ttp_get_puppy_meta( $featured_id, '_ttp_price', '' );
				$sex    = ttp_get_puppy_meta( $featured_id, '_ttp_sex', '' );
				$color  = ttp_get_puppy_meta( $featured_id, '_ttp_color', '' );
				$gohome = ttp_get_puppy_meta( $featured_id, '_ttp_go_home_date', '' );
				?>
				<article class="ttp-featuredcard">
					<a class="ttp-featuredcard__img" href="<?php echo esc_url( get_permalink($featured_id) ); ?>">
						<?php if ( has_post_thumbnail( $featured_id ) ) : ?>
							<?php echo get_the_post_thumbnail( $featured_id, 'large' ); ?>
						<?php endif; ?>
					</a>
					<div class="ttp-featuredcard__body">
						<div class="ttp-row ttp-row--between">
							<?php echo ttp_badge_html( $status ); ?>
							<span class="ttp-muted">Austin pickup</span>
						</div>
						<h2 class="ttp-featuredcard__title"><a href="<?php echo esc_url( get_permalink($featured_id) ); ?>"><?php echo esc_html( get_the_title($featured_id) ); ?></a></h2>
						<div class="ttp-featuredcard__meta">
							<?php if ( $price ) : ?><span><strong>$<?php echo esc_html($price); ?></strong></span><?php endif; ?>
							<?php if ( $sex ) : ?><span>· <?php echo esc_html($sex); ?></span><?php endif; ?>
							<?php if ( $color ) : ?><span>· <?php echo esc_html($color); ?></span><?php endif; ?>
						</div>

						<div class="ttp-featuredcard__facts">
							<div><strong>Breed</strong><br><?php echo esc_html( wp_strip_all_tags( get_the_term_list($featured_id, 'ttp_breed', '', ', ') ) ); ?></div>
							<div><strong>Go-home</strong><br><?php echo $gohome ? esc_html( date_i18n( 'M j, Y', strtotime($gohome) ) ) : esc_html__('TBD', 'ttp'); ?></div>
							<div><strong>Next step</strong><br>Apply</div>
						</div>

						<div class="ttp-featuredcard__actions">
							<a class="ttp-btn" href="<?php echo esc_url( ttp_get_apply_url_for_puppy($featured_id) ); ?>">Apply</a>
							<a class="ttp-btn ttp-btn--ghost" href="<?php echo esc_url( get_permalink($featured_id) ); ?>">Details</a>
						</div>

						<div class="ttp-muted" style="margin-top:10px;font-size:14px;">This is the one we currently have available—so the site stays focused.</div>
					</div>
				</article>
			<?php else : ?>
				<div class="ttp-card ttp-card--wide">
					<h2 class="ttp-h2">Currently between litters</h2>
					<p class="ttp-muted">Most seasons we have one breed at a time. When we don’t have puppies available, use our referral request form—then we’ll decide who to connect you with privately.</p>
					<?php echo do_shortcode('[ttp_lead_cta]'); ?>
				</div>
			<?php endif; ?>
		</div>
	</div>
</section>

<section class="ttp-section ttp-section--alt">
	<div class="ttp-container" style="display:grid;grid-template-columns:1.1fr .9fr;gap:16px;">
		<div class="ttp-card">
			<h2 class="ttp-h2">What to expect</h2>
			<ul class="ttp-prose">
				<li><strong>Local pickup:</strong> typically at our home in Austin (78723).</li>
				<li><strong>Timing:</strong> pups stay with mom ~8 weeks before going home.</li>
				<li><strong>Deposit:</strong> not required for the waitlist; refundable deposits may be used to hold a puppy after approval.</li>
			</ul>
			<div class="ttp-row" style="margin-top:10px;">
				<a class="ttp-btn ttp-btn--ghost" href="/process/">Process / FAQ</a>
				<a class="ttp-btn ttp-btn--ghost" href="/contact/">Contact</a>
			</div>
		</div>

		<div class="ttp-card">
			<h2 class="ttp-h2">Breed pages (SEO + education)</h2>
			<p class="ttp-muted">Right now we’re breeding Maltipoms. We keep Morkie information available for future planning.</p>
			<div class="ttp-row" style="margin-top:10px;">
				<a class="ttp-btn ttp-btn--ghost" href="/maltipom/">Maltipom (Austin)</a>
				<a class="ttp-btn ttp-btn--ghost" href="/morkie/">Morkie (Info)</a>
			</div>
			<hr>
			<p class="ttp-muted" style="margin:0 0 10px;">Austin-metro pickup pages:</p>
			<div class="ttp-row">
				<a class="ttp-btn ttp-btn--ghost" href="/round-rock-puppies/">Round Rock</a>
				<a class="ttp-btn ttp-btn--ghost" href="/cedar-park-puppies/">Cedar Park</a>
				<a class="ttp-btn ttp-btn--ghost" href="/bastrop-puppies/">Bastrop</a>
				<a class="ttp-btn ttp-btn--ghost" href="/pflugerville-puppies/">Pflugerville</a>
				<a class="ttp-btn ttp-btn--ghost" href="/georgetown-puppies/">Georgetown</a>
			</div>
		</div>
	</div>
</section>

<section class="ttp-section">
	<div class="ttp-container">
		<div class="ttp-card">
			<h2 class="ttp-h2">Reviews &amp; happy homes</h2>
			<p class="ttp-muted">We’re small, so we keep social proof simple and real. See our Google reviews and photo gallery.</p>
			<div class="ttp-row" style="margin-top:10px;">
				<a class="ttp-btn ttp-btn--ghost" href="/reviews/">View reviews</a>
			</div>
		</div>
	</div>
</section>

<?php get_footer(); ?>
