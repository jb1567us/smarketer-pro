<?php
get_header();
while ( have_posts() ) : the_post();
	$status = ttp_get_puppy_status( get_the_ID() );
	$price  = ttp_get_puppy_meta( get_the_ID(), '_ttp_price', '' );
	$sex    = ttp_get_puppy_meta( get_the_ID(), '_ttp_sex', '' );
	$color  = ttp_get_puppy_meta( get_the_ID(), '_ttp_color', '' );
	$gohome = ttp_get_puppy_meta( get_the_ID(), '_ttp_go_home_date', '' );
?>
<div class="ttp-container ttp-section">
	<header class="ttp-pagehead">
		<div class="ttp-row ttp-row--between">
			<?php echo ttp_badge_html( $status ); ?>
			<a class="ttp-muted" href="<?php echo esc_url( get_post_type_archive_link('ttp_puppy') ); ?>">← Back to puppies</a>
		</div>
		<h1 class="ttp-h1"><?php the_title(); ?></h1>
	</header>

	<div class="ttp-product">
		<div class="ttp-product__media">
			<?php if ( has_post_thumbnail() ) { the_post_thumbnail('large'); } ?>
			<div class="ttp-card" style="margin-top:14px;">
				<h2 class="ttp-h2">About this puppy</h2>
				<div class="ttp-prose"><?php the_content(); ?></div>
			</div>
		</div>

		<aside class="ttp-product__sidebar">
			<div class="ttp-card ttp-card--wide">
				<div class="ttp-row ttp-row--between">
					<span class="ttp-muted">Austin pickup</span>
					<?php echo ttp_badge_html( $status ); ?>
				</div>

				<div class="ttp-product__price">
					<?php if ( $price ) : ?>$<?php echo esc_html($price); ?><?php else : ?><?php echo esc_html( ttp_get_option('price_anchor', '$2,000+') ); ?><?php endif; ?>
				</div>

				<div class="ttp-facts">
					<div><strong>Breed</strong><br><?php echo esc_html( wp_strip_all_tags( get_the_term_list(get_the_ID(), 'ttp_breed', '', ', ') ) ); ?></div>
					<div><strong>Go-home</strong><br><?php echo $gohome ? esc_html( date_i18n('M j, Y', strtotime($gohome)) ) : esc_html__('TBD','ttp'); ?></div>
					<div><strong>Sex</strong><br><?php echo $sex ? esc_html($sex) : esc_html__('—','ttp'); ?></div>
					<div><strong>Color</strong><br><?php echo $color ? esc_html($color) : esc_html__('—','ttp'); ?></div>
				</div>

				<div class="ttp-row">
					<a class="ttp-btn ttp-btn--lg" href="<?php echo esc_url( ttp_get_apply_url_for_puppy(get_the_ID()) ); ?>">Apply</a>
					<a class="ttp-btn ttp-btn--ghost ttp-btn--lg" href="/process/">Process / FAQ</a>
				</div>

				<hr>

				<p class="ttp-muted" style="margin:0;">Raised in-home in Austin · Socialized with people & pets · House training in progress</p>
			</div>
		</aside>
	</div>
</div>
<?php endwhile; get_footer(); ?>
