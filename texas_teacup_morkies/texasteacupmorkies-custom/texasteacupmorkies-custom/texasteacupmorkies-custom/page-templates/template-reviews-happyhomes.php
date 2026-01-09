<?php
/*
Template Name: Reviews & Happy Homes
*/
get_header();

$google_reviews_url = (string) ttp_get_option( 'google_reviews_url', '' );
$q = new WP_Query( array(
	'post_type' => 'ttp_happy_home',
	'posts_per_page' => 48,
	'orderby' => 'date',
	'order' => 'DESC',
	'no_found_rows' => true,
) );
?>
<section class="ttp-section">
	<div class="ttp-container">
		<header class="ttp-pagehead">
			<h1 class="ttp-h1"><?php the_title(); ?></h1>
			<p class="ttp-muted">Real families, real photos. We’re a small in-home breeder—your trust matters.</p>
			<?php if ( $google_reviews_url ) : ?><p><a class="ttp-btn ttp-btn--ghost" href="<?php echo esc_url( $google_reviews_url ); ?>" target="_blank" rel="noopener">Read our Google Reviews</a></p><?php endif; ?>
		</header>

		<?php if ( $q->have_posts() ) : ?>
			<div class="ttp-gridphotos">
				<?php while ( $q->have_posts() ) : $q->the_post(); ?>
					<figure class="ttp-photo">
						<a href="<?php the_permalink(); ?>" class="ttp-photo__img"><?php if ( has_post_thumbnail() ) { the_post_thumbnail( 'ttp_happy_home' ); } ?></a>
						<figcaption class="ttp-photo__cap"><?php
							$client = get_post_meta( get_the_ID(), '_ttp_client_name', true );
							$loc = get_post_meta( get_the_ID(), '_ttp_client_location', true );
							$bits = array();
							if ( $client ) $bits[] = $client;
							if ( $loc ) $bits[] = $loc;
							echo esc_html( implode( ' • ', $bits ) );
						?></figcaption>
					</figure>
				<?php endwhile; wp_reset_postdata(); ?>
			</div>
		<?php else : ?>
			<div class="ttp-card"><h2 class="ttp-h2">Happy Homes coming soon</h2><p>Add client photos in WP Admin → Happy Homes.</p></div>
		<?php endif; ?>
	</div>
</section>
<?php get_footer(); ?>
