<?php get_header(); ?>
<div class="ttp-container ttp-section">
	<?php while ( have_posts() ) : the_post(); ?>
		<header class="ttp-pagehead">
			<h1 class="ttp-h1"><?php the_title(); ?></h1>
		</header>
		<div class="ttp-card ttp-card--wide">
			<div class="ttp-prose"><?php the_content(); ?></div>
		</div>
	<?php endwhile; ?>
</div>
<?php get_footer(); ?>
