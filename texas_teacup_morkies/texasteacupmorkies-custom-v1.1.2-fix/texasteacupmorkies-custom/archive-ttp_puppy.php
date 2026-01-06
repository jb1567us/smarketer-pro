<?php
get_header();
?>
<div class="ttp-container ttp-section">
	<header class="ttp-pagehead">
		<h1 class="ttp-h1">Available Puppies</h1>
		<p class="ttp-muted">We usually have one breed at a time. Statuses are shown as Available / Reserved / Sold.</p>
	</header>

	<?php if ( have_posts() ) : ?>
		<div class="ttp-gridcards">
			<?php while ( have_posts() ) : the_post();
				$status = ttp_get_puppy_status( get_the_ID() );
				$price  = ttp_get_puppy_meta( get_the_ID(), '_ttp_price', '' );
			?>
				<article class="ttp-card ttp-puppycard">
					<a class="ttp-card__img" href="<?php the_permalink(); ?>">
						<?php if ( has_post_thumbnail() ) { the_post_thumbnail('large'); } ?>
					</a>
					<div class="ttp-card__body">
						<div class="ttp-row ttp-row--between">
							<?php echo ttp_badge_html( $status ); ?>
							<?php if ( $price ) : ?><span><strong>$<?php echo esc_html($price); ?></strong></span><?php endif; ?>
						</div>
						<h2 class="ttp-h3"><a href="<?php the_permalink(); ?>"><?php the_title(); ?></a></h2>
						<p class="ttp-muted"><?php echo esc_html( ttp_excerpt_fallback( get_the_ID(), 'Click for details.' ) ); ?></p>
						<div class="ttp-row">
							<a class="ttp-btn ttp-btn--sm" href="<?php echo esc_url( ttp_get_apply_url_for_puppy(get_the_ID()) ); ?>">Apply</a>
							<a class="ttp-btn ttp-btn--ghost ttp-btn--sm" href="<?php the_permalink(); ?>">Details</a>
						</div>
					</div>
				</article>
			<?php endwhile; ?>
		</div>

		<div class="ttp-muted" style="margin-top:16px;"><?php the_posts_pagination(); ?></div>
	<?php else : ?>
		<div class="ttp-card">
			<h2 class="ttp-h2">No puppies listed right now</h2>
			<p class="ttp-muted">If we’re between litters, use referral request mode. If we’re close to the next litter, we’ll open the waitlist.</p>
			<?php echo do_shortcode('[ttp_lead_cta]'); ?>
		</div>
	<?php endif; ?>
</div>
<?php get_footer(); ?>
