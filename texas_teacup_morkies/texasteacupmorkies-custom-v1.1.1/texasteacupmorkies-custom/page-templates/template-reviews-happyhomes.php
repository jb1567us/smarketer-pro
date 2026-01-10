<?php
/*
Template Name: Reviews & Happy Homes
*/
get_header();
$reviews_url = (string) ttp_get_option('google_reviews_url', '' );
?>
<div class="ttp-container ttp-section">
	<header class="ttp-pagehead">
		<h1 class="ttp-h1"><?php the_title(); ?></h1>
		<p class="ttp-muted">Real reviews and real photos. Keep this page simple and authentic.</p>
	</header>

	<?php while ( have_posts() ) : the_post(); ?>
		<div class="ttp-card ttp-card--wide">
			<div class="ttp-prose"><?php the_content(); ?></div>
			<?php if ( $reviews_url ) : ?>
				<hr>
				<p><a class="ttp-btn ttp-btn--ghost" href="<?php echo esc_url($reviews_url); ?>" target="_blank" rel="noopener">Read our Google reviews</a></p>
			<?php else : ?>
				<p class="ttp-muted">Add your Google reviews link in <strong>Appearance → TTP Settings</strong>.</p>
			<?php endif; ?>
		</div>
	<?php endwhile; ?>
</div>
<?php get_footer(); ?>
