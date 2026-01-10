<?php
get_header();

$show = sanitize_text_field( $_GET['status'] ?? 'available' );
$valid = array( 'available', 'reserved', 'sold', 'all' );
if ( ! in_array( $show, $valid, true ) ) { $show = 'available'; }

$args = array(
	'post_type' => 'ttp_puppy',
	'posts_per_page' => 24,
	'orderby' => 'date',
	'order' => 'DESC',
);
if ( 'all' !== $show ) {
	$args['meta_query'] = array(
		array( 'key' => '_ttp_status', 'value' => $show, 'compare' => '=' ),
	);
}
$q = new WP_Query( $args );
?>
<section class="ttp-section">
	<div class="ttp-container">
		<header class="ttp-pagehead">
			<h1 class="ttp-h1">Available Puppies</h1>
			<p class="ttp-muted">Limited availability—check back or join the waitlist for updates.</p>
		</header>

		<div class="ttp-filters">
			<?php
			$tabs = array('available'=>'Available','reserved'=>'Reserved','sold'=>'Sold','all'=>'All');
			foreach ( $tabs as $k => $label ) {
				$url = add_query_arg( array( 'status' => $k ), get_post_type_archive_link( 'ttp_puppy' ) );
				$active = ( $show === $k );
				printf('<a class="ttp-pill %s" href="%s" aria-current="%s">%s</a>', $active?'is-active':'', esc_url($url), $active?'page':'false', esc_html($label));
			}
			?>
		</div>

		<?php if ( $q->have_posts() ) : ?>
			<div class="ttp-gridcards">
				<?php while ( $q->have_posts() ) : $q->the_post(); $meta = ttp_get_puppy_meta( get_the_ID() ); ?>
					<article class="ttp-card ttp-card--puppy">
						<a class="ttp-card__img" href="<?php the_permalink(); ?>"><?php if ( has_post_thumbnail() ) { the_post_thumbnail( 'ttp_puppy_card' ); } ?></a>
						<div class="ttp-card__body">
							<div class="ttp-row ttp-row--between">
								<div class="ttp-badge ttp-badge--<?php echo esc_attr( $meta['status'] ?: 'status' ); ?>"><?php echo esc_html( ttp_badge_label( $meta['status'] ?? '' ) ); ?></div>
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
			<div class="ttp-card"><h2 class="ttp-h2">No puppies listed for this status.</h2></div>
		<?php endif; ?>
	</div>
</section>
<?php get_footer(); ?>
