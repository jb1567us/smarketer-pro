<?php get_header(); ?>
<div class="ttp-container ttp-section">
	<div class="ttp-card">
		<h1 class="ttp-h2"><?php single_post_title(); ?></h1>
		<div class="ttp-prose"><?php the_content(); ?></div>
	</div>
</div>
<?php get_footer(); ?>
