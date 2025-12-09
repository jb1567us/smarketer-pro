<?php
get_header();
the_post();
?>
<section class="ttp-section">
	<div class="ttp-container">
		<article class="ttp-card ttp-card--wide">
			<h1 class="ttp-h1"><?php the_title(); ?></h1>
			<div class="ttp-prose"><?php the_content(); ?></div>
		</article>
	</div>
</section>
<?php
get_footer();
