<?php
get_header();
?>
<section class="ttp-section">
	<div class="ttp-container">
		<h1 class="ttp-h1"><?php bloginfo( 'name' ); ?></h1>
		<?php if ( have_posts() ) : ?>
			<div class="ttp-stack">
				<?php while ( have_posts() ) : the_post(); ?>
					<article class="ttp-card">
						<h2 class="ttp-h2"><a href="<?php the_permalink(); ?>"><?php the_title(); ?></a></h2>
						<div class="ttp-muted"><?php the_time( get_option( 'date_format' ) ); ?></div>
						<div class="ttp-prose"><?php the_excerpt(); ?></div>
					</article>
				<?php endwhile; ?>
			</div>
			<div class="ttp-pagination"><?php the_posts_pagination(); ?></div>
		<?php else : ?>
			<p><?php esc_html_e( 'No content found.', 'ttp' ); ?></p>
		<?php endif; ?>
	</div>
</section>
<?php
get_footer();
