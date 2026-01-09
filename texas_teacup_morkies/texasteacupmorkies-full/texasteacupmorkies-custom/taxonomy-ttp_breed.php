<?php
get_header();

$term = get_queried_object();
$term_name = $term && ! is_wp_error( $term ) ? $term->name : '';
$desc = $term && ! is_wp_error( $term ) ? term_description( $term ) : '';

$lead_mode = ttp_get_option( 'lead_mode', 'referral' );
$apply_page = absint( ttp_get_option( 'apply_page_id', 0 ) );
$ref_page = absint( ttp_get_option( 'referral_page_id', 0 ) );

$waitlist_url = $apply_page ? get_permalink( $apply_page ) : (string) ttp_get_option( 'waitlist_form_url', '' );
$referral_url = $ref_page ? get_permalink( $ref_page ) : (string) ttp_get_option( 'referral_form_url', '' );

$q = new WP_Query( array(
	'post_type' => 'ttp_puppy',
	'posts_per_page' => 24,
	'orderby' => 'date',
	'order' => 'DESC',
	'tax_query' => array( array('taxonomy'=>'ttp_breed','field'=>'term_id','terms'=> $term ? $term->term_id : 0) ),
	'meta_query' => array( array('key'=>'_ttp_status','value'=>'available','compare'=>'=') ),
	'no_found_rows' => true,
) );
?>
<section class="ttp-section">
	<div class="ttp-container">
		<header class="ttp-pagehead">
			<h1 class="ttp-h1"><?php echo esc_html( $term_name ); ?> <span class="ttp-muted">Puppies in Austin, TX</span></h1>
			<p class="ttp-muted">Raised in-home • Socialized with people & pets • House training in progress</p>
			<?php if ( $desc ) : ?><div class="ttp-prose"><?php echo wp_kses_post( $desc ); ?></div><?php endif; ?>
		</header>

		<?php if ( $q->have_posts() ) : ?>
			<div class="ttp-gridcards">
				<?php while ( $q->have_posts() ) : $q->the_post(); $meta = ttp_get_puppy_meta( get_the_ID() ); ?>
					<article class="ttp-card ttp-card--puppy">
						<a class="ttp-card__img" href="<?php the_permalink(); ?>"><?php if ( has_post_thumbnail() ) { the_post_thumbnail( 'ttp_puppy_card' ); } ?></a>
						<div class="ttp-card__body">
							<div class="ttp-row ttp-row--between">
								<div class="ttp-badge ttp-badge--available">Available</div>
								<div class="ttp-muted"><?php echo esc_html( $meta['breed'] ?: '' ); ?></div>
							</div>
							<h2 class="ttp-h3"><a href="<?php the_permalink(); ?>"><?php the_title(); ?></a></h2>
							<div class="ttp-muted"><?php if ( ! empty( $meta['price'] ) ) : ?><?php echo esc_html( $meta['price'] ); ?><?php endif; ?><?php if ( ! empty( $meta['ready_date'] ) ) : ?> • Ready <?php echo esc_html( $meta['ready_date'] ); ?><?php endif; ?></div>
							<div class="ttp-row">
								<a class="ttp-btn ttp-btn--sm" href="<?php echo esc_url( ttp_get_apply_url_for_puppy( get_the_ID() ) ); ?>">Apply</a>
								<a class="ttp-btn ttp-btn--ghost ttp-btn--sm" href="<?php the_permalink(); ?>">Details</a>
							</div>
						</div>
					</article>
				<?php endwhile; wp_reset_postdata(); ?>
			</div>
		<?php else : ?>
			<div class="ttp-card ttp-card--wide">
				<h2 class="ttp-h2">No <?php echo esc_html( $term_name ); ?> puppies available right now</h2>
				<p>We typically have puppies once a year. When we’re ready to take leads, we open the waitlist.</p>
				<div class="ttp-row">
					<?php if ( 'waitlist' === $lead_mode && $waitlist_url ) : ?><a class="ttp-btn" href="<?php echo esc_url( $waitlist_url ); ?>">Join Waitlist</a><?php else : ?><a class="ttp-btn" href="<?php echo esc_url( $referral_url ? $referral_url : home_url('/contact/') ); ?>">Request a Referral</a><?php endif; ?>
				</div>
			</div>
		<?php endif; ?>
	</div>
</section>
<?php get_footer(); ?>
